import { createFileRoute } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { transitBlueprintsQueryOptions } from "@/services/transit-blueprint.service";
import { BlueprintFilters } from "@/components/transit-blueprints/BlueprintFilters";
import { BlueprintCard } from "@/components/transit-blueprints/BlueprintCard";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Plus, ChevronLeft, ChevronRight } from "lucide-react";
import { Link } from "@tanstack/react-router";
import type { TransitBlueprintSearchParams } from "@/types/transit-blueprint";

export const Route = createFileRoute("/_authenticated/transit-blueprints/")({
  validateSearch: (
    search: Record<string, unknown>,
  ): TransitBlueprintSearchParams => {
    return {
      page: Number(search?.page) || 1,
      per_page: Number(search?.per_page) || 12,
      search: search?.search as string | undefined,
      origin: search?.origin as string | undefined,
      destination: search?.destination as string | undefined,
    };
  },
  component: TransitBlueprintsListPage,
});

function TransitBlueprintsListPage() {
  const searchParams = Route.useSearch();
  const navigate = Route.useNavigate();

  const { data, isLoading } = useQuery(
    transitBlueprintsQueryOptions(searchParams),
  );

  const handleFilterChange = (newFilters: TransitBlueprintSearchParams) => {
    navigate({
      search: (prev) => ({
        ...prev,
        ...newFilters,
      }),
    });
  };

  const handlePageChange = (page: number) => {
    handleFilterChange({ ...searchParams, page });
  };

  return (
    <div className="container mx-auto py-8 px-4 space-y-8">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">
            Transit Blueprints
          </h1>
          <p className="text-muted-foreground mt-1">
            Community-written step-by-step routes for hard-to-reach places where
            standard maps fail.
          </p>
        </div>
        <Button render={<Link to="/transit-blueprints/new" />}>
          <Plus className="mr-2 h-4 w-4" />
          Add Blueprint
        </Button>
      </div>

      <BlueprintFilters filters={searchParams} onChange={handleFilterChange} />

      {/* Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-[180px] rounded-xl" />
          ))}
        </div>
      ) : data && data.items.length > 0 ? (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {data.items.map((blueprint) => (
              <BlueprintCard key={blueprint.id} blueprint={blueprint} />
            ))}
          </div>

          {/* Pagination */}
          {data.total_pages > 1 && (
            <div className="flex items-center justify-center gap-4 pt-4">
              <Button
                variant="outline"
                size="sm"
                onClick={() => handlePageChange(data.page - 1)}
                disabled={data.page <= 1}
              >
                <ChevronLeft className="h-4 w-4 mr-1" />
                Previous
              </Button>
              <span className="text-sm text-muted-foreground">
                Page {data.page} of {data.total_pages}
              </span>
              <Button
                variant="outline"
                size="sm"
                onClick={() => handlePageChange(data.page + 1)}
                disabled={data.page >= data.total_pages}
              >
                Next
                <ChevronRight className="h-4 w-4 ml-1" />
              </Button>
            </div>
          )}
        </>
      ) : (
        <div className="text-center py-20">
          <h2 className="text-xl font-semibold mb-2">No blueprints yet</h2>
          <p className="text-muted-foreground mb-6">
            Be the first to contribute a transit blueprint for fellow travelers!
          </p>
          <Button render={<Link to="/transit-blueprints/new" />}>
            <Plus className="mr-2 h-4 w-4" />
            Add Blueprint
          </Button>
        </div>
      )}
    </div>
  );
}
