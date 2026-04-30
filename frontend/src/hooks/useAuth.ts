import { useQuery } from "@tanstack/react-query";
import { currentUserQueryOptions } from "@/services/auth.service";

export function useAuth() {
  const { data: user, isLoading, error } = useQuery(currentUserQueryOptions);
  return {
    user: user ?? null,
    isAuthenticated: !!user,
    isLoading,
    error,
  };
}
