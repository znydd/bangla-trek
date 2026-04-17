import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import type { EntryReviewListParams, ReviewTravelStyle } from "@/types/review";

interface ReviewFiltersProps {
  filters: EntryReviewListParams;
  onChange: (filters: EntryReviewListParams) => void;
}

const travelStyles: { value: ReviewTravelStyle | "all"; label: string }[] = [
  { value: "all", label: "All" },
  { value: "budget", label: "Budget" },
  { value: "luxury", label: "Luxury" },
  { value: "adventure", label: "Adventure" },
  { value: "family", label: "Family" },
];

export function ReviewFilters({ filters, onChange }: ReviewFiltersProps) {
  return (
    <div className="flex flex-col gap-3 rounded-xl border border-border/50 bg-muted/30 p-4 sm:flex-row sm:items-center sm:justify-between">
      <div className="flex flex-wrap items-center gap-2">
        <span className="mr-1 text-sm font-medium text-muted-foreground">
          Travel style:
        </span>
        {travelStyles.map((style) => (
          <Button
            key={style.value}
            type="button"
            variant={
              (filters.travel_style || "all") === style.value
                ? "secondary"
                : "outline"
            }
            size="sm"
            onClick={() =>
              onChange({
                ...filters,
                travel_style:
                  style.value === "all" ? undefined : style.value,
                page: 1,
              })
            }
            className="rounded-full px-4"
          >
            {style.label}
          </Button>
        ))}
      </div>

      <Select
        value={filters.sort_by || "newest"}
        onValueChange={(value) =>
          onChange({
            ...filters,
            sort_by: value as EntryReviewListParams["sort_by"],
            page: 1,
          })
        }
      >
        <SelectTrigger className="w-full sm:w-[160px]">
          <SelectValue placeholder="Sort reviews" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="newest">Newest First</SelectItem>
          <SelectItem value="highest_rating">Highest Rated</SelectItem>
          <SelectItem value="lowest_rating">Lowest Rated</SelectItem>
        </SelectContent>
      </Select>
    </div>
  );
}
