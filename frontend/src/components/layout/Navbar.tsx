import { Link } from "@tanstack/react-router";
import { useAuth } from "@/hooks/useAuth";
import { logout, loginWithGoogle } from "@/services/auth.service";
import { Button } from "@/components/ui/button";
import NotificationDropdown from "@/components/layout/NotificationDropdown";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { User as UserIcon, LogOut, ChevronDown, Map, Compass, UsersRound, Navigation, ShieldAlert, Footprints } from "lucide-react";

const navItems = [
  { to: "/community", label: "Community", menuLabel: "Community Explore", icon: Map },
  { to: "/social-map", label: "Social Map", menuLabel: "Social Map", icon: Map },
  { to: "/buddy-matching", label: "Buddy Matching", menuLabel: "Buddy Matching", icon: UsersRound },
  { to: "/planner", label: "AI Planner", menuLabel: "AI Planner", icon: Compass },
  { to: "/trips", label: "Group Trips", menuLabel: "Group Trips", icon: UsersRound },
  { to: "/route-optimizer", label: "Route Optimizer", menuLabel: "Route Optimizer", icon: Navigation },
  { to: "/emergency", label: "Emergency", menuLabel: "Emergency Hub", icon: ShieldAlert },
  { to: "/transit-blueprints", label: "Transit Blueprints", menuLabel: "Transit Blueprints", icon: Footprints },
];

function UserAvatar({
  name,
  pictureUrl,
  sizeClass,
  iconSize,
}: {
  name: string;
  pictureUrl?: string | null;
  sizeClass: string;
  iconSize: number;
}) {
  return (
    <div className={`${sizeClass} rounded-full overflow-hidden border bg-muted shrink-0`}>
      {pictureUrl ? (
        <img src={pictureUrl} alt={name} className="h-full w-full object-cover" />
      ) : (
        <div className="h-full w-full flex items-center justify-center bg-primary/10 text-primary">
          <UserIcon size={iconSize} />
        </div>
      )}
    </div>
  );
}

export default function Navbar() {
  const { user, isAuthenticated, isLoading } = useAuth();

  return (
    <nav className="sticky top-0 z-40 w-full border-b bg-background/95 backdrop-blur-sm supports-backdrop-filter:bg-background/60">
      <div className="container mx-auto px-4 h-16 flex items-center justify-between">
        <div className="flex items-center gap-8">
          <Link to="/" className="flex items-center gap-2">
            <div className="bg-green-600 p-1.5 rounded-lg text-white">
              <Compass size={20} strokeWidth={2.5} />
            </div>
            <span className="font-bold text-xl tracking-tight text-green-700 hidden sm:inline-block">
              Bangla Trek
            </span>
          </Link>

          <div className="hidden md:flex items-center gap-1">
            {navItems.map(({ to, label, icon: Icon }) => (
              <Button
                key={to}
                variant="ghost"
                render={<Link to={to} activeProps={{ className: "text-foreground bg-muted" }} />}
                className="font-medium text-muted-foreground hover:text-foreground"
              >
                <Icon size={16} className="mr-2" />
                {label}
              </Button>
            ))}
          </div>
        </div>

        <div className="flex items-center gap-3">
          {isLoading ? (
            <div className="h-8 w-24 bg-muted animate-pulse rounded-lg" />
          ) : isAuthenticated && user ? (
            <>
              <NotificationDropdown />
              <DropdownMenu>

              <DropdownMenuTrigger render={<Button variant="ghost" className="relative flex items-center gap-2 pr-1 h-10 rounded-full hover:bg-muted" />}>
                <UserAvatar name={user.name} pictureUrl={user.picture_url} sizeClass="h-7 w-7" iconSize={14} />
                <span className="text-sm font-medium hidden sm:inline-block max-w-[100px] truncate">
                  {user.name.split(' ')[0]}
                </span>
                <ChevronDown size={14} className="text-muted-foreground" />
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-56 mt-1">
                <div className="flex items-center gap-2 p-2 px-3 border-b mb-1">
                  <UserAvatar name={user.name} pictureUrl={user.picture_url} sizeClass="h-9 w-9" iconSize={16} />
                  <div className="flex flex-col overflow-hidden">
                    <span className="text-sm font-semibold truncate">{user.name}</span>
                    <span className="text-xs text-muted-foreground truncate">{user.email}</span>
                  </div>
                </div>
                {navItems.map(({ to, menuLabel }) => (
                  <DropdownMenuItem key={to} render={<Link to={to} className="w-full" />}>
                    {menuLabel}
                  </DropdownMenuItem>
                ))}
                <DropdownMenuItem onClick={logout} variant="destructive">
                  <LogOut size={16} className="mr-2" />
                  Logout
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
            </>
          ) : (
            <Button onClick={loginWithGoogle} size="sm" className="rounded-full px-5">
              Login
            </Button>
          )}
        </div>
      </div>
    </nav>
  );
}
