export type UserTravelStatus = "traveling" | "planning" | "offline";

export type UserLocationUpsert = {
  latitude: number;
  longitude: number;
  status?: UserTravelStatus;
  message?: string | null;
};

export type UserLocation = {
  user_id: string;
  latitude: number;
  longitude: number;
  status: string | null;
  message: string | null;
  updated_at: string | null;
};

export type UserLocationPoint = UserLocation & {
  user_name: string | null;
  user_picture_url: string | null;
};

