import { queryOptions } from "@tanstack/react-query";
import api from "@/lib/api";
import type {
  BuddyMatch,
  BuddyMatchList,
  BuddyMatchSuggestion,
  DiscoverBuddiesParams,
  ListMatchesParams,
  MatchActionPayload,
  ConnectionResponse,
} from "@/types/buddy-match";

const BASE = "/api/v1/buddy-matching";

// --- Query options ---

export const discoverBuddiesQueryOptions = (params: DiscoverBuddiesParams = {}) =>
  queryOptions<BuddyMatchSuggestion[]>({
    queryKey: ["buddy-matching", "discover", params],
    queryFn: async () => {
      const res = await api.get<BuddyMatchSuggestion[]>(`${BASE}/discover`, {
        params,
      });
      return res.data;
    },
  });

export const myMatchesQueryOptions = (params: ListMatchesParams = {}) =>
  queryOptions<BuddyMatchList>({
    queryKey: ["buddy-matching", "my-matches", params],
    queryFn: async () => {
      const res = await api.get<BuddyMatchList>(`${BASE}/my-matches`, {
        params,
      });
      return res.data;
    },
  });

export const suggestedMatchesQueryOptions = () =>
  myMatchesQueryOptions({ status: "suggested", per_page: 100 });

export const pendingMatchesQueryOptions = () =>
  myMatchesQueryOptions({ status: "pending", per_page: 100 });

export const acceptedMatchesQueryOptions = () =>
  myMatchesQueryOptions({ status: "accepted", per_page: 100 });

export const incomingRequestsQueryOptions = () =>
  queryOptions<BuddyMatchList>({
    queryKey: ["buddy-matching", "incoming-requests"],
    queryFn: async () => {
      const res = await api.get<BuddyMatchList>(`${BASE}/incoming-requests`);
      return res.data;
    },
  });

// --- Mutations ---

export const matchAction = async (
  matchId: string,
  payload: MatchActionPayload
) => {
  const res = await api.post<BuddyMatch>(
    `${BASE}/matches/${matchId}/action`,
    payload
  );
  return res.data;
};

export const deleteMatch = async (matchId: string) => {
  const res = await api.delete(`${BASE}/matches/${matchId}`);
  return res.data;
};

export const connectWithUser = async (userId: string) => {
  const res = await api.post<ConnectionResponse>(`${BASE}/connect/${userId}`);
  return res.data;
};
