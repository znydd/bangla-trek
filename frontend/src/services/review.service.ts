import { queryOptions } from "@tanstack/react-query";
import api from "@/lib/api";
import type {
  CreateReviewPayload,
  EntryReview,
  EntryReviewListParams,
  EntryReviewListResponse,
  UpdateReviewPayload,
} from "@/types/review";

const base = (entryId: string) => `/api/v1/community-entries/${entryId}/reviews`;

export const entryReviewsQueryOptions = (
  entryId: string,
  params: EntryReviewListParams = {},
) =>
  queryOptions<EntryReviewListResponse>({
    queryKey: ["community-entries", entryId, "reviews", params],
    queryFn: async () => {
      const res = await api.get<EntryReviewListResponse>(base(entryId), {
        params,
      });
      return res.data;
    },
    retry: false,
  });

export const createReview = async (
  entryId: string,
  payload: CreateReviewPayload,
) => {
  const res = await api.post<EntryReview>(base(entryId), payload);
  return res.data;
};

export const updateReview = async (
  entryId: string,
  reviewId: string,
  payload: UpdateReviewPayload,
) => {
  const res = await api.put<EntryReview>(
    `${base(entryId)}/${reviewId}`,
    payload,
  );
  return res.data;
};

export const deleteReview = async (entryId: string, reviewId: string) => {
  await api.delete(`${base(entryId)}/${reviewId}`);
};

export const uploadReviewPhotos = async (
  entryId: string,
  reviewId: string,
  files: File[],
) => {
  const formData = new FormData();
  for (const file of files) {
    formData.append("files", file);
  }
  const res = await api.post<EntryReview>(
    `${base(entryId)}/${reviewId}/photos`,
    formData,
    { headers: { "Content-Type": "multipart/form-data" } },
  );
  return res.data;
};

export const deleteReviewPhoto = async (
  entryId: string,
  reviewId: string,
  photoId: string,
) => {
  await api.delete(`${base(entryId)}/${reviewId}/photos/${photoId}`);
};
