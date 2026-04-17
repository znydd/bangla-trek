import uuid
from datetime import date
from typing import List, Optional, Set, Tuple

from sqlalchemy import and_, func, or_, select
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Session, selectinload

from app.models.buddy_match import BuddyMatch
from app.models.group_trip import GroupTrip, GroupTripMember
from app.models.itinerary import Itinerary
from app.models.user import User
from app.models.user_location import UserLocation
from app.schemas.buddy_match import BuddyDiscoveryFilters, BuddyMatchSuggestion


class BuddyMatchingService:
    """Service for finding and managing buddy matches based on interests and destinations."""

    def __init__(self, db: Session):
        self.db = db

    def _calculate_interest_overlap(
        self, interests1: List[str], interests2: List[str]
    ) -> Tuple[float, List[str]]:
        """Calculate interest overlap score and return common interests."""
        if not interests1 or not interests2:
            return 0.0, []

        set1 = set(i.lower() for i in interests1)
        set2 = set(i.lower() for i in interests2)

        common = set1 & set2
        if not common:
            return 0.0, []

        # Jaccard similarity: |A ∩ B| / |A ∪ B|
        union = set1 | set2
        score = len(common) / len(union) if union else 0.0

        return score, list(common)

    def _calculate_match_score(
        self,
        interest_overlap: float,
        destination_overlap: bool,
        has_location_proximity: bool = False,
        has_date_overlap: bool = False,
    ) -> float:
        """Calculate overall match score from 0.0 to 1.0."""
        # Weights for different factors
        interest_weight = 0.4
        destination_weight = 0.25
        date_overlap_weight = 0.15
        location_weight = 0.2

        score = interest_overlap * interest_weight

        if destination_overlap:
            score += destination_weight

        if has_date_overlap:
            score += date_overlap_weight

        if has_location_proximity:
            score += location_weight

        return min(score, 1.0)

    def discover_buddies(
        self,
        user_id: uuid.UUID,
        filters: Optional[BuddyDiscoveryFilters] = None,
    ) -> List[BuddyMatchSuggestion]:
        """
        Discover potential buddy matches based on:
        1. Overlapping interests from itineraries
        2. Overlapping destinations from itineraries and group trips
        3. Location proximity (optional)
        """
        filters = filters or BuddyDiscoveryFilters()

        # Get current user's data
        user_interests = self._get_user_interests(user_id)
        user_destinations = self._get_user_destinations(user_id)
        user_location = self._get_user_location(user_id)
        user_trip_dates = self._get_user_trip_date_ranges(user_id)

        # Find potential matches from itineraries
        itinerary_matches = self._find_matches_from_itineraries(
            user_id, user_interests, user_destinations, user_trip_dates, filters
        )

        # Find potential matches from group trips
        trip_matches = self._find_matches_from_group_trips(
            user_id, user_interests, user_destinations, user_trip_dates, filters
        )

        # Combine and deduplicate matches
        all_matches = self._merge_matches(itinerary_matches + trip_matches)

        # Sort by match score (descending)
        all_matches.sort(key=lambda m: m.match_score, reverse=True)

        # Filter by minimum score
        all_matches = [m for m in all_matches if m.match_score >= filters.min_match_score]

        # Limit results
        return all_matches[: filters.limit]

    def _get_user_interests(self, user_id: uuid.UUID) -> Set[str]:
        """Get all unique interests from user's itineraries."""
        interests = (
            self.db.execute(
                select(Itinerary.interests).where(Itinerary.user_id == user_id)
            )
            .scalars()
            .all()
        )

        # Flatten and deduplicate
        all_interests = set()
        for interest_list in interests:
            if interest_list:
                all_interests.update(i.lower() for i in interest_list)

        return all_interests

    def _get_user_destinations(self, user_id: uuid.UUID) -> Set[str]:
        """Get all unique destinations from user's itineraries and group trips."""
        destinations: Set[str] = set()

        # From itineraries
        itinerary_dests = (
            self.db.execute(
                select(Itinerary.destination)
                .where(Itinerary.user_id == user_id)
                .distinct()
            )
            .scalars()
            .all()
        )
        destinations.update(d.lower() for d in itinerary_dests if d)

        # From group trips
        trip_dests = (
            self.db.execute(
                select(GroupTrip.destination)
                .join(GroupTripMember, GroupTrip.id == GroupTripMember.trip_id)
                .where(GroupTripMember.user_id == user_id)
                .distinct()
            )
            .scalars()
            .all()
        )
        destinations.update(d.lower() for d in trip_dests if d)

        return destinations

    def _get_user_trip_date_ranges(
        self, user_id: uuid.UUID
    ) -> dict[str, list[tuple[date, date]]]:
        """
        Get date ranges for each destination from user's group trips.
        Returns: {destination: [(start_date, end_date), ...]}
        """
        trip_dates: dict[str, list[tuple[date, date]]] = {}

        trips = (
            self.db.execute(
                select(GroupTrip.destination, GroupTrip.start_date, GroupTrip.end_date)
                .join(GroupTripMember, GroupTrip.id == GroupTripMember.trip_id)
                .where(GroupTripMember.user_id == user_id)
            )
            .all()
        )

        for dest, start, end in trips:
            if dest and start and end:
                dest_lower = dest.lower()
                if dest_lower not in trip_dates:
                    trip_dates[dest_lower] = []
                trip_dates[dest_lower].append((start, end))

        return trip_dates

    def _check_date_overlap(
        self,
        user_dates: dict[str, list[tuple[date, date]]],
        other_dest: str,
        other_start: date,
        other_end: date,
    ) -> bool:
        """Check if other user's trip dates overlap with current user's dates at same destination."""
        dest_lower = other_dest.lower()

        if dest_lower not in user_dates:
            return False

        user_ranges = user_dates[dest_lower]

        for user_start, user_end in user_ranges:
            # Check if date ranges overlap
            # Two ranges overlap if: start1 <= end2 AND start2 <= end1
            if user_start <= other_end and other_start <= user_end:
                return True

        return False

    def _get_user_location(self, user_id: uuid.UUID) -> Optional[UserLocation]:
        """Get user's current location if available."""
        return (
            self.db.execute(
                select(UserLocation).where(UserLocation.user_id == user_id)
            )
            .scalar_one_or_none()
        )

    def _find_matches_from_itineraries(
        self,
        user_id: uuid.UUID,
        user_interests: Set[str],
        user_destinations: Set[str],
        user_trip_dates: dict[str, list[tuple[date, date]]],
        filters: BuddyDiscoveryFilters,
    ) -> List[BuddyMatchSuggestion]:
        """Find potential buddies from overlapping itineraries."""
        matches = []

        # Base query: other users with itineraries
        query = (
            select(Itinerary.user_id, Itinerary.interests, Itinerary.destination)
            .where(Itinerary.user_id != user_id)
            .distinct()
        )

        # Filter by destination if specified
        if filters.destination:
            query = query.where(
                Itinerary.destination.ilike(f"%{filters.destination}%")
            )

        # Filter by interest if specified
        if filters.interest:
            query = query.where(
                Itinerary.interests.any(filters.interest)
            )

        results = self.db.execute(query).all()

        # Get user info for matches
        user_ids = [r[0] for r in results]
        if not user_ids:
            return []

        users = (
            self.db.execute(select(User).where(User.id.in_(user_ids)))
            .scalars()
            .all()
        )
        user_map = {u.id: u for u in users}

        # Process results
        for other_user_id, interests, destination in results:
            if other_user_id not in user_map:
                continue

            other_user = user_map[other_user_id]

            # Calculate interest overlap
            other_interests = set(i.lower() for i in interests) if interests else set()
            interest_score, common_interests = self._calculate_interest_overlap(
                list(user_interests), list(other_interests)
            )

            # Check destination overlap
            dest_lower = destination.lower() if destination else ""
            dest_overlap = dest_lower in user_destinations
            common_dests = [destination] if dest_overlap else []

            # Check date overlap for group trips at this destination
            date_overlap = False
            if dest_overlap and dest_lower in user_trip_dates:
                # For itineraries without dates, we can't check exact overlap
                # But we note they share the destination
                date_overlap = True  # Assume potential overlap if same destination

            # Calculate overall score with date overlap bonus
            score = self._calculate_match_score(
                interest_score, dest_overlap, has_date_overlap=date_overlap
            )

            if score >= filters.min_match_score:
                matches.append(
                    BuddyMatchSuggestion(
                        matched_user_id=other_user_id,
                        matched_user_name=other_user.name,
                        matched_user_picture_url=other_user.picture_url,
                        match_score=round(score, 2),
                        common_interests=common_interests,
                        common_destinations=common_dests,
                        match_source="itinerary",
                    )
                )

        return matches

    def _find_matches_from_group_trips(
        self,
        user_id: uuid.UUID,
        user_interests: Set[str],
        user_destinations: Set[str],
        user_trip_dates: dict[str, list[tuple[date, date]]],
        filters: BuddyDiscoveryFilters,
    ) -> List[BuddyMatchSuggestion]:
        """Find potential buddies from overlapping group trips."""
        matches = []

        # Get user's trips
        user_trip_ids = (
            self.db.execute(
                select(GroupTripMember.trip_id).where(
                    GroupTripMember.user_id == user_id
                )
            )
            .scalars()
            .all()
        )

        if not user_trip_ids:
            return []

        # Find other members of the same trips
        query = (
            select(
                GroupTripMember.user_id,
                GroupTrip.destination,
                GroupTrip.start_date,
                GroupTrip.end_date,
            )
            .join(GroupTrip, GroupTripMember.trip_id == GroupTrip.id)
            .where(
                and_(
                    GroupTripMember.trip_id.in_(user_trip_ids),
                    GroupTripMember.user_id != user_id,
                )
            )
        )

        # Filter by destination if specified
        if filters.destination:
            query = query.where(
                GroupTrip.destination.ilike(f"%{filters.destination}%")
            )

        results = self.db.execute(query).all()

        if not results:
            return []

        # Get user info
        user_ids = list(set(r[0] for r in results))
        users = (
            self.db.execute(select(User).where(User.id.in_(user_ids)))
            .scalars()
            .all()
        )
        user_map = {u.id: u for u in users}

        # Get interests for these users from their itineraries
        user_interests_map = {}
        for uid in user_ids:
            user_interests_map[uid] = self._get_user_interests(uid)

        # Process results
        for other_user_id, destination, start_date, end_date in results:
            if other_user_id not in user_map:
                continue

            other_user = user_map[other_user_id]
            other_interests = user_interests_map.get(other_user_id, set())

            # Calculate interest overlap
            interest_score, common_interests = self._calculate_interest_overlap(
                list(user_interests), list(other_interests)
            )

            # Check destination overlap
            dest_lower = destination.lower() if destination else ""
            dest_overlap = dest_lower in user_destinations
            common_dests = [destination] if dest_overlap else []

            # Check for overlapping travel dates at same destination
            date_overlap = False
            if dest_overlap and start_date and end_date:
                date_overlap = self._check_date_overlap(
                    user_trip_dates, destination, start_date, end_date
                )

            # Calculate overall score with date overlap bonus
            score = self._calculate_match_score(
                interest_score, dest_overlap, has_date_overlap=date_overlap
            )
            # Boost score for being in same group trip
            score = min(score + 0.1, 1.0)
            # Additional boost for overlapping dates
            if date_overlap:
                score = min(score + 0.15, 1.0)

            if score >= filters.min_match_score:
                matches.append(
                    BuddyMatchSuggestion(
                        matched_user_id=other_user_id,
                        matched_user_name=other_user.name,
                        matched_user_picture_url=other_user.picture_url,
                        match_score=round(score, 2),
                        common_interests=common_interests,
                        common_destinations=common_dests,
                        match_source="group_trip",
                    )
                )

        return matches

    def _merge_matches(
        self, matches: List[BuddyMatchSuggestion]
    ) -> List[BuddyMatchSuggestion]:
        """Merge duplicate matches, keeping the highest score."""
        merged: dict[uuid.UUID, BuddyMatchSuggestion] = {}

        for match in matches:
            existing = merged.get(match.matched_user_id)
            if existing:
                # Keep higher score
                if match.match_score > existing.match_score:
                    # Merge common interests and destinations
                    match.common_interests = list(
                        set(existing.common_interests + match.common_interests)
                    )
                    match.common_destinations = list(
                        set(existing.common_destinations + match.common_destinations)
                    )
                    match.match_source = "combined"
                    merged[match.matched_user_id] = match
                else:
                    existing.common_interests = list(
                        set(existing.common_interests + match.common_interests)
                    )
                    existing.common_destinations = list(
                        set(existing.common_destinations + match.common_destinations)
                    )
                    existing.match_source = "combined"
            else:
                merged[match.matched_user_id] = match

        return list(merged.values())

    def save_match(
        self,
        user_id: uuid.UUID,
        suggestion: BuddyMatchSuggestion,
        status: str = "suggested",
    ) -> BuddyMatch:
        """Save a buddy match to the database."""
        # Check if match already exists
        existing = (
            self.db.execute(
                select(BuddyMatch).where(
                    and_(
                        BuddyMatch.user_id == user_id,
                        BuddyMatch.matched_user_id == suggestion.matched_user_id,
                    )
                )
            )
            .scalar_one_or_none()
        )

        if existing:
            # Update existing match
            existing.match_score = suggestion.match_score
            existing.common_interests = suggestion.common_interests
            existing.common_destinations = suggestion.common_destinations
            if status != "suggested":
                existing.status = status
            self.db.commit()
            self.db.refresh(existing)
            return existing

        # Create new match
        match = BuddyMatch(
            user_id=user_id,
            matched_user_id=suggestion.matched_user_id,
            match_score=suggestion.match_score,
            common_interests=suggestion.common_interests,
            common_destinations=suggestion.common_destinations,
            status=status,
        )
        self.db.add(match)
        self.db.commit()
        self.db.refresh(match)
        return match

    def get_my_matches(
        self,
        user_id: uuid.UUID,
        status: Optional[str] = None,
        page: int = 1,
        per_page: int = 20,
    ) -> Tuple[List[dict], int]:
        """Get user's buddy matches with optional status filter."""
        # Base query
        base = select(BuddyMatch).where(BuddyMatch.user_id == user_id)

        if status:
            base = base.where(BuddyMatch.status == status)

        # Count total
        count_q = select(func.count()).select_from(base.subquery())
        total = self.db.execute(count_q).scalar() or 0

        # Paginated results with user info
        matches = (
            self.db.execute(
                base.order_by(BuddyMatch.match_score.desc())
                .offset((page - 1) * per_page)
                .limit(per_page)
            )
            .scalars()
            .all()
        )

        # Enrich with matched user info
        results = []
        for match in matches:
            matched_user = (
                self.db.execute(select(User).where(User.id == match.matched_user_id))
                .scalar_one()
            )
            results.append(
                {
                    "id": match.id,
                    "user_id": match.user_id,
                    "matched_user_id": match.matched_user_id,
                    "matched_user_name": matched_user.name,
                    "matched_user_picture_url": matched_user.picture_url,
                    "match_score": match.match_score,
                    "common_interests": match.common_interests,
                    "common_destinations": match.common_destinations,
                    "status": match.status,
                    "created_at": match.created_at,
                    "updated_at": match.updated_at,
                }
            )

        return results, total

    def get_incoming_requests(
        self,
        user_id: uuid.UUID,
        page: int = 1,
        per_page: int = 20,
    ) -> Tuple[List[dict], int]:
        """
        Get pending connection requests from other users.
        These are matches where the current user is the matched_user_id and status is 'pending'.
        """
        # Base query - matches where I'm the target and status is pending
        base = select(BuddyMatch).where(
            and_(
                BuddyMatch.matched_user_id == user_id,
                BuddyMatch.status == "pending",
            )
        )

        # Count total
        count_q = select(func.count()).select_from(base.subquery())
        total = self.db.execute(count_q).scalar() or 0

        # Paginated results with initiator user info
        matches = (
            self.db.execute(
                base.order_by(BuddyMatch.created_at.desc())
                .offset((page - 1) * per_page)
                .limit(per_page)
            )
            .scalars()
            .all()
        )

        # Enrich with initiator user info
        results = []
        for match in matches:
            initiator = (
                self.db.execute(select(User).where(User.id == match.user_id))
                .scalar_one()
            )
            results.append(
                {
                    "id": match.id,
                    "user_id": match.user_id,
                    "matched_user_id": match.matched_user_id,
                    "matched_user_name": initiator.name,
                    "matched_user_picture_url": initiator.picture_url,
                    "match_score": match.match_score,
                    "common_interests": match.common_interests,
                    "common_destinations": match.common_destinations,
                    "status": match.status,
                    "created_at": match.created_at,
                    "updated_at": match.updated_at,
                }
            )

        return results, total

    def update_match_status(
        self, match_id: uuid.UUID, user_id: uuid.UUID, action: str
    ) -> BuddyMatch:
        """
        Update the status of a buddy match.
        Also handles accepting incoming requests and creates reciprocal matches.
        """
        # Look for match where user is either the owner or the matched user
        match = (
            self.db.execute(
                select(BuddyMatch).where(
                    and_(
                        BuddyMatch.id == match_id,
                        or_(
                            BuddyMatch.user_id == user_id,
                            BuddyMatch.matched_user_id == user_id,
                        ),
                    )
                )
            )
            .scalar_one_or_none()
        )

        if not match:
            raise ValueError("Match not found")

        status_map = {
            "accept": "accepted",
            "reject": "rejected",
            "block": "blocked",
        }

        if action not in status_map:
            raise ValueError(f"Invalid action: {action}")

        new_status = status_map[action]
        match.status = new_status

        # If accepting, create reciprocal match so both users are connected
        if new_status == "accepted":
            # Determine who is the other user
            if match.user_id == user_id:
                # I initiated, create reverse match for the other person
                other_user_id = match.matched_user_id
            else:
                # Other person initiated, create match for me pointing to them
                other_user_id = match.user_id

            # Check if reciprocal match already exists
            existing_reverse = (
                self.db.execute(
                    select(BuddyMatch).where(
                        and_(
                            BuddyMatch.user_id == user_id,
                            BuddyMatch.matched_user_id == other_user_id,
                        )
                    )
                )
                .scalar_one_or_none()
            )

            if not existing_reverse:
                # Create reciprocal match
                reciprocal = BuddyMatch(
                    user_id=user_id,
                    matched_user_id=other_user_id,
                    match_score=match.match_score,
                    common_interests=match.common_interests,
                    common_destinations=match.common_destinations,
                    status="accepted",
                )
                self.db.add(reciprocal)

        self.db.commit()
        self.db.refresh(match)
        return match

    def delete_match(self, match_id: uuid.UUID, user_id: uuid.UUID) -> None:
        """Delete a buddy match."""
        match = (
            self.db.execute(
                select(BuddyMatch).where(
                    and_(
                        BuddyMatch.id == match_id,
                        BuddyMatch.user_id == user_id,
                    )
                )
            )
            .scalar_one_or_none()
        )

        if not match:
            raise ValueError("Match not found")

        self.db.delete(match)
        self.db.commit()
