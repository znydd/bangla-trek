import { CommunityEntry, PaginatedResponse } from "@/types/community";
import { EntryCard } from "./EntryCard";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { ChevronLeft, ChevronRight, Inbox } from "lucide-react";

interface EntryGridProps {
  data?: PaginatedResponse<CommunityEntry>;
  isLoading: boolean;
  onPageChange: (page: number) => void;
}

export function EntryGrid({ data, isLoading, onPageChange }: EntryGridProps) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="flex flex-col space-y-3">
            <Skeleton className="h-[200px] w-full rounded-xl" />
            <div className="space-y-2">
              <Skeleton className="h-4 w-[250px]" />
              <Skeleton className="h-4 w-[200px]" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (!data || data.items.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-muted-foreground bg-muted/20 rounded-2xl border-2 border-dashed border-border/50">
        <Inbox size={48} strokeWidth={1} className="mb-4 opacity-20" />
        <h3 className="text-xl font-medium">No entries found</h3>
        <p className="text-sm">Try adjusting your filters or search terms.</p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {data.items.map((entry) => (
          <EntryCard key={entry.id} entry={entry} />
        ))}
      </div>

      {data.total_pages > 1 && (
        <div className="flex items-center justify-center gap-4 py-4">
          <Button
            variant="outline"
            size="sm"
            onClick={() => onPageChange(data.page - 1)}
            disabled={data.page <= 1}
          >
            <ChevronLeft className="mr-2 h-4 w-4" />
            Previous
          </Button>
          <div className="flex items-center gap-1">
            <span className="text-sm font-medium">Page {data.page}</span>
            <span className="text-sm text-muted-foreground">of {data.total_pages}</span>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={() => onPageChange(data.page + 1)}
            disabled={data.page >= data.total_pages}
          >
            Next
            <ChevronRight className="ml-2 h-4 w-4" />
          </Button>
        </div>
      )}
    </div>
  );
}
