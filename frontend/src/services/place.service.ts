import api from "@/lib/api";
import type { PlaceCardData, PlaceDetail } from "@/types/place";

export interface PlaceSearchParams {
  category?: string;
  district?: string;
  q?: string;
  query?: string;
  skip?: number;
  limit?: number;
}

export interface DuplicateCheckParams {
  name: string;
  district?: string;
  latitude?: number;
  longitude?: number;
}

export const fetchPlaces = async (params?: PlaceSearchParams): Promise<PlaceCardData[]> => {
  const queryParams = { ...params };
  if (queryParams.query && !queryParams.q) {
    queryParams.q = queryParams.query;
  }
  const res = await api.get<PlaceCardData[]>("/api/v1/places", { params: queryParams });
  return res.data;
};

export const fetchPlaceBySlug = async (slug: string): Promise<PlaceDetail> => {
  const res = await api.get<PlaceDetail>(`/api/v1/places/${slug}`);
  return res.data;
};

export const checkDuplicatePlace = async (params: DuplicateCheckParams) => {
  const res = await api.get<{ is_duplicate: boolean; matches: Array<{ id: string; name: string; score: number }> }>(
    "/api/v1/places/duplicate-check",
    { params }
  );
  return res.data;
};

export const createPlaceDraft = async (data: Record<string, unknown>) => {
  const res = await api.post<{ id: string; name: string; status: string }>("/api/v1/places/drafts", data);
  return res.data;
};

export const submitPlaceDraft = async (draftId: string) => {
  const res = await api.post<{ id: string; status: string }>(`/api/v1/places/drafts/${draftId}/submit`);
  return res.data;
};
