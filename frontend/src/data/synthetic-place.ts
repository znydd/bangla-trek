import debotakhumImg from "./debotakhum.jpg";
import sajekImg from "./Sajek.jpg";
import nilgiriImg from "./nilgiri.jpg";
import tanguarImg from "./tanguar_haor.jpg";
import coxBazarImg from "./cox_bazar.jpg";
import sundarbanImg from "./Sundarban.jpg";
import bannerImage from "../../banner.png";
import type { PlaceCardData, PlaceDetail, PlaceImage } from "@/types/place";

const PLACE_LOCAL_IMAGES: Record<string, string> = {
  debotakhum: debotakhumImg,
  sajek: sajekImg,
  nilgiri: nilgiriImg,
  tanguar: tanguarImg,
  cox: coxBazarImg,
  laboni: coxBazarImg,
  sundarban: sundarbanImg,
};

export function getLocalImageForPlace(queryStr?: string | null): string | null {
  if (!queryStr) return null;
  const lower = queryStr.toLowerCase();
  for (const [key, img] of Object.entries(PLACE_LOCAL_IMAGES)) {
    if (lower.includes(key)) return img;
  }
  return null;
}

export function resolvePlaceImage(
  image?: PlaceImage | string | null,
  placeNameOrSlug?: string | null,
): string {
  // 1. Try matching place name/slug first
  if (placeNameOrSlug) {
    const local = getLocalImageForPlace(placeNameOrSlug);
    if (local) return local;
  }

  // 2. Try matching string image URL / caption
  if (typeof image === "string") {
    const local = getLocalImageForPlace(image);
    if (local) return local;
    if (image.startsWith("http")) return image;
  }

  // 3. Try matching image object URL or caption
  if (image && typeof image === "object") {
    if (image.url) {
      const local =
        getLocalImageForPlace(image.url) ||
        getLocalImageForPlace(image.caption) ||
        getLocalImageForPlace(image.alt);
      if (local) return local;
      if (image.url.startsWith("http")) return image.url;
    }
  }

  return bannerImage;
}

export function toPlaceCardData(place: PlaceDetail): PlaceCardData {
  return {
    id: place.id,
    slug: place.slug,
    name: place.name,
    category: place.category,
    tags: place.tags || [],
    source: place.source,
    summary: place.summary,
    rating: place.rating,
    review_count: place.review_count,
    location: {
      upazila: place.location?.upazila || "",
      district: place.location?.district || "",
    },
    cover_image: place.cover_image,
    quick_facts: {
      cost_level: place.quick_facts?.cost_level || "moderate",
      budget_estimate: place.quick_facts?.budget_estimate || "",
      best_season: place.quick_facts?.best_season || "",
      access_difficulty: place.quick_facts?.access_difficulty || "Moderate",
    },
  };
}
