export interface GroupTripMember {
  user_id: string;
  name: string;
  picture_url: string | null;
  role: "owner" | "member";
  joined_at: string;
}

export interface GroupTrip {
  id: string;
  creator_id: string;
  title: string;
  destination: string;
  description: string | null;
  start_date: string;
  end_date: string;
  visibility: "public" | "private";
  invite_code: string;
  member_count: number;
  itinerary_id: string | null;
  created_at: string;
  creator_name: string;
  creator_picture_url: string | null;
}

export interface GroupTripDetail extends GroupTrip {
  members: GroupTripMember[];
}

export interface GroupTripPreview {
  id: string;
  title: string;
  destination: string;
  description: string | null;
  start_date: string;
  end_date: string;
  visibility: "public" | "private";
  member_count: number;
  itinerary_id: string | null;
  creator_name: string;
  creator_picture_url: string | null;
}

export interface OverlappingTrip {
  id: string;
  title: string;
  destination: string;
  description: string | null;
  start_date: string;
  end_date: string;
  visibility: "public" | "private";
  member_count: number;
  creator_name: string;
  creator_picture_url: string | null;
}

export interface CreateGroupTripPayload {
  title: string;
  destination: string;
  description?: string;
  start_date: string;
  end_date: string;
  visibility: "public" | "private";
}

export interface UpdateGroupTripPayload {
  title?: string;
  destination?: string;
  description?: string;
  start_date?: string;
  end_date?: string;
  visibility?: "public" | "private";
}

export interface GroupTripListParams {
  page?: number;
  per_page?: number;
}
