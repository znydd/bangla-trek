export type ReviewTravelStyle = "budget" | "luxury" | "adventure" | "family";

export type ReviewSort = "newest" | "highest_rating" | "lowest_rating";

export interface ReviewPhoto {
  id: string;
  url: string;
  public_id: string;
  caption: string | null;
  created_at: string;
}

export interface EntryReview {
  id: string;
  entry_id: string;
  user_id: string;
  author_name: string;
  author_picture_url: string | null;
  rating: number;
  travel_style: ReviewTravelStyle;
  actual_cost_bdt: number | null;
  time_spent_minutes: number | null;
  review_text: string;
  photos: ReviewPhoto[];
  itinerary_id: string | null;
  activity_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface ReviewStyleSummary {
  travel_style: ReviewTravelStyle;
  count: number;
}

export interface ReviewSummary {
  average_rating: number | null;
  review_count: number;
  breakdown: Record<1 | 2 | 3 | 4 | 5, number>;
  by_travel_style: ReviewStyleSummary[];
}

export interface EntryReviewListParams {
  page?: number;
  per_page?: number;
  travel_style?: ReviewTravelStyle;
  sort_by?: ReviewSort;
}

export interface EntryReviewListResponse {
  items: EntryReview[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
  summary: ReviewSummary;
  my_review_id: string | null;
}

export interface CreateReviewPayload {
  rating: number;
  travel_style: ReviewTravelStyle;
  actual_cost_bdt?: number | null;
  time_spent_minutes?: number | null;
  review_text: string;
  itinerary_id?: string | null;
  activity_id?: string | null;
}

export type UpdateReviewPayload = Partial<CreateReviewPayload>;
