import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { EntryCategory, EntryTag, CommunityEntryListParams } from "@/types/community";
import { Search, X } from "lucide-react";
import { getCategoryLabel } from "./CategoryIcon";

interface EntryFiltersProps {
  filters: CommunityEntryListParams;
  onChange: (filters: CommunityEntryListParams) => void;
}

export function EntryFilters({ filters, onChange }: EntryFiltersProps) {
  const categories: (EntryCategory | "all")[] = [
    "all",
    "attraction",
    "hotel",
    "guesthouse",
    "homestay",
    "restaurant",
  ];

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onChange({ ...filters, search: e.target.value, page: 1 });
  };

  const handleCategoryChange = (value: string | null) => {
    if (!value) return;
    onChange({
      ...filters,
      category: value === "all" ? undefined : (value as EntryCategory),
      page: 1,
    });
  };

  const handleTagChange = (tag: EntryTag | "all") => {
    onChange({
      ...filters,
      tag: tag === "all" ? undefined : tag,
      page: 1,
    });
  };

  const handleSortChange = (value: string | null) => {
    if (!value) return;
    onChange({ ...filters, sort_by: value as "newest" | "name", page: 1 });
  };

  const clearFilters = () => {
    onChange({ page: 1, per_page: filters.per_page });
  };

  const hasActiveFilters = 
    filters.category || 
    filters.tag || 
    (filters.search && filters.search.length > 0) || 
    filters.sort_by;

  return (
    <div className="flex flex-col gap-4 bg-muted/30 p-4 rounded-xl border border-border/50">
      <div className="flex flex-col md:flex-row gap-4">
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
          <Select
            value={filters.category || "all"}
            onValueChange={handleCategoryChange}
          >
            <SelectTrigger className="w-[160px]">
              <SelectValue placeholder="Category" />
            </SelectTrigger>
            <SelectContent>
              {categories.map((cat) => (
                <SelectItem key={cat} value={cat}>
                  {cat === "all" ? "All Categories" : getCategoryLabel(cat)}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Select
            value={filters.sort_by || "newest"}
            onValueChange={handleSortChange}
          >
            <SelectTrigger className="w-[140px]">
              <SelectValue placeholder="Sort by" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="newest">Newest First</SelectItem>
              <SelectItem value="name">Name A-Z</SelectItem>
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

      <div className="flex flex-wrap items-center gap-2">
        <span className="text-sm font-medium text-muted-foreground mr-2">Tags:</span>
        <Button
          variant={!filters.tag ? "secondary" : "outline"}
          size="sm"
          onClick={() => handleTagChange("all")}
          className="rounded-full px-4 h-8"
        >
          All
        </Button>
        <Button
          variant={filters.tag === "trending" ? "secondary" : "outline"}
          size="sm"
          onClick={() => handleTagChange("trending")}
          className="rounded-full px-4 h-8"
        >
          Trending
        </Button>
        <Button
          variant={filters.tag === "hidden_gem" ? "secondary" : "outline"}
          size="sm"
          onClick={() => handleTagChange("hidden_gem")}
          className="rounded-full px-4 h-8"
        >
          Hidden Gem
        </Button>
      </div>
    </div>
  );
}
