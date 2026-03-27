import { queryOptions } from "@tanstack/react-query";
import api from "@/lib/api";
import type {
  CommunityEntry,
  CommunityEntryListParams,
  CreateEntryPayload,
  PaginatedResponse,
  UpdateEntryPayload,
} from "@/types/community";

const BASE = "/api/v1/community-entries";

// --- Query options ---

export const communityEntriesQueryOptions = (
  params: CommunityEntryListParams = {},
) =>
  queryOptions<PaginatedResponse<CommunityEntry>>({
    queryKey: ["community-entries", params],
    queryFn: async () => {
      const res = await api.get<PaginatedResponse<CommunityEntry>>(BASE, {
        params,
      });
      return res.data;
    },
  });

export const communityEntryQueryOptions = (entryId: string) =>
  queryOptions<CommunityEntry>({
    queryKey: ["community-entries", entryId],
    queryFn: async () => {
      const res = await api.get<CommunityEntry>(`${BASE}/${entryId}`);
      return res.data;
    },
  });

// --- Mutations ---

export const createEntry = async (payload: CreateEntryPayload) => {
  const res = await api.post<CommunityEntry>(BASE, payload);
  return res.data;
};

export const updateEntry = async (id: string, payload: UpdateEntryPayload) => {
  const res = await api.put<CommunityEntry>(`${BASE}/${id}`, payload);
  return res.data;
};

export const deleteEntry = async (id: string) => {
  await api.delete(`${BASE}/${id}`);
};

export const uploadPhotos = async (entryId: string, files: File[]) => {
  const formData = new FormData();
  for (const file of files) {
    formData.append("files", file);
  }
  const res = await api.post<CommunityEntry>(
    `${BASE}/${entryId}/photos`,
    formData,
    { headers: { "Content-Type": "multipart/form-data" } },
  );
  return res.data;
};

export const deletePhoto = async (entryId: string, photoId: string) => {
  await api.delete(`${BASE}/${entryId}/photos/${photoId}`);
};
