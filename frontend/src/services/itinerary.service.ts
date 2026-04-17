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

export const itineraryQueryOptions = (id: string) =>
  queryOptions({
    queryKey: ["itineraries", id],
    queryFn: async () => {
      const response = await api.get<Itinerary>(`/itinerary/${id}`);
      return response.data;
    },
  });

export const exportItineraryPdf = async (id: string) => {
  const response = await api.get(`/export/itinerary/${id}/pdf`, {
    responseType: "blob",
  });
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement("a");
  link.href = url;
  link.setAttribute("download", `itinerary-${id.slice(0, 8)}.pdf`);
  document.body.appendChild(link);
  link.click();
  link.remove();
};

// --- Mutations ---

export const generateItinerary = async (payload: GenerateItineraryPayload) => {
  const res = await api.post<Itinerary>(`${BASE}/generate`, payload);
  return res.data;
};

export const deleteItinerary = async (id: string) => {
  await api.delete(`${BASE}/${id}`);
};
