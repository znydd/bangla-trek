export interface GroupActivity {
  id: string;
  trip_id: string;
  user_id: string;
  user_name: string;
  user_picture_url?: string;
  activity_type: string;
  description: string;
  metadata_json?: Record<string, any>;
  created_at: string;
}

export interface PollOption {
  id: string;
  poll_id: string;
  text: string;
  image_url?: string;
  itinerary_activity_id?: string;
  vote_count: number;
  is_voted_by_me: boolean;
}

export interface Poll {
  id: string;
  trip_id: string;
  creator_id: string;
  creator_name: string;
  title: string;
  description?: string;
  is_active: boolean;
  created_at: string;
  options: PollOption[];
  total_votes: number;
  my_vote_option_id?: string;
}

export interface PollOptionCreate {
  text: string;
  image_url?: string;
  itinerary_activity_id?: string;
}

export interface PollCreate {
  title: string;
  description?: string;
  options: PollOptionCreate[];
}

export interface ItineraryLinkRequest {
  itinerary_id: string;
}
