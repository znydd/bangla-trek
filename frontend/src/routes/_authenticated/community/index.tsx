import { createFileRoute } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { communityEntriesQueryOptions } from "@/services/community.service";
import { EntryFilters } from "@/components/community/EntryFilters";
import { EntryGrid } from "@/components/community/EntryGrid";
import { CommunityEntryListParams, EntryCategory, EntryTag } from "@/types/community";
import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";
import { Link } from "@tanstack/react-router";

export const Route = createFileRoute("/_authenticated/community/")({
  validateSearch: (search: Record<string, unknown>): CommunityEntryListParams => {
    return {
      page: Number(search?.page) || 1,
      per_page: Number(search?.per_page) || 12,
      category: search?.category as EntryCategory | undefined,
      tag: search?.tag as EntryTag | undefined,
      search: search?.search as string | undefined,
      sort_by: search?.sort_by as "newest" | "name" | undefined,
    };
  },
  component: CommunityListingPage,
});

function CommunityListingPage() {
  const searchParams = Route.useSearch();
  const navigate = Route.useNavigate();

  const { data, isLoading } = useQuery(
    communityEntriesQueryOptions(searchParams)
  );

  const handleFilterChange = (newFilters: CommunityEntryListParams) => {
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
          <h1 className="text-3xl font-bold tracking-tight">Community Travel Data</h1>
          <p className="text-muted-foreground mt-1">
            Discover and contribute travel insights from fellow explorers.
          </p>
        </div>
        <Button render={<Link to="/community/new" />}>
          <Plus className="mr-2 h-4 w-4" />
          Add Entry
        </Button>
      </div>

      <EntryFilters filters={searchParams} onChange={handleFilterChange} />

      <EntryGrid
        data={data}
        isLoading={isLoading}
        onPageChange={handlePageChange}
      />
    </div>
  );
}
