import { queryOptions } from "@tanstack/react-query";
import api from "@/lib/api";
import type {
  Accommodation,
  AccommodationListResponse,
  AccommodationSearchParams,
  AIRecommendationsResponse,
} from "@/types/accommodation";

const BASE = "/api/v1/accommodations";
const LIST_BASE = `${BASE}/`;

// --- Query options ---

export const accommodationsQueryOptions = (
  params: AccommodationSearchParams = {},
) =>
  queryOptions<AccommodationListResponse>({
    queryKey: ["accommodations", params],
    queryFn: async () => {
      const res = await api.get<AccommodationListResponse>(LIST_BASE, { params });
      return res.data;
    },
  });

export const accommodationQueryOptions = (entryId: string) =>
  queryOptions<Accommodation>({
    queryKey: ["accommodations", entryId],
    queryFn: async () => {
      const res = await api.get<Accommodation>(`${BASE}/${entryId}`);
      return res.data;
    },
  });

export const aiRecommendationsQueryOptions = (itineraryId: string) =>
  queryOptions<AIRecommendationsResponse>({
    queryKey: ["accommodation-recommendations", itineraryId],
    queryFn: async () => {
      const res = await api.get<AIRecommendationsResponse>(
        `${BASE}/itinerary/${itineraryId}/recommendations`,
      );
      return res.data;
    },
    staleTime: 5 * 60 * 1000, // Cache for 5 minutes to avoid excessive API calls
  });
