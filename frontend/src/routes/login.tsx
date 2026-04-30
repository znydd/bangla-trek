import { createFileRoute, redirect } from "@tanstack/react-router";
import { currentUserQueryOptions, loginWithGoogle } from "@/services/auth.service";

export const Route = createFileRoute("/login")({
  beforeLoad: async ({ context }) => {
    // Already authenticated — go to dashboard
    const user = context.queryClient.getQueryData(
      currentUserQueryOptions.queryKey,
    );
    if (user) throw redirect({ to: "/" });
  },
  component: LoginPage,
});

function LoginPage() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[80vh] px-4">
      <div className="bg-white rounded-xl shadow p-8 w-full max-w-sm text-center">
        <h2 className="text-2xl font-bold mb-2">Welcome back</h2>
        <p className="text-gray-500 text-sm mb-6">
          Sign in to plan your Bangladesh adventure
        </p>
        <button
          onClick={loginWithGoogle}
          className="w-full flex items-center justify-center gap-3 border rounded-lg px-4 py-2.5 hover:bg-gray-50 transition-colors font-medium"
        >
          <img
            src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg"
            alt="Google"
            className="w-5 h-5"
          />
          Continue with Google
        </button>
      </div>
    </div>
  );
}
