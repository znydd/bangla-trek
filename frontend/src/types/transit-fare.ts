export type TransitFareMode = "cng" | "bus" | "train";
export type FareSourceType = "observed" | "quoted" | "booked";

export interface TransitFareModeEstimate {
  mode: TransitFareMode;
  median_fare_bdt: number | null;
  submission_count: number;
  recent_submission_count: number;
  min_fare_bdt: number | null;
  max_fare_bdt: number | null;
  last_updated_at: string | null;
  sample_window_days: number | null;
  is_low_data: boolean;
  used_all_time_fallback: boolean;
}

export interface TransitFareEstimate {
  origin: string;
  destination: string;
  estimates: TransitFareModeEstimate[];
}

export interface TransitFareContribution {
  id: string;
  user_id: string;
  origin: string;
  destination: string;
  mode: TransitFareMode;
  fare_bdt: number;
  min_fare_bdt: number | null;
  max_fare_bdt: number | null;
  notes: string | null;
  source_type: FareSourceType;
  travel_date: string | null;
  submitted_at: string;
  author_name: string;
  author_picture_url: string | null;
}

export interface TransitFareContributionList {
  items: TransitFareContribution[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

export interface TransitFareContributionListParams {
  page?: number;
  per_page?: number;
  origin?: string;
  destination?: string;
  mode?: TransitFareMode;
  date_from?: string;
  date_to?: string;
}

export interface CreateTransitFareContributionPayload {
  origin: string;
  destination: string;
  mode: TransitFareMode;
  fare_bdt: number;
  min_fare_bdt?: number | null;
  max_fare_bdt?: number | null;
  notes?: string | null;
  source_type?: FareSourceType;
  travel_date?: string | null;
}

export interface BookingLink {
  id: string;
  label: string;
  url: string;
}

export interface BookingLinksResponse {
  items: BookingLink[];
}
