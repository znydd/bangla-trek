export type EntryCategory =
  | "attraction"
  | "hotel"
  | "guesthouse"
  | "homestay"
  | "restaurant";

export type EntryTag = "trending" | "hidden_gem";

export type PriceRange = "budget" | "mid_range" | "premium" | "luxury";

export interface PhotoItem {
  id: string;
  url: string;
  public_id: string;
  caption: string | null;
}

export interface VideoEmbed {
  id: string;
  url: string;
  platform: "youtube" | "facebook" | "tiktok";
}

export interface CommunityEntry {
  id: string;
  user_id: string;
  author_name: string;
  author_picture_url: string | null;
  category: EntryCategory;
  name: string;
  location: string;
  latitude: number | null;
  longitude: number | null;
  price_range: PriceRange;
  amenities: string[];
  photos: PhotoItem[];
  travel_tips: string;
  video_embeds: VideoEmbed[];
  tags: EntryTag[];
  created_at: string;
  updated_at: string;
}

export interface CommunityEntryListParams {
  page?: number;
  per_page?: number;
  category?: EntryCategory;
  tag?: EntryTag;
  search?: string;
  sort_by?: "newest" | "name";
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

export type CreateEntryPayload = {
  category: EntryCategory;
  name: string;
  location: string;
  latitude?: number | null;
  longitude?: number | null;
  price_range: PriceRange;
  amenities: string[];
  travel_tips: string;
  video_embeds: { url: string; platform: "youtube" | "facebook" | "tiktok" }[];
  tags: EntryTag[];
};

export type UpdateEntryPayload = Partial<CreateEntryPayload>;
