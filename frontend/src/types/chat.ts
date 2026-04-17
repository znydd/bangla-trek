export interface ChatMessage {
  id: string;
  itinerary_id: string;
  role: "user" | "assistant";
  content: string;
  created_at: string;
}

export interface ChatSendPayload {
  itinerary_id: string;
  message: string;
}

export interface UpdatedActivity {
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

export interface ChatResponse {
  reply: string;
  updated_activities: UpdatedActivity[] | null;
  message: ChatMessage;
}

export interface SeasonalWarning {
  severity: "info" | "warning" | "danger";
  title: string;
  description: string;
  recommended_months: string[] | null;
}

export interface SeasonalIntelResponse {
  destination: string;
  warnings: SeasonalWarning[];
  best_months: string[];
  current_season_summary: string;
}
