export type TransitMode =
  | "bus"
  | "cng"
  | "walking"
  | "rickshaw"
  | "train"
  | "launch"
  | "boat"
  | "ferry"
  | "auto"
  | "bike"
  | "car"
  | "mixed"
  | "other";

export interface TransitBlueprintStep {
  id: string;
  step_number: number;
  instruction: string;
  mode: TransitMode;
  estimated_duration_mins: number | null;
  estimated_cost_bdt: number | null;
}

export interface TransitBlueprint {
  id: string;
  user_id: string;
  origin: string;
  destination: string;
  raw_description: string;
  estimated_duration_mins: number | null;
  estimated_cost_bdt: number | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
  steps: TransitBlueprintStep[];
  author_name: string;
  author_picture_url: string | null;
}

export interface TransitBlueprintListItem {
  id: string;
  origin: string;
  destination: string;
  estimated_duration_mins: number | null;
  estimated_cost_bdt: number | null;
  step_count: number;
  created_at: string;
  author_name: string;
  author_picture_url: string | null;
}

export interface TransitBlueprintSearchParams {
  page?: number;
  per_page?: number;
  search?: string;
  origin?: string;
  destination?: string;
}

export interface TransitBlueprintListResponse {
  items: TransitBlueprintListItem[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

export interface CreateTransitBlueprintPayload {
  origin: string;
  destination: string;
  raw_description: string;
  estimated_duration_mins?: number | null;
  estimated_cost_bdt?: number | null;
  notes?: string | null;
}

export interface ParsePreviewPayload {
  raw_description: string;
  origin?: string;
  destination?: string;
}

export interface ParsedStepPreview {
  step_number: number;
  instruction: string;
  mode: TransitMode;
  estimated_duration_mins: number | null;
  estimated_cost_bdt: number | null;
}

export interface ParsePreviewResponse {
  steps: ParsedStepPreview[];
  total_estimated_duration_mins: number | null;
  total_estimated_cost_bdt: number | null;
}
