import { createFileRoute } from "@tanstack/react-router";
import { loginWithGoogle } from "@/services/auth.service";

export const Route = createFileRoute("/")({
  component: HomePage,
});

function HomePage() {
  return (
    <div className="flex items-center justify-center min-h-screen">
      <button onClick={loginWithGoogle}>Login with Google</button>
    </div>
  );
}
