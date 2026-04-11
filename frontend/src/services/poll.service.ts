import { queryOptions } from "@tanstack/react-query";
import api from "@/lib/api";
import type { Poll, CreatePollPayload } from "@/types/poll";

const BASE = "/api/v1/trips";

export const tripPollsQueryOptions = (tripId: string) =>
  queryOptions<Poll[]>({
    queryKey: ["polls", tripId],
    queryFn: async () => {
      const res = await api.get<Poll[]>(`${BASE}/${tripId}/polls`);
      return res.data;
    },
    refetchInterval: 5000, // Short polling for near-real-time
  });

export const createPoll = async (tripId: string, payload: CreatePollPayload) => {
  const res = await api.post<Poll>(`${BASE}/${tripId}/polls`, payload);
  return res.data;
};

export const votePoll = async (tripId: string, pollId: string, optionId: string) => {
  const res = await api.post(`${BASE}/${tripId}/polls/${pollId}/vote`, { option_id: optionId });
  return res.data;
};
