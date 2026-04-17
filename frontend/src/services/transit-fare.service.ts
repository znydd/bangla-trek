import { queryOptions } from "@tanstack/react-query";
import api from "@/lib/api";
import type {
  BookingLinksResponse,
  CreateTransitFareContributionPayload,
  TransitFareContribution,
  TransitFareContributionList,
  TransitFareContributionListParams,
  TransitFareEstimate,
  TransitFareMode,
} from "@/types/transit-fare";

const BASE = "/api/v1/transit-fares";

export const fareEstimateQueryOptions = (
  origin: string,
  destination: string,
  mode?: TransitFareMode,
) =>
  queryOptions<TransitFareEstimate>({
    queryKey: ["transit-fares", "estimate", origin, destination, mode ?? "all"],
    queryFn: async () => {
      const res = await api.get<TransitFareEstimate>(`${BASE}/estimate`, {
        params: { origin, destination, mode },
      });
      return res.data;
    },
    enabled: !!origin && !!destination,
  });

export const fareContributionsQueryOptions = (
  params: TransitFareContributionListParams = {},
) =>
  queryOptions<TransitFareContributionList>({
    queryKey: ["transit-fares", "contributions", params],
    queryFn: async () => {
      const res = await api.get<TransitFareContributionList>(
        `${BASE}/contributions`,
        { params },
      );
      return res.data;
    },
  });

export const bookingLinksQueryOptions = () =>
  queryOptions<BookingLinksResponse>({
    queryKey: ["transit-fares", "booking-links"],
    queryFn: async () => {
      const res = await api.get<BookingLinksResponse>(`${BASE}/booking-links`);
      return res.data;
    },
    staleTime: 1000 * 60 * 60 * 12,
  });

export const createFareContribution = async (
  payload: CreateTransitFareContributionPayload,
) => {
  const res = await api.post<TransitFareContribution>(
    `${BASE}/contributions`,
    payload,
  );
  return res.data;
};

export const deleteFareContribution = async (contributionId: string) => {
  await api.delete(`${BASE}/contributions/${contributionId}`);
};
