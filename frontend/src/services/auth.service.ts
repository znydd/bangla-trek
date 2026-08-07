import { queryOptions } from "@tanstack/react-query";
import api from "@/lib/api";
import type { User } from "@/types/user";

const API_BASE = import.meta.env.VITE_API_URL as string;

// Redirect to backend → Google consent → backend sets cookies → redirects to /auth/callback
export const loginWithGoogle = () => {
  window.location.href = `${API_BASE}/api/v1/auth/google`;
};

// Dev login helper for quick local testing
export const devLogin = async (email: string, name: string, role: string = "user") => {
  const res = await api.post<{ access_token: string; user: User }>("/api/v1/auth/dev-login", {
    email,
    name,
    role,
  });
  return res.data;
};

// Clears httpOnly cookies server-side then redirects to /login
export const logout = async () => {
  await api.post("/api/v1/auth/logout");
  window.location.href = "/";
};

// TanStack Query option — browser auto-sends the httpOnly cookie, no token handling needed
export const currentUserQueryOptions = queryOptions<User>({
  queryKey: ["auth", "me"],
  queryFn: async () => {
    const res = await api.get<User>("/api/v1/auth/me");
    return res.data;
  },
  retry: false,
  staleTime: 5 * 60 * 1000, // 5 minutes
});

