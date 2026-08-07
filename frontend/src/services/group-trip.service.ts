import { queryOptions } from "@tanstack/react-query";
import api from "@/lib/api";

export interface TravelTripRead {
  id: string;
  creator_id: string;
  creator_name: string;
  creator_picture_url?: string | null;
  title: string;
  origin: string;
  destination: string;
  start_at: string;
  end_at: string;
  transport?: string | null;
  estimated_cost_min_bdt?: number | null;
  estimated_cost_max_bdt?: number | null;
  max_members: number;
  joined_members_count: number;
  status: string;
  created_at: string;
}

export interface TravelTripMemberPublicRead {
  user_id: string;
  name: string;
  picture_url?: string | null;
  role: string;
  status: string;
  joined_at: string;
}

export interface TravelTripDetailRead {
  id: string;
  creator_id: string;
  creator_name: string;
  creator_picture_url?: string | null;
  title: string;
  origin: string;
  destination: string;
  start_at: string;
  end_at: string;
  meeting_point?: string | null;
  transport?: string | null;
  estimated_cost_min_bdt?: number | null;
  estimated_cost_max_bdt?: number | null;
  description?: string | null;
  itinerary?: string | null;
  max_members: number;
  joined_members_count: number;
  status: string;
  communication_platform?: string | null;
  communication_note?: string | null;
  requirements: Array<{ id: string; requirement: string; sort_order: number }>;
  members: TravelTripMemberPublicRead[];
  created_at: string;
  updated_at: string;
}

export interface TravelTripParticipantRead {
  user_id: string;
  name: string;
  email: string;
  picture_url?: string | null;
  role: string;
  status: string;
  joined_at: string;
}

export interface EmailDraftRead {
  trip_id: string;
  trip_title: string;
  bcc_emails: string[];
  subject: string;
  body: string;
  mailto_url: string;
  gmail_url?: string | null;
}

const BASE = "/api/v1/travel-trips";

export const fetchPublicTrips = async (params?: { origin?: string; destination?: string }) => {
  const res = await api.get<TravelTripRead[]>(BASE, { params });
  return res.data;
};

export const travelTripsQueryOptions = (params?: { origin?: string; destination?: string }) =>
  queryOptions<TravelTripRead[]>({
    queryKey: ["travel-trips", "public", params],
    queryFn: () => fetchPublicTrips(params),
  });

export const fetchTripDetail = async (tripId: string) => {
  const res = await api.get<TravelTripDetailRead>(`${BASE}/${tripId}`);
  return res.data;
};

export const tripDetailQueryOptions = (tripId: string) =>
  queryOptions<TravelTripDetailRead>({
    queryKey: ["travel-trips", tripId],
    queryFn: () => fetchTripDetail(tripId),
    enabled: !!tripId,
  });

export const createTrip = async (payload: Record<string, unknown>) => {
  const res = await api.post<TravelTripDetailRead>(BASE, payload);
  return res.data;
};

export const joinTrip = async (tripId: string) => {
  const res = await api.post<TravelTripDetailRead>(`${BASE}/${tripId}/join`);
  return res.data;
};

export const leaveTrip = async (tripId: string) => {
  const res = await api.delete(`${BASE}/${tripId}/membership`);
  return res.data;
};

export const cancelTrip = async (tripId: string) => {
  const res = await api.post(`${BASE}/${tripId}/cancel`);
  return res.data;
};

export const fetchOrganizerEmailDraft = async (tripId: string) => {
  const res = await api.get<EmailDraftRead>(`${BASE}/${tripId}/email-draft`);
  return res.data;
};

export const fetchOrganizerParticipants = async (tripId: string) => {
  const res = await api.get<TravelTripParticipantRead[]>(`${BASE}/${tripId}/participants`);
  return res.data;
};

export const deleteTrip = async (tripId: string) => {
  const res = await api.delete(`${BASE}/${tripId}`);
  return res.data;
};
