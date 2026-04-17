import { Calendar, Clock, Coins, MoreVertical, Trash2 } from "lucide-react";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import type { EntryReview, ReviewTravelStyle } from "@/types/review";
import { StarRating } from "./StarRating";

interface ReviewCardProps {
  review: EntryReview;
  canManage?: boolean;
  onDelete?: (reviewId: string) => void;
}

const styleLabels: Record<ReviewTravelStyle, string> = {
  budget: "Budget",
  luxury: "Luxury",
  adventure: "Adventure",
  family: "Family",
};

function formatTime(minutes: number | null) {
  if (!minutes) return null;
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  if (hours === 0) return `${mins}m`;
  if (mins === 0) return `${hours}h`;
  return `${hours}h ${mins}m`;
}

export function ReviewCard({ review, canManage, onDelete }: ReviewCardProps) {
  const initials = review.author_name
    .split(" ")
    .map((part) => part[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();
  const timeSpent = formatTime(review.time_spent_minutes);

  return (
    <Card className="p-5">
      <div className="flex items-start justify-between gap-4">
        <div className="flex min-w-0 items-start gap-3">
          <Avatar className="h-10 w-10 border">
            {review.author_picture_url && (
              <AvatarImage src={review.author_picture_url} alt={review.author_name} />
            )}
            <AvatarFallback>{initials || "BT"}</AvatarFallback>
          </Avatar>
          <div className="min-w-0 space-y-1">
            <div className="flex flex-wrap items-center gap-2">
              <p className="font-semibold">{review.author_name}</p>
              <Badge variant="secondary">
                {styleLabels[review.travel_style]}
              </Badge>
            </div>
            <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-muted-foreground">
              <span className="flex items-center gap-1">
                <Calendar size={12} />
                {new Date(review.created_at).toLocaleDateString(undefined, {
                  dateStyle: "medium",
                })}
              </span>
              {review.actual_cost_bdt != null && (
                <span className="flex items-center gap-1">
                  <Coins size={12} />
                  BDT {review.actual_cost_bdt.toLocaleString()}
                </span>
              )}
              {timeSpent && (
                <span className="flex items-center gap-1">
                  <Clock size={12} />
                  {timeSpent}
                </span>
              )}
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <StarRating value={review.rating} size="sm" />
          {canManage && (
            <DropdownMenu>
              <DropdownMenuTrigger
                render={<Button variant="ghost" size="icon-sm" />}
              >
                <MoreVertical size={16} />
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem
                  variant="destructive"
                  onClick={() => onDelete?.(review.id)}
                >
                  <Trash2 size={14} className="mr-2" />
                  Delete Review
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          )}
        </div>
      </div>

      <p className="whitespace-pre-wrap leading-relaxed text-foreground/80">
        {review.review_text}
      </p>

      {review.photos.length > 0 && (
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
          {review.photos.slice(0, 4).map((photo) => (
            <div
              key={photo.id}
              className="aspect-square overflow-hidden rounded-lg border bg-muted"
            >
              <img
                src={photo.url}
                alt={photo.caption || "Review photo"}
                className="h-full w-full object-cover transition-transform duration-300 hover:scale-105"
              />
            </div>
          ))}
        </div>
      )}
    </Card>
  );
}
