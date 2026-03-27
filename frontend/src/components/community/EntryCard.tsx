import { Link } from "@tanstack/react-router";
import { Card, CardContent, CardFooter, CardHeader } from "@/components/ui/card";
import { CommunityEntry, PriceRange } from "@/types/community";
import { TagBadge } from "./TagBadge";
import { CategoryIcon, getCategoryLabel } from "./CategoryIcon";
import { MapPin } from "lucide-react";

interface EntryCardProps {
  entry: CommunityEntry;
}

export function getPriceRangeLabel(priceRange: PriceRange) {
  switch (priceRange) {
    case "budget":
      return "$ Budget";
    case "mid_range":
      return "$$ Mid-range";
    case "premium":
      return "$$$ Premium";
    case "luxury":
      return "$$$$ Luxury";
    default:
      return priceRange;
  }
}

export function EntryCard({ entry }: EntryCardProps) {
  const firstPhoto = entry.photos.length > 0 ? entry.photos[0].url : null;

  return (
    <Link to="/community/$entryId" params={{ entryId: entry.id }} className="block group">
      <Card className="overflow-hidden h-full transition-all hover:shadow-md border-border/50 group-hover:border-primary/20">
        <div className="aspect-video w-full overflow-hidden bg-muted">
          {firstPhoto ? (
            <img
              src={firstPhoto}
              alt={entry.name}
              className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
            />
          ) : (
            <div className="flex h-full w-full items-center justify-center text-muted-foreground/40">
              <CategoryIcon category={entry.category} size={48} strokeWidth={1} />
            </div>
          )}
        </div>
        <CardHeader className="p-4 pb-2">
          <div className="flex items-start justify-between gap-2">
            <h3 className="font-semibold text-lg leading-tight group-hover:text-primary transition-colors line-clamp-1">
              {entry.name}
            </h3>
            <div className="flex gap-1 shrink-0">
              {entry.tags.map((tag) => (
                <TagBadge key={tag} tag={tag} />
              ))}
            </div>
          </div>
          <div className="flex items-center gap-1.5 text-sm text-muted-foreground">
            <MapPin size={14} className="shrink-0" />
            <span className="line-clamp-1">{entry.location}</span>
          </div>
        </CardHeader>
        <CardContent className="p-4 pt-0 pb-2">
          <div className="flex items-center gap-2 text-xs font-medium">
            <div className="flex items-center gap-1 bg-secondary/50 px-2 py-0.5 rounded-full">
              <CategoryIcon category={entry.category} size={12} />
              <span>{getCategoryLabel(entry.category)}</span>
            </div>
            <span className="text-muted-foreground">•</span>
            <span>{getPriceRangeLabel(entry.price_range)}</span>
          </div>
        </CardContent>
        <CardFooter className="p-4 pt-0 text-xs text-muted-foreground flex justify-between items-center">
          <span className="line-clamp-1">by {entry.author_name}</span>
          <span>{new Date(entry.created_at).toLocaleDateString()}</span>
        </CardFooter>
      </Card>
    </Link>
  );
}
