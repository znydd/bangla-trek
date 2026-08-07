import { createFileRoute } from "@tanstack/react-router";
import { useEffect } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { currentUserQueryOptions } from "@/services/auth.service";

export const Route = createFileRoute("/auth/callback")({
  component: AuthCallback,
});

function AuthCallback() {
  const queryClient = useQueryClient();

  useEffect(() => {
    // Invalidate auth query so user object is refetched with cookie
    queryClient.invalidateQueries({ queryKey: currentUserQueryOptions.queryKey });
    // Redirect user to home page
    window.location.href = "/";
  }, [queryClient]);

  return (
    <div className="flex items-center justify-center min-h-[70vh]">
      <p className="text-sm font-semibold text-muted-foreground">Signing you in…</p>
    </div>
  );
}
