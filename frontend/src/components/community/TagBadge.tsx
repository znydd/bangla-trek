import { Badge } from "@/components/ui/badge";
import { EntryTag } from "@/types/community";
import { cn } from "@/lib/utils";

interface TagBadgeProps {
  tag: EntryTag;
  className?: string;
}

export function TagBadge({ tag, className }: TagBadgeProps) {
  if (tag === "trending") {
    return (
      <Badge
        className={cn(
          "bg-orange-100 text-orange-700 border-orange-200 dark:bg-orange-900/30 dark:text-orange-400 dark:border-orange-800",
          className
        )}
      >
        Trending
      </Badge>
    );
  }

  if (tag === "hidden_gem") {
    return (
      <Badge
        className={cn(
          "bg-emerald-100 text-emerald-700 border-emerald-200 dark:bg-emerald-900/30 dark:text-emerald-400 dark:border-emerald-800",
          className
        )}
      >
        Hidden Gem
      </Badge>
    );
  }

  return null;
}
