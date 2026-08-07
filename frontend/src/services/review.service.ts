import { queryOptions } from "@tanstack/react-query";
import api from "@/lib/api";

export interface PlaceReviewSummaryData {
  place_id: string;
  total_reviews: number;
  average_rating: number;
  rating_breakdown: Record<string, number>;
  most_common_travel_style: string | null;
  typical_access_difficulty: string | null;
  most_reported_payment_method: string | null;
  cost_range: {
    min: number | null;
    median: number | null;
    max: number | null;
  };
  crowd_level_distribution: Record<string, number>;
  network_reliability_distribution: Record<string, number>;
}

export const fetchPlaceReviews = async (placeId: string) => {
  const res = await api.get(`/api/v1/places/${placeId}/reviews`);
  return res.data;
};

export const placeReviewsQueryOptions = (placeId: string) =>
  queryOptions({
    queryKey: ["places", placeId, "reviews"],
    queryFn: () => fetchPlaceReviews(placeId),
    retry: false,
  });

export const fetchPlaceReviewSummary = async (placeId: string): Promise<PlaceReviewSummaryData> => {
  const res = await api.get<PlaceReviewSummaryData>(`/api/v1/places/${placeId}/review-summary`);
  return res.data;
};

export const placeReviewSummaryQueryOptions = (placeId: string) =>
  queryOptions<PlaceReviewSummaryData>({
    queryKey: ["places", placeId, "review-summary"],
    queryFn: () => fetchPlaceReviewSummary(placeId),
    retry: false,
  });

export const submitPlaceReview = async (placeId: string, payload: Record<string, unknown>) => {
  const res = await api.post(`/api/v1/places/${placeId}/reviews`, payload);
  return res.data;
};

export const toggleReviewHelpful = async (placeId: string, reviewId: string) => {
  const res = await api.post(`/api/v1/places/${placeId}/reviews/${reviewId}/helpful`);
  return res.data;
};
