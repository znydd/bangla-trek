import { createRootRouteWithContext, Outlet } from "@tanstack/react-router";
import type { QueryClient } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/sonner";
import Navbar from "@/components/layout/Navbar";

interface RouterContext {
  queryClient: QueryClient;
}

export const Route = createRootRouteWithContext<RouterContext>()({
  component: RootComponent,
});

function RootComponent() {
  return (
    <div className="min-h-screen flex flex-col font-sans antialiased">
      <Navbar />
      <main className="flex-1">
        <Outlet />
      </main>
      <footer className="border-t py-6 text-center text-sm text-muted-foreground bg-muted/30">
        <p>© {new Date().getFullYear()} Bangla Trek. Smart Travel Itinerary Planner for Bangladesh.</p>
      </footer>
      <Toaster position="top-center" richColors />
    </div>
  );
}
