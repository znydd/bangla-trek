export type FacilityType = "hospital" | "police_station" | "tourist_police";

export interface EmergencyFacility {
  id: string;
  name: string;
  facility_type: FacilityType;
  address: string;
  district: string;
  latitude: number;
  longitude: number;
  phone_number: string | null;
  notes: string | null;
  distance_km: number | null;
}

export interface EmergencyFacilityListResponse {
  items: EmergencyFacility[];
  total: number;
}

export interface EmergencyFacilityCreate {
  name: string;
  facility_type: FacilityType;
  address: string;
  district: string;
  latitude: number;
  longitude: number;
  phone_number?: string | null;
  notes?: string | null;
}

export interface FacilitySearchParams {
  facility_type?: FacilityType;
  district?: string;
  search?: string;
  lat?: number;
  lng?: number;
  limit?: number;
}

export interface EmergencyPhrase {
  id: string;
  english: string;
  bengali: string;
  romanized: string;
}

export interface EmergencyPhraseCategory {
  category: string;
  phrases: EmergencyPhrase[];
}

export interface TranslatePayload {
  text: string;
  dialect?: string;
}

export interface TranslateResponse {
  original_text: string;
  bengali: string;
  romanized: string;
  dialect: string;
  dialect_text: string | null;
  dialect_romanized: string | null;
}
