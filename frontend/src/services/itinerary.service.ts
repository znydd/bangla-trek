import { queryOptions } from "@tanstack/react-query";
import api from "@/lib/api";
import type {
  GenerateItineraryPayload,
  Itinerary,
  ItineraryListItem,
} from "@/types/itinerary";

const BASE = "/api/v1/itineraries";

// --- Query options ---

export const userItinerariesQueryOptions = () =>
  queryOptions<ItineraryListItem[]>({
    queryKey: ["itineraries"],
    queryFn: async () => {
      const res = await api.get<ItineraryListItem[]>(BASE);
      return res.data;
    },
  });

export const itineraryQueryOptions = (itineraryId: string) =>
  queryOptions<Itinerary>({
    queryKey: ["itineraries", itineraryId],
    queryFn: async () => {
      const res = await api.get<Itinerary>(`${BASE}/${itineraryId}`);
      return res.data;
    },
  });

// --- Mutations ---

export const generateItinerary = async (payload: GenerateItineraryPayload) => {
  const res = await api.post<Itinerary>(`${BASE}/generate`, payload);
  return res.data;
};

export const deleteItinerary = async (id: string) => {
  await api.delete(`${BASE}/${id}`);
};
