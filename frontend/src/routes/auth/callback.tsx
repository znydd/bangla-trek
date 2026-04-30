import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useEffect } from "react";

export const Route = createFileRoute("/auth/callback")({
  component: AuthCallback,
});

function AuthCallback() {
  const navigate = useNavigate();

  useEffect(() => {
    // Cookies are already set by the backend redirect.
    // Just navigate — authenticated.tsx beforeLoad will call /auth/me once.
    navigate({ to: "/authenticated" });
  }, [navigate]);

  return (
    <div className="flex items-center justify-center min-h-screen">
      <p>Signing you in…</p>
    </div>
  );
}
