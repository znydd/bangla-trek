import { queryOptions } from "@tanstack/react-query";
import api from "@/lib/api";
import type {
  EmergencyFacilityListResponse,
  EmergencyFacility,
  EmergencyFacilityCreate,
  EmergencyPhraseCategory,
  FacilitySearchParams,
  TranslatePayload,
  TranslateResponse,
} from "@/types/emergency";

const BASE = "/api/v1/emergency";

// --- Query options ---

export const emergencyFacilitiesQueryOptions = (
  params: FacilitySearchParams = {},
) =>
  queryOptions<EmergencyFacilityListResponse>({
    queryKey: ["emergency-facilities", params],
    queryFn: async () => {
      const res = await api.get<EmergencyFacilityListResponse>(
        `${BASE}/facilities`,
        { params },
      );
      return res.data;
    },
  });

export const nearestFacilitiesQueryOptions = (
  lat: number,
  lng: number,
  facilityType?: string,
  limit?: number,
) =>
  queryOptions<EmergencyFacility[]>({
    queryKey: ["emergency-nearest", lat, lng, facilityType, limit],
    queryFn: async () => {
      const res = await api.get<EmergencyFacility[]>(
        `${BASE}/facilities/nearest`,
        {
          params: {
            lat,
            lng,
            facility_type: facilityType,
            limit: limit || 5,
          },
        },
      );
      return res.data;
    },
    enabled: !!lat && !!lng,
  });

export const emergencyPhrasesQueryOptions = () =>
  queryOptions<EmergencyPhraseCategory[]>({
    queryKey: ["emergency-phrases"],
    queryFn: async () => {
      const res = await api.get<EmergencyPhraseCategory[]>(`${BASE}/phrases`);
      return res.data;
    },
    staleTime: 10 * 60 * 1000, // Cache for 10 minutes (static data)
  });

// --- Mutations ---

export const translatePhrase = async (payload: TranslatePayload) => {
  const res = await api.post<TranslateResponse>(`${BASE}/translate`, payload);
  return res.data;
};

export const createFacility = async (payload: EmergencyFacilityCreate) => {
  const res = await api.post<EmergencyFacility>(`${BASE}/facilities`, payload);
  return res.data;
};

export const deleteFacility = async (facilityId: string) => {
  const res = await api.delete(`${BASE}/facilities/${facilityId}`);
  return res.data;
};
