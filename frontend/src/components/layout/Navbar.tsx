import { Link } from "@tanstack/react-router";
import { Compass, LogOut } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import { loginWithGoogle, logout } from "@/services/auth.service";

export default function Navbar() {
  const { user, isAuthenticated, isLoading } = useAuth();

  const navItemClass =
    "text-sm text-white/65 transition-colors hover:text-white";
  return (
    <header className="relative z-50 px-4 pt-4">
      <nav className="mx-auto flex h-14 max-w-5xl items-center justify-between rounded-full border border-white/10 bg-zinc-950 px-3 pl-5 text-white shadow-2xl shadow-black/15">
        <Link to="/" className="flex items-center gap-2">
          <span className="flex h-8 w-8 items-center justify-center rounded-full bg-emerald-500 text-zinc-950">
            <Compass size={17} strokeWidth={2.6} />
          </span>

          <span className="hidden text-sm font-bold tracking-tight sm:block">
            Bangla Trek
          </span>
        </Link>

        <div className="hidden items-center gap-7 md:flex">
          <a href="/#places" className={navItemClass}>
            Explore
          </a>

          {isAuthenticated ? (
            <>
              <Link to="/emergency" className={navItemClass}>
                Travel Companion
              </Link>

              <Link to="/community/new" className={navItemClass}>
                Contribute
              </Link>
            </>
          ) : (
            <>
              <button
                type="button"
                onClick={loginWithGoogle}
                className={navItemClass}
              >
                Travel Companion
              </button>

              <button
                type="button"
                onClick={loginWithGoogle}
                className={navItemClass}
              >
                Contribute
              </button>
            </>
          )}
        </div>

        <div className="flex items-center gap-2">
          {isLoading ? (
            <div className="h-9 w-24 animate-pulse rounded-full bg-white/10" />
          ) : isAuthenticated && user ? (
            <>
              <div className="hidden items-center gap-2 sm:flex">
                {user.picture_url && (
                  <img
                    src={user.picture_url}
                    alt={user.name}
                    className="h-8 w-8 rounded-full border border-white/20 object-cover"
                  />
                )}

                <span className="max-w-24 truncate text-sm font-medium">
                  {user.name.split(" ")[0]}
                </span>
              </div>

              <button
                type="button"
                onClick={logout}
                aria-label="Log out"
                className="flex h-9 w-9 items-center justify-center rounded-full text-white/60 transition-colors hover:bg-white/10 hover:text-white"
              >
                <LogOut size={16} />
              </button>
            </>
          ) : (
            <>
              <button
                type="button"
                onClick={loginWithGoogle}
                className="rounded-full px-4 py-2 text-sm font-medium text-white/75 transition-colors hover:text-white"
              >
                Login
              </button>

              <button
                type="button"
                onClick={loginWithGoogle}
                className="hidden rounded-full bg-white px-5 py-2 text-sm font-semibold text-zinc-950 transition-transform hover:scale-[1.02] sm:block"
              >
                Get started
              </button>
            </>
          )}
        </div>
      </nav>
    </header>
  );
}
