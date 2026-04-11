import { createFileRoute, Link } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import {
  groupTripsQueryOptions,
  myGroupTripsQueryOptions,
} from "@/services/group-trip.service";
import { TripCard } from "@/components/trips/TripCard";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import type { GroupTripListParams } from "@/types/group-trip";
import { Plus, UsersRound, Globe, Compass } from "lucide-react";

type TripTab = "public" | "my";

export const Route = createFileRoute("/_authenticated/trips/")({
  validateSearch: (
    search: Record<string, unknown>
  ): GroupTripListParams & { tab?: TripTab } => ({
    page: Number(search?.page) || 1,
    per_page: Number(search?.per_page) || 12,
    tab: (search?.tab as TripTab) || "public",
  }),
  component: TripsListPage,
});

function TripsListPage() {
  const searchParams = Route.useSearch();
  const navigate = Route.useNavigate();
  const activeTab: TripTab = searchParams.tab || "public";

  const paginationParams: GroupTripListParams = {
    page: searchParams.page,
    per_page: searchParams.per_page,
  };

  const publicQuery = useQuery({
    ...groupTripsQueryOptions(paginationParams),
    enabled: activeTab === "public",
  });
  const myQuery = useQuery({
    ...myGroupTripsQueryOptions(paginationParams),
    enabled: activeTab === "my",
  });

  const data = activeTab === "public" ? publicQuery.data : myQuery.data;
  const isLoading =
    activeTab === "public" ? publicQuery.isLoading : myQuery.isLoading;

  const handleTabChange = (tab: TripTab) => {
    navigate({ search: { page: 1, per_page: searchParams.per_page, tab } });
  };

  const handlePageChange = (page: number) => {
    navigate({ search: (prev) => ({ ...prev, page }) });
  };

  return (
    <div className="container mx-auto py-8 px-4 space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <UsersRound className="h-7 w-7 text-primary" />
            <h1 className="text-3xl font-bold tracking-tight">Group Trips</h1>
          </div>
          <p className="text-muted-foreground mt-1">
            Plan together, travel together. Create or join group trips.
          </p>
        </div>
        <Button render={<Link to="/trips/new" />}>
          <Plus className="mr-2 h-4 w-4" />
          Create Trip
        </Button>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-1 p-1 rounded-lg bg-muted/50 w-fit">
        <button
          id="tab-public-trips"
          onClick={() => handleTabChange("public")}
          className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all ${
            activeTab === "public"
              ? "bg-background text-foreground shadow-sm"
              : "text-muted-foreground hover:text-foreground hover:bg-background/50"
          }`}
        >
          <Globe size={16} />
          All Public Trips
        </button>
        <button
          id="tab-my-trips"
          onClick={() => handleTabChange("my")}
          className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all ${
            activeTab === "my"
              ? "bg-background text-foreground shadow-sm"
              : "text-muted-foreground hover:text-foreground hover:bg-background/50"
          }`}
        >
          <Compass size={16} />
          My Trips
        </button>
      </div>

      {/* Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-64 rounded-xl" />
          ))}
        </div>
      ) : data?.items?.length > 0 ? (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {data.items.map((trip) => (
              <TripCard key={trip.id} trip={trip} />
            ))}
          </div>

          {/* Pagination */}
          {data.total_pages > 1 && (
            <div className="flex justify-center gap-2 pt-4">
              <Button
                variant="outline"
                size="sm"
                disabled={data.page <= 1}
                onClick={() => handlePageChange(data.page - 1)}
              >
                Previous
              </Button>
              <span className="flex items-center text-sm text-muted-foreground px-3">
                Page {data.page} of {data.total_pages}
              </span>
              <Button
                variant="outline"
                size="sm"
                disabled={data.page >= data.total_pages}
                onClick={() => handlePageChange(data.page + 1)}
              >
                Next
              </Button>
            </div>
          )}
        </>
      ) : (
        <div className="text-center py-20 space-y-4">
          <UsersRound className="h-16 w-16 mx-auto text-muted-foreground/30" />
          <div>
            <h2 className="text-xl font-semibold">
              {activeTab === "public"
                ? "No public trips yet"
                : "You haven't created or joined any trips yet"}
            </h2>
            <p className="text-muted-foreground mt-1">
              {activeTab === "public"
                ? "Be the first to create a public group trip!"
                : "Create your first group trip or join one via an invite link!"}
            </p>
          </div>
          <Button render={<Link to="/trips/new" />}>
            <Plus className="mr-2 h-4 w-4" />
            Create Trip
          </Button>
        </div>
      )}
    </div>
  );
}
