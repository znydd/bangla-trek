export interface PollOption {
  id: string;
  poll_id: string;
  title: string;
  description?: string;
  vote_count: number;
  has_voted: boolean;
}

export interface Poll {
  id: string;
  trip_id: string;
  creator_id: string;
  creator_name: string;
  title: string;
  category: string;
  is_open: boolean;
  created_at: string;
  options: PollOption[];
  total_votes: number;
}

export interface CreatePollOption {
  title: string;
  description?: string;
}

export interface CreatePollPayload {
  title: string;
  category: string;
  options: CreatePollOption[];
}
