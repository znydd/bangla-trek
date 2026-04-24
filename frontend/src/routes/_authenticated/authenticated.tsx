import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useQueryClient } from "@tanstack/react-query";
import { useEffect } from "react";
import api from "@/lib/api";

export const Route = createFileRoute("/_authenticated/authenticated")({
  component: AuthenticatedPage,
});

function AuthenticatedPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  useEffect(() => {
    navigate({ to: "/community", replace: true });
  }, [navigate]);

  const handleLogout = async () => {
    await api.post("/api/v1/auth/logout");
    queryClient.clear();
    window.location.href = "/";
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen gap-4">
      <p>Taking you to the community page...</p>
      <button onClick={handleLogout}>Logout</button>
    </div>
  );
}
