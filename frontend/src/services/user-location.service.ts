import { queryOptions } from "@tanstack/react-query";
import api from "@/lib/api";
import type { UserLocation, UserLocationPoint, UserLocationUpsert } from "@/types/user-location";

const BASE = "/api/v1/user-locations";

export const myUserLocationQueryOptions = () =>
  queryOptions<UserLocation | null>({
    queryKey: ["user-locations", "me"],
    queryFn: async () => {
      const res = await api.get<UserLocation | null>(`${BASE}/me`);
      return res.data;
    },
    staleTime: 10_000,
  });

export type NearbyUserLocationsParams = {
  lat: number;
  lng: number;
  radius_km?: number;
  status?: string;
};

export const nearbyUserLocationsQueryOptions = (params: NearbyUserLocationsParams) =>
  queryOptions<UserLocationPoint[]>({
    queryKey: ["user-locations", "nearby", params],
    queryFn: async () => {
      const res = await api.get<UserLocationPoint[]>(`${BASE}/nearby`, { params });
      return res.data;
    },
    enabled: Number.isFinite(params.lat) && Number.isFinite(params.lng),
    staleTime: 5_000,
  });

export const upsertMyLocation = async (payload: UserLocationUpsert) => {
  const res = await api.put<UserLocation>(`${BASE}/me`, payload);
  return res.data;
};

export const deleteMyLocation = async () => {
  const res = await api.delete<{ message: string }>(`${BASE}/me`);
  return res.data;
};

