export type Carrier = "GP" | "Robi" | "Banglalink" | "Teletalk";
export type SignalStrength = "No Signal" | "2G" | "3G" | "4G" | "5G";

export interface CarrierSignal {
  carrier: string;
  signal: string;
  votes: number;
}

export interface NomadMetricSummary {
  entry_id: string;
  avg_safety_rating: number | null;
  bkash_available_pct: number;
  signal_by_carrier: CarrierSignal[];
  has_submitted: boolean;
}

export interface NomadMetricSubmit {
  entry_id: string;
  carrier: Carrier;
  signal_strength: SignalStrength;
  safety_rating: number;
  bkash_available: boolean;
}
