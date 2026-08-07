import { useState } from "react";
import { Link } from "@tanstack/react-router";
import { Compass, LogOut } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import { loginWithGoogle, logout } from "@/services/auth.service";
import { LoginModal } from "@/components/ui/login-modal";

export default function Navbar() {
  const { user, isAuthenticated, isLoading } = useAuth();
  const [loginOpen, setLoginOpen] = useState(false);
  const [loginAction, setLoginAction] = useState("");

  const handleNavClick = (e: React.MouseEvent, action: string) => {
    if (!isAuthenticated) {
      e.preventDefault();
      setLoginAction(action);
      setLoginOpen(true);
    }
  };

  const navItemClass = "text-md text-white/80 transition-colors hover:text-white";

  return (
    <>
      <LoginModal
        open={loginOpen}
        onOpenChange={setLoginOpen}
        action={loginAction}
      />

      <header className="relative z-50 px-4 pt-4">
        <nav className="relative mx-auto flex h-14 max-w-3xl items-center justify-between rounded-full border border-white/10 bg-zinc-900 px-3 pl-5 text-white shadow-2xl shadow-black/15">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2">
            <span className="flex h-10 w-10 items-center justify-center rounded-full bg-emerald-500 text-zinc-950">
              <Compass size={26} strokeWidth={2.6} />
            </span>
            <span className="hidden text-xl font-bold tracking-tight sm:block">
              Bongo Vromon
            </span>
          </Link>

          {/* Nav links — absolutely centered */}
          <div className="absolute left-1/2 hidden -translate-x-1/2 items-center gap-7 md:flex">
            <Link
              to="/travel-buddy"
              className={navItemClass}
              onClick={(e) => handleNavClick(e, "use Travel Buddy")}
            >
              Travel Buddy
            </Link>
            <Link
              to="/contribute"
              className={navItemClass}
              onClick={(e) => handleNavClick(e, "contribute a place")}
            >
              Contribute
            </Link>
          </div>

          {/* Auth section */}
          <div className="flex items-center gap-2">
            {isLoading ? (
              <div className="h-9 w-20 animate-pulse rounded-full bg-white/10" />
            ) : isAuthenticated && user ? (
              <>
                {user.picture_url ? (
                  <img
                    src={user.picture_url}
                    alt={user.name}
                    className="h-9 w-9 rounded-full border-2 border-emerald-500 object-cover"
                  />
                ) : (
                  <div className="flex h-9 w-9 items-center justify-center rounded-full border-2 border-emerald-500 bg-emerald-700 text-sm font-bold text-white">
                    {user.name.charAt(0).toUpperCase()}
                  </div>
                )}

                <span className="hidden max-w-28 truncate text-sm font-medium sm:block">
                  {user.name.split(" ")[0]}
                </span>

                <button
                  type="button"
                  onClick={logout}
                  aria-label="Log out"
                  className="flex h-9 w-9 items-center justify-center rounded-full text-white/50 transition-colors hover:bg-white/10 hover:text-white"
                >
                  <LogOut size={16} />
                </button>
              </>
            ) : (
              <button
                type="button"
                onClick={loginWithGoogle}
                className="rounded-full bg-emerald-600 px-7 py-2 text-sm font-semibold text-white transition-colors hover:bg-emerald-500"
              >
                Login
              </button>
            )}
          </div>
        </nav>
      </header>
    </>
  );
}
