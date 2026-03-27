import { createFileRoute, redirect } from "@tanstack/react-router";
import { useQueryClient } from "@tanstack/react-query";
import { currentUserQueryOptions } from "@/services/auth.service";
import api from "@/lib/api";

export const Route = createFileRoute("/authenticated")({
  beforeLoad: async ({ context }) => {
    try {
      await context.queryClient.ensureQueryData(currentUserQueryOptions);
    } catch {
      throw redirect({ to: "/" });
    }
  },
  component: AuthenticatedPage,
});

function AuthenticatedPage() {
  const queryClient = useQueryClient();

  const handleLogout = async () => {
    await api.post("/api/v1/auth/logout");
    queryClient.clear(); // wipe cache before navigating so no stale refetch fires
    window.location.href = "/";
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen gap-4">
      <p>authenticated</p>
      <button onClick={handleLogout}>Logout</button>
    </div>
  );
}
