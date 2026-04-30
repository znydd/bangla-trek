import { queryOptions } from "@tanstack/react-query";
import api from "@/lib/api";
import type {
  GroupTrip,
  GroupTripDetail,
  GroupTripPreview,
  GroupTripListParams,
  CreateGroupTripPayload,
  UpdateGroupTripPayload,
  OverlappingTrip,
} from "@/types/group-trip";
import type { PaginatedResponse } from "@/types/community";

const BASE = "/api/v1/group-trips";

// --- Query options ---

export const groupTripsQueryOptions = (params: GroupTripListParams = {}) =>
  queryOptions<PaginatedResponse<GroupTrip>>({
    queryKey: ["group-trips", "public", params],
    queryFn: async () => {
      const res = await api.get<PaginatedResponse<GroupTrip>>(BASE, { params });
      return res.data;
    },
  });

export const myGroupTripsQueryOptions = (params: GroupTripListParams = {}) =>
  queryOptions<PaginatedResponse<GroupTrip>>({
    queryKey: ["group-trips", "my", params],
    queryFn: async () => {
      const res = await api.get<PaginatedResponse<GroupTrip>>(`${BASE}/my`, {
        params,
      });
      return res.data;
    },
  });

export const groupTripDetailQueryOptions = (tripId: string) =>
  queryOptions<GroupTripDetail>({
    queryKey: ["group-trips", tripId],
    queryFn: async () => {
      const res = await api.get<GroupTripDetail>(`${BASE}/${tripId}`);
      return res.data;
    },
  });

export const invitePreviewQueryOptions = (inviteCode: string) =>
  queryOptions<GroupTripPreview>({
    queryKey: ["group-trips", "invite-preview", inviteCode],
    queryFn: async () => {
      const res = await api.get<GroupTripPreview>(
        `${BASE}/invite/${inviteCode}/preview`
      );
      return res.data;
    },
  });

export const discoverOverlappingQueryOptions = (
  destination: string,
  startDate: string,
  endDate: string
) =>
  queryOptions<OverlappingTrip[]>({
    queryKey: ["group-trips", "discover", destination, startDate, endDate],
    queryFn: async () => {
      const res = await api.get<OverlappingTrip[]>(`${BASE}/discover`, {
        params: {
          destination,
          start_date: startDate,
          end_date: endDate,
        },
      });
      return res.data;
    },
    enabled: !!destination && !!startDate && !!endDate,
  });

// --- Mutations ---

export const createGroupTrip = async (payload: CreateGroupTripPayload) => {
  const res = await api.post<GroupTripDetail>(BASE, payload);
  return res.data;
};

export const updateGroupTrip = async (
  tripId: string,
  payload: UpdateGroupTripPayload
) => {
  const res = await api.put<GroupTripDetail>(`${BASE}/${tripId}`, payload);
  return res.data;
};

export const joinGroupTrip = async (inviteCode: string) => {
  const res = await api.post<GroupTripDetail>(`${BASE}/join/${inviteCode}`);
  return res.data;
};

export const leaveGroupTrip = async (tripId: string) => {
  const res = await api.delete(`${BASE}/${tripId}/leave`);
  return res.data;
};

export const deleteGroupTrip = async (tripId: string) => {
  const res = await api.delete(`${BASE}/${tripId}`);
  return res.data;
};
