export type MatchStatus = "suggested" | "pending" | "accepted" | "rejected" | "blocked";
export type MatchSource = "itinerary" | "group_trip" | "location" | "combined" | "manual";

export interface BuddyMatchSuggestion {
  matched_user_id: string;
  matched_user_name: string;
  matched_user_picture_url: string | null;
  match_score: number;
  common_interests: string[];
  common_destinations: string[];
  match_source: MatchSource;
}

export interface BuddyMatch {
  id: string;
  user_id: string;
  matched_user_id: string;
  matched_user_name: string;
  matched_user_picture_url: string | null;
  match_score: number;
  common_interests: string[];
  common_destinations: string[];
  status: MatchStatus;
  created_at: string;
  updated_at: string;
}

export interface BuddyMatchList {
  items: BuddyMatch[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

export interface DiscoverBuddiesParams {
  destination?: string;
  interest?: string;
  min_match_score?: number;
  limit?: number;
}

export interface ListMatchesParams {
  status?: MatchStatus;
  page?: number;
  per_page?: number;
}

export interface MatchActionPayload {
  action: "accept" | "reject" | "block";
}

export interface ConnectionResponse {
  detail: string;
  match_id: string;
  status: MatchStatus;
}
