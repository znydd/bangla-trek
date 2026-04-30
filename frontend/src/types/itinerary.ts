export type TravelStyle = "budget" | "comfort" | "luxury";
export type GroupType = "solo" | "couple" | "family" | "friends";

export interface ItineraryActivity {
  id: string;
  day_number: number;
  start_time: string;
  end_time: string;
  title: string;
  description: string;
  estimated_cost: number;
  location: string;
  category: string;
  community_entry_id: string | null;
}

export interface Itinerary {
  id: string;
  user_id: string;
  destination: string;
  duration_days: number;
  budget: number;
  travel_style: TravelStyle;
  interests: string[];
  group_type: GroupType;
  created_at: string;
  updated_at: string;
  activities: ItineraryActivity[];
}

export interface ItineraryListItem {
  id: string;
  destination: string;
  duration_days: number;
  budget: number;
  travel_style: TravelStyle;
  group_type: GroupType;
  created_at: string;
  activity_count: number;
}

export interface GenerateItineraryPayload {
  destination: string;
  duration_days: number;
  budget: number;
  travel_style: TravelStyle;
  interests: string[];
  group_type: GroupType;
}
