import { queryOptions } from "@tanstack/react-query";
import api from "@/lib/api";
import type {
  GroupActivity,
  Poll,
  PollCreate,
  ItineraryLinkRequest,
} from "@/types/group-collaboration";

const BASE = "/api/v1/group-trips";

// --- Activity Feed ---

export const groupActivityQueryOptions = (tripId: string) =>
  queryOptions<GroupActivity[]>({
    queryKey: ["group-activity", tripId],
    queryFn: async () => {
      const res = await api.get<GroupActivity[]>(`${BASE}/${tripId}/activity`);
      return res.data;
    },
    refetchInterval: 10000, // Refresh activity feed every 10 seconds
  });

// --- Polling ---

export const groupPollsQueryOptions = (tripId: string) =>
  queryOptions<Poll[]>({
    queryKey: ["group-polls", tripId],
    queryFn: async () => {
      const res = await api.get<Poll[]>(`${BASE}/${tripId}/polls`);
      return res.data;
    },
    refetchInterval: 15000, // Refresh polls every 15 seconds
  });

export const createPoll = async (tripId: string, payload: PollCreate) => {
  const res = await api.post<Poll>(`${BASE}/${tripId}/polls`, payload);
  return res.data;
};

export const voteInPoll = async (pollId: string, optionId: string) => {
  const res = await api.post(`/api/v1/polls/${pollId}/vote`, null, {
    params: { option_id: optionId },
  });
  return res.data;
};

// --- Itinerary Linking ---

export const linkItinerary = async (tripId: string, itineraryId: string) => {
  const payload: ItineraryLinkRequest = { itinerary_id: itineraryId };
  const res = await api.patch(`${BASE}/${tripId}/itinerary`, payload);
  return res.data;
};
