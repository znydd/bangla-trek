export interface User {
  id: string;
  google_id: string;
  email: string;
  name: string;
  picture_url: string | null;
  role: "user" | "admin";
  is_active: boolean;
  created_at: string;
  updated_at: string;
}
