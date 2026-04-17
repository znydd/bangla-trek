import { queryOptions } from "@tanstack/react-query";
import api from "@/lib/api";
import type {
  ChatMessage,
  ChatSendPayload,
  ChatResponse,
  SeasonalIntelResponse,
} from "@/types/chat";

const BASE = "/api/v1/chat";

// --- Query options ---

export const chatHistoryQueryOptions = (itineraryId: string) =>
  queryOptions<ChatMessage[]>({
    queryKey: ["chat", itineraryId],
    queryFn: async () => {
      const res = await api.get<ChatMessage[]>(`${BASE}/${itineraryId}`);
      return res.data;
    },
  });

export const seasonalIntelQueryOptions = (
  destination: string,
  travelMonth?: number
) =>
  queryOptions<SeasonalIntelResponse>({
    queryKey: ["seasonal-intel", destination, travelMonth],
    queryFn: async () => {
      const params: Record<string, string | number> = { destination };
      if (travelMonth) params.travel_month = travelMonth;
      const res = await api.get<SeasonalIntelResponse>(
        `${BASE}/seasonal-intel/`,
        { params }
      );
      return res.data;
    },
    enabled: !!destination,
    staleTime: 1000 * 60 * 30, // cache seasonal data for 30 min
  });

// --- Mutations ---

export const sendChatMessage = async (
  payload: ChatSendPayload
): Promise<ChatResponse> => {
  const res = await api.post<ChatResponse>(BASE, payload);
  return res.data;
};
