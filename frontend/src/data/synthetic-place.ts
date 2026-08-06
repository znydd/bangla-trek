import bannerImage from "../../banner.png";
import rawSyntheticPlace from "./synthetic-place.json";
import type { PlaceCardData, PlaceDetail, PlaceImage } from "@/types/place";

export const syntheticPlace = rawSyntheticPlace as PlaceDetail;

export const syntheticPlaces: PlaceDetail[] = [syntheticPlace];

export function resolvePlaceImage(image: PlaceImage): string {
  if (image.url) return image.url;
  if (image.asset_key === "banner") return bannerImage;
  return bannerImage;
}

export function toPlaceCardData(place: PlaceDetail): PlaceCardData {
  return {
    id: place.id,
    slug: place.slug,
    name: place.name,
    category: place.category,
    tags: place.tags,
    source: place.source,
    summary: place.summary,
    rating: place.rating,
    review_count: place.review_count,
    location: {
      upazila: place.location.upazila,
      district: place.location.district,
    },
    cover_image: place.cover_image,
    quick_facts: {
      cost_level: place.quick_facts.cost_level,
      budget_estimate: place.quick_facts.budget_estimate,
      best_season: place.quick_facts.best_season,
      access_difficulty: place.quick_facts.access_difficulty,
    },
  };
}

export const syntheticPlaceCards = syntheticPlaces.map(toPlaceCardData);
