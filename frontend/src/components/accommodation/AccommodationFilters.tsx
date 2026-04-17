import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import type { AccommodationSearchParams, AccommodationType } from "@/types/accommodation";
import { Search, X, Hotel, Building2, Home } from "lucide-react";

interface AccommodationFiltersProps {
  filters: AccommodationSearchParams;
  onChange: (filters: AccommodationSearchParams) => void;
}

const ACCOMMODATION_TYPES: { value: AccommodationType | "all"; label: string; icon: React.ReactNode }[] = [
  { value: "all", label: "All Types", icon: null },
  { value: "hotel", label: "Hotel", icon: <Hotel size={14} /> },
  { value: "guesthouse", label: "Guesthouse", icon: <Building2 size={14} /> },
  { value: "homestay", label: "Homestay", icon: <Home size={14} /> },
];

const PRICE_RANGES = [
  { value: "all", label: "Any Budget" },
  { value: "budget", label: "$ Budget" },
  { value: "mid_range", label: "$$ Mid-range" },
  { value: "premium", label: "$$$ Premium" },
  { value: "luxury", label: "$$$$ Luxury" },
];

export function AccommodationFilters({ filters, onChange }: AccommodationFiltersProps) {
  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onChange({ ...filters, search: e.target.value, page: 1 });
  };

  const handleTypeChange = (value: string | null) => {
    if (!value) return;
    onChange({
      ...filters,
      accommodation_type: value === "all" ? undefined : (value as AccommodationType),
      page: 1,
    });
  };

  const handlePriceChange = (value: string | null) => {
    if (!value) return;
    onChange({
      ...filters,
      price_range: value === "all" ? undefined : value,
      page: 1,
    });
  };

  const handleSortChange = (value: string | null) => {
    if (!value) return;
    onChange({
      ...filters,
      sort_by: value as AccommodationSearchParams["sort_by"],
      page: 1,
    });
  };

  const clearFilters = () => {
    onChange({ page: 1, per_page: filters.per_page });
  };

  const hasActiveFilters =
    filters.accommodation_type ||
    filters.price_range ||
    (filters.search && filters.search.length > 0) ||
    (filters.sort_by && filters.sort_by !== "newest");

  return (
    <div className="flex flex-col gap-4 bg-muted/30 p-4 rounded-xl border border-border/50">
      <div className="flex flex-col md:flex-row gap-4">
        {/* Search */}
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search by name or location..."
            value={filters.search || ""}
            onChange={handleSearchChange}
            className="pl-10"
          />
        </div>
        <div className="flex flex-wrap gap-2">
          {/* Price Range */}
          <Select
            value={filters.price_range || "all"}
            onValueChange={handlePriceChange}
          >
            <SelectTrigger className="w-[160px]">
              <SelectValue placeholder="Budget" />
            </SelectTrigger>
            <SelectContent>
              {PRICE_RANGES.map((pr) => (
                <SelectItem key={pr.value} value={pr.value}>
                  {pr.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          {/* Sort */}
          <Select
            value={filters.sort_by || "newest"}
            onValueChange={handleSortChange}
          >
            <SelectTrigger className="w-[160px]">
              <SelectValue placeholder="Sort by" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="newest">Newest First</SelectItem>
              <SelectItem value="name">Name A-Z</SelectItem>
              <SelectItem value="price_asc">Price: Low → High</SelectItem>
              <SelectItem value="price_desc">Price: High → Low</SelectItem>
            </SelectContent>
          </Select>

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

      {/* Type toggle buttons */}
      <div className="flex flex-wrap items-center gap-2">
        <span className="text-sm font-medium text-muted-foreground mr-2">Type:</span>
        {ACCOMMODATION_TYPES.map((type) => (
          <Button
            key={type.value}
            variant={
              (filters.accommodation_type || "all") === type.value
                ? "secondary"
                : "outline"
            }
            size="sm"
            onClick={() => handleTypeChange(type.value)}
            className="rounded-full px-4 h-8 gap-1.5"
          >
            {type.icon}
            {type.label}
          </Button>
        ))}
      </div>
    </div>
  );
}
