import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import type { TransitBlueprintSearchParams } from "@/types/transit-blueprint";
import { Search, X } from "lucide-react";

interface BlueprintFiltersProps {
  filters: TransitBlueprintSearchParams;
  onChange: (filters: TransitBlueprintSearchParams) => void;
}

export function BlueprintFilters({ filters, onChange }: BlueprintFiltersProps) {
  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onChange({ ...filters, search: e.target.value, page: 1 });
  };

  const handleOriginChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onChange({ ...filters, origin: e.target.value, page: 1 });
  };

  const handleDestinationChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onChange({ ...filters, destination: e.target.value, page: 1 });
  };

  const clearFilters = () => {
    onChange({ page: 1, per_page: filters.per_page });
  };

  const hasActiveFilters =
    (filters.search && filters.search.length > 0) ||
    (filters.origin && filters.origin.length > 0) ||
    (filters.destination && filters.destination.length > 0);

  return (
    <div className="flex flex-col gap-4 bg-muted/30 p-4 rounded-xl border border-border/50">
      <div className="flex flex-col md:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search blueprints..."
            value={filters.search || ""}
            onChange={handleSearchChange}
            className="pl-10"
          />
        </div>
        <Input
          placeholder="Filter by origin..."
          value={filters.origin || ""}
          onChange={handleOriginChange}
          className="md:w-[200px]"
        />
        <Input
          placeholder="Filter by destination..."
          value={filters.destination || ""}
          onChange={handleDestinationChange}
          className="md:w-[200px]"
        />
        {hasActiveFilters && (
          <Button
            variant="ghost"
            size="sm"
            onClick={clearFilters}
            className="h-10 px-3 text-muted-foreground hover:text-foreground"
          >
            <X className="mr-2 h-4 w-4" />
            Clear
          </Button>
        )}
      </div>
    </div>
  );
}
