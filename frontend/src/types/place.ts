import type { VideoEmbed } from "@/types/community";

export type PlaceSourceType = "admin" | "community";
export type CostLevel = "low" | "moderate" | "high";
export type TravelStyle = "budget" | "comfort" | "adventure" | "family";

export interface PlaceImage {
  id: string;
  url: string | null;
  asset_key?: "banner";
  alt: string;
  caption?: string | null;
  credit?: string | null;
  object_position?: string;
}

export interface PlaceSource {
  type: PlaceSourceType;
  label: string;
  verified: boolean;
  contributor_name: string;
}

export interface PlaceLocation {
  village?: string | null;
  upazila: string;
  district: string;
  division: string;
  nearest_hub: string;
  latitude: number;
  longitude: number;
}

export interface PlaceQuickFacts {
  cost_level: CostLevel;
  budget_estimate: string;
  best_season: string;
  suggested_duration: string;
  access_difficulty: string;
  guide_requirement: string;
  ideal_for: string[];
}

export interface SignalReport {
  carrier: string;
  network: string;
  reliability: string;
  report_count: number;
  last_reported_at: string;
}

export interface PlaceMetrics {
  report_count: number;
  last_updated_at: string;
  crowd_level: string;
  road_condition: string;
  payment_methods: string[];
  electricity: string;
  drinking_water: string;
  signal_reports: SignalReport[];
}

export interface ReviewObservation {
  crowd_level: string;
  access_difficulty: string;
  road_condition: string;
  payment_methods: string[];
  carrier?: string | null;
  network?: string | null;
  network_reliability?: string | null;
  safety?: string | null;
  cleanliness?: string | null;
}

export interface PlaceReview {
  id: string;
  author_name: string;
  author_initials: string;
  rating: number;
  visited_at: string;
  submitted_at: string;
  travel_style: TravelStyle;
  group_type: string;
  group_size: number;
  starting_location: string;
  actual_cost: string;
  title: string;
  travel_guide: string;
  photos?: PlaceImage[];
  video_embeds?: Array<VideoEmbed & { caption?: string | null }>;
  observations: ReviewObservation;
  helpful_count: number;
}

export interface PlaceDetail {
  id: string;
  slug: string;
  name: string;
  category: string;
  tags: string[];
  source: PlaceSource;
  summary: string;
  description: string;
  rating: number | null;
  review_count: number;
  location: PlaceLocation;
  cover_image: PlaceImage;
  gallery: PlaceImage[];
  quick_facts: PlaceQuickFacts;
  highlights: string[];
  know_before_you_go: string[];
  metrics: PlaceMetrics;
  reviews: PlaceReview[];
  created_at: string;
  updated_at: string;
}

export interface PlaceCardData {
  id: string;
  slug: string;
  name: string;
  category: string;
  tags: string[];
  source: PlaceSource;
  summary: string;
  rating: number | null;
  review_count: number;
  location: Pick<PlaceLocation, "upazila" | "district">;
  cover_image: PlaceImage;
  quick_facts: Pick<
    PlaceQuickFacts,
    "cost_level" | "budget_estimate" | "best_season" | "access_difficulty"
  >;
}

export interface ReviewDraft {
  author_name: string;
  rating: number;
  visited_at: string;
  travel_style: TravelStyle;
  group_type: string;
  group_size: number;
  starting_location: string;
  actual_cost: string;
  title: string;
  travel_guide: string;
  photo_files: File[];
  video_embeds: Array<Omit<VideoEmbed, "id">>;
  crowd_level: string;
  access_difficulty: string;
  road_condition: string;
  payment_methods: string[];
  carrier: string;
  network: string;
  network_reliability: string;
  safety: string;
  cleanliness: string;
}
