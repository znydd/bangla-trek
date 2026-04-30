import { createFileRoute } from "@tanstack/react-router";
import { useQueryClient } from "@tanstack/react-query";
import api from "@/lib/api";

export const Route = createFileRoute("/_authenticated/authenticated")({
  component: AuthenticatedPage,
});

function AuthenticatedPage() {
  const queryClient = useQueryClient();

  const handleLogout = async () => {
    await api.post("/api/v1/auth/logout");
    queryClient.clear();
    window.location.href = "/";
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen gap-4">
      <p>authenticated</p>
      <button onClick={handleLogout}>Logout</button>
    </div>
  );
}
