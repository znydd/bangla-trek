import { queryOptions } from "@tanstack/react-query";
import api from "@/lib/api";
import type {
  GenerateItineraryPayload,
  Itinerary,
  ItineraryListItem,
} from "@/types/itinerary";

const BASE = "/api/v1/itineraries";
const LIST_BASE = `${BASE}/`;

// --- Query options ---

export const userItinerariesQueryOptions = () =>
  queryOptions<ItineraryListItem[]>({
    queryKey: ["itineraries"],
    queryFn: async () => {
      const res = await api.get<ItineraryListItem[]>(LIST_BASE);
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

export const exportItineraryPdf = async (itineraryId: string) => {
  const response = await api.get(`${BASE}/${itineraryId}/export`, {
    responseType: "blob",
  });
  
  // Create a link element, hide it, direct it to the blob, and click it
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement("a");
  link.href = url;
  link.setAttribute("download", `itinerary_${itineraryId}.pdf`);
  document.body.appendChild(link);
  link.click();
  
  // Clean up
  link.parentNode?.removeChild(link);
  window.URL.revokeObjectURL(url);
};
