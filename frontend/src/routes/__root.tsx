import {
  createRootRouteWithContext,
  Outlet,
} from "@tanstack/react-router";
import type { QueryClient } from "@tanstack/react-query";
import { useCallback, useState, type CSSProperties } from "react";
import { Toaster } from "@/components/ui/sonner";
import { SidebarProvider } from "@/components/ui/sidebar";
import Navbar from "@/components/layout/Navbar";
import { GlobalAiChat } from "@/components/place/GlobalAiChat";

interface RouterContext {
  queryClient: QueryClient;
}

export const Route = createRootRouteWithContext<RouterContext>()({
  component: RootComponent,
});

function RootComponent() {
  const [aiOpen, setAiOpen] = useState(false);
  const [aiSidebarWidth, setAiSidebarWidth] = useState(440);
  const [aiSidebarResizing, setAiSidebarResizing] = useState(false);
  const handleAiOpenChange = useCallback((open: boolean) => {
    setAiOpen(open);
  }, []);

  return (
    <SidebarProvider
      open={aiOpen}
      onOpenChange={handleAiOpenChange}
      className={`bg-[#f7f7f2] font-sans antialiased ${
        aiSidebarResizing
          ? "[&_[data-slot=sidebar-container]]:!transition-none [&_[data-slot=sidebar-gap]]:!transition-none"
          : ""
      }`}
      style={
        {
          "--sidebar-width": `${aiSidebarWidth}px`,
          "--sidebar-width-mobile": "min(100vw, 28rem)",
        } as CSSProperties
      }
    >
      <div className="flex min-h-svh min-w-0 flex-1 flex-col">
        <Navbar />
        <main className="flex-1">
          <Outlet />
        </main>
        <footer className="border-t bg-muted/30 py-6 text-center text-sm text-muted-foreground">
          <p>© {new Date().getFullYear()} Bangla Trek. Smart Travel Itinerary Planner for Bangladesh.</p>
        </footer>
        <Toaster position="top-center" richColors />
      </div>
      <GlobalAiChat
        width={aiSidebarWidth}
        onWidthChange={setAiSidebarWidth}
        onResizeStateChange={setAiSidebarResizing}
      />
    </SidebarProvider>
  );
}
