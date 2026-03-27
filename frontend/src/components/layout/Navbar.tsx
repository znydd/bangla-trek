import { Link } from "@tanstack/react-router";
import { useAuth } from "@/hooks/useAuth";
import { logout } from "@/services/auth.service";

export default function Navbar() {
  const { isAuthenticated } = useAuth();

  return (
    <nav className="border-b bg-white px-6 py-3 flex items-center justify-between">
      <Link to="/" className="font-bold text-lg text-green-700">
        Bangla Trek
      </Link>
      {isAuthenticated && (
        <button
          onClick={logout}
          className="text-sm text-red-600 hover:underline"
        >
          Logout
        </button>
      )}
    </nav>
  );
}
