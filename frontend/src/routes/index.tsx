import { createFileRoute, Link } from "@tanstack/react-router";
import { currentUserQueryOptions, loginWithGoogle } from "@/services/auth.service";
import { Button } from "@/components/ui/button";
import { Compass, Map, ShieldCheck, Zap } from "lucide-react";

export const Route = createFileRoute("/")({
  beforeLoad: async ({ context }) => {
    // Check if user is already authenticated
    try {
      const user = await context.queryClient.ensureQueryData(currentUserQueryOptions);
      if (user) {
        // If logged in, maybe we stay on landing but with different CTA
        // or redirect to a dashboard. For now, let's keep it simple.
      }
    } catch {
      // Not logged in, that's fine for the landing page
    }
  },
  component: HomePage,
});

function HomePage() {
  return (
    <div className="flex flex-col min-h-[80vh]">
      {/* Hero Section */}
      <section className="flex-1 flex flex-col items-center justify-center text-center px-4 py-20 bg-linear-to-b from-green-50 to-white dark:from-green-950/20 dark:to-background">
        <div className="inline-flex items-center gap-2 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 px-4 py-1.5 rounded-full text-sm font-semibold mb-6 animate-fade-in">
          <Zap size={16} />
          <span>AI-Powered Itinerary Planner</span>
        </div>
        
        <h1 className="text-5xl md:text-7xl font-bold tracking-tight mb-6 bg-linear-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">
          Discover the Soul of <br className="hidden md:block" /> Bangladesh
        </h1>
        
        <p className="max-w-2xl text-lg md:text-xl text-muted-foreground mb-10 leading-relaxed">
          Plan your perfect trip with AI-powered itineraries, community-sourced hidden gems, 
          and real-time collaboration. Your adventure starts here.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 items-center">
          <Button size="lg" onClick={loginWithGoogle} className="rounded-full px-8 h-12 text-base font-semibold shadow-lg shadow-green-600/20">
            Start Planning Now
          </Button>
          <Button size="lg" variant="outline" render={<Link to="/community" />} className="rounded-full px-8 h-12 text-base font-semibold">
            <Map size={18} className="mr-2" />
            Explore Community
          </Button>
        </div>

        <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl w-full">
          <div className="p-6 rounded-2xl border bg-card text-left space-y-3">
            <div className="bg-primary/10 w-10 h-10 rounded-lg flex items-center justify-center text-primary">
              <Compass size={24} />
            </div>
            <h3 className="font-bold text-lg">AI Itineraries</h3>
            <p className="text-sm text-muted-foreground">Smart, personalized travel plans tailored to your budget and preferences.</p>
          </div>
          <div className="p-6 rounded-2xl border bg-card text-left space-y-3">
            <div className="bg-primary/10 w-10 h-10 rounded-lg flex items-center justify-center text-primary">
              <Map size={24} />
            </div>
            <h3 className="font-bold text-lg">Hidden Gems</h3>
            <p className="text-sm text-muted-foreground">Discover underrated locations shared by local experts and fellow travelers.</p>
          </div>
          <div className="p-6 rounded-2xl border bg-card text-left space-y-3">
            <div className="bg-primary/10 w-10 h-10 rounded-lg flex items-center justify-center text-primary">
              <ShieldCheck size={24} />
            </div>
            <h3 className="font-bold text-lg">Verified Data</h3>
            <p className="text-sm text-muted-foreground">Crowd-sourced infrastructure ratings, safety metrics, and local transport fares.</p>
          </div>
        </div>
      </section>
    </div>
  );
}
