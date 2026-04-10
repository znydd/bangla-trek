import { useState } from "react";
import { createFileRoute, Link } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { itineraryQueryOptions } from "@/services/itinerary.service";
import { accommodationsQueryOptions } from "@/services/accommodation.service";
import { AccommodationCard } from "@/components/accommodation/AccommodationCard";
import { AccommodationFilters } from "@/components/accommodation/AccommodationFilters";
import { AIRecommendationStrip } from "@/components/accommodation/AIRecommendationStrip";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  ArrowLeft,
  BedDouble,
  Loader2,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import type { AccommodationSearchParams } from "@/types/accommodation";

export const Route = createFileRoute(
  "/_authenticated/planner/$itineraryId/accommodations/",
)({
  component: AccommodationsPage,
});

function AccommodationsPage() {
  const { itineraryId } = Route.useParams();
  const [filters, setFilters] = useState<AccommodationSearchParams>({
    page: 1,
    per_page: 12,
  });

  // Fetch the parent itinerary for context
  const { data: itinerary } = useQuery(itineraryQueryOptions(itineraryId));

  // Build search params — include destination as search context
  const searchParams: AccommodationSearchParams = {
    ...filters,
    search: filters.search || itinerary?.destination,
  };

  const { data: accommodationData, isLoading } = useQuery(
    accommodationsQueryOptions(searchParams),
  );

  const handleFilterChange = (newFilters: AccommodationSearchParams) => {
    setFilters(newFilters);
  };

  const handlePageChange = (newPage: number) => {
    setFilters((prev) => ({ ...prev, page: newPage }));
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  return (
    <div className="container mx-auto py-8 px-4 space-y-8">
      {/* Back navigation */}
      <Button
        variant="ghost"
        size="sm"
        render={
          <Link
            to="/planner/$itineraryId"
            params={{ itineraryId }}
          />
        }
      >
        <ArrowLeft className="mr-2 h-4 w-4" /> Back to Itinerary
      </Button>

      {/* Page header */}
      <div className="space-y-2">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-primary/10 rounded-xl">
            <BedDouble className="h-7 w-7 text-primary" />
          </div>
          <div>
            <h1 className="text-3xl font-bold tracking-tight">
              Accommodations
            </h1>
            {itinerary && (
              <p className="text-muted-foreground">
                Find the perfect stay for your {itinerary.duration_days}-day trip
                to{" "}
                <span className="font-medium text-foreground">
                  {itinerary.destination}
                </span>
              </p>
            )}
          </div>
        </div>
      </div>

      {/* AI Recommendations Section */}
      <AIRecommendationStrip itineraryId={itineraryId} />

      {/* Divider */}
      <div className="flex items-center gap-4">
        <div className="flex-1 h-px bg-border" />
        <span className="text-sm font-medium text-muted-foreground">
          Browse All Accommodations
        </span>
        <div className="flex-1 h-px bg-border" />
      </div>

      {/* Filters */}
      <AccommodationFilters filters={filters} onChange={handleFilterChange} />

      {/* Results count */}
      {accommodationData && (
        <div className="flex items-center justify-between text-sm text-muted-foreground">
          <span>
            Showing{" "}
            <span className="font-medium text-foreground">
              {accommodationData.items.length}
            </span>{" "}
            of{" "}
            <span className="font-medium text-foreground">
              {accommodationData.total}
            </span>{" "}
            accommodations
          </span>
          {accommodationData.total_pages > 1 && (
            <span>
              Page {accommodationData.page} of {accommodationData.total_pages}
            </span>
          )}
        </div>
      )}

      {/* Loading state */}
      {isLoading && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="space-y-3">
              <Skeleton className="aspect-[4/3] w-full rounded-xl" />
              <Skeleton className="h-5 w-3/4" />
              <Skeleton className="h-4 w-1/2" />
              <Skeleton className="h-4 w-full" />
            </div>
          ))}
        </div>
      )}

      {/* Results grid */}
      {accommodationData && (
        <>
          {accommodationData.items.length > 0 ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {accommodationData.items.map((acc) => (
                <AccommodationCard
                  key={acc.id}
                  accommodation={acc}
                  itineraryId={itineraryId}
                />
              ))}
            </div>
          ) : (
            <div className="text-center py-16 space-y-4">
              <BedDouble className="h-12 w-12 mx-auto text-muted-foreground/30" />
              <div>
                <h3 className="font-semibold text-lg">
                  No accommodations found
                </h3>
                <p className="text-muted-foreground text-sm max-w-md mx-auto mt-1">
                  Try adjusting your filters or search query. You can also
                  contribute accommodation data to help fellow travelers!
                </p>
              </div>
              <Button
                variant="outline"
                render={<Link to="/community/new" />}
              >
                Contribute Accommodation
              </Button>
            </div>
          )}

          {/* Pagination */}
          {accommodationData.total_pages > 1 && (
            <div className="flex items-center justify-center gap-2 pt-4">
              <Button
                variant="outline"
                size="sm"
                onClick={() =>
                  handlePageChange(accommodationData.page - 1)
                }
                disabled={accommodationData.page <= 1}
              >
                <ChevronLeft className="h-4 w-4 mr-1" /> Previous
              </Button>
              <div className="flex items-center gap-1">
                {Array.from(
                  { length: Math.min(accommodationData.total_pages, 5) },
                  (_, i) => {
                    const page = i + 1;
                    return (
                      <Button
                        key={page}
                        variant={
                          page === accommodationData.page
                            ? "default"
                            : "ghost"
                        }
                        size="sm"
                        className="w-9 h-9"
                        onClick={() => handlePageChange(page)}
                      >
                        {page}
                      </Button>
                    );
                  },
                )}
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={() =>
                  handlePageChange(accommodationData.page + 1)
                }
                disabled={
                  accommodationData.page >= accommodationData.total_pages
                }
              >
                Next <ChevronRight className="h-4 w-4 ml-1" />
              </Button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
