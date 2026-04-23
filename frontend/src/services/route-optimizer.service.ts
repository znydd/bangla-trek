import api from "@/lib/api";

export interface LocationPoint {
  name: string;
  lat: number;
  lng: number;
}

export interface LegEstimate {
  origin_name: string;
  destination_name: string;
  duration: number; // minutes
  distance: number; // km
  mode: string;
  fallback: boolean;
  geometry?: any; // Added to hold the squiggly road lines
}

export interface OptimizedDay {
  day_number: number;
  locations: LocationPoint[];
  legs: LegEstimate[];
  needs_transit_blueprint: boolean; // Added to trigger the UI warning
}

export interface OptimizationRequest {
  start_location: LocationPoint;
  end_location: LocationPoint;
  waypoints: LocationPoint[];
  num_days: number;
  mode: "driving" | "walking" | "cycling";
}

export interface OptimizationResponse {
  days: OptimizedDay[];
  status?: string;
}

export const optimizeRoute = async (data: OptimizationRequest): Promise<OptimizationResponse> => {
  const response = await api.post<OptimizationResponse>("/api/v1/route-optimizer/optimize", data);
  return response.data;
};

export const fetchSavedItineraries = async () => {
  const response = await api.get("/api/v1/itineraries");
  return response.data;
};

export const getItineraryById = async (id: string) => {
  const response = await api.get(`/api/v1/itineraries/${id}`);
  return response.data;
};