export type AccommodationType = "hotel" | "guesthouse" | "homestay";

export interface AccommodationPhoto {
  id: string;
  url: string;
  public_id: string;
  caption: string | null;
}

export interface Accommodation {
  id: string;
  user_id: string;
  category: AccommodationType;
  name: string;
  location: string;
  latitude: number | null;
  longitude: number | null;
  price_range: string;
  amenities: string[];
  travel_tips: string | null;
  tags: string[];
  created_at: string;
  updated_at: string;
  photos: AccommodationPhoto[];
  author_name: string;
  author_picture_url: string | null;
  distance_km: number | null;
}

export interface AccommodationSearchParams {
  page?: number;
  per_page?: number;
  accommodation_type?: AccommodationType;
  price_range?: string;
  amenities?: string[];
  search?: string;
  sort_by?: "newest" | "name" | "price_asc" | "price_desc" | "distance";
  ref_lat?: number;
  ref_lng?: number;
}

export interface AccommodationListResponse {
  items: Accommodation[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

export interface AIAccommodationRecommendation {
  accommodation_id: string;
  name: string;
  category: string;
  price_range: string;
  location: string;
  reasoning: string;
  estimated_cost_per_night: number;
  travel_convenience_score: number;
  cost_benefit_summary: string;
}

export interface AIRecommendationsResponse {
  recommendations: AIAccommodationRecommendation[];
  summary: string;
  itinerary_id: string;
}
