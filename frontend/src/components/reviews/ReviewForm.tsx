import { useState } from "react";
import { Clock, Coins, Loader2, MessageSquare } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import type { CreateReviewPayload, ReviewTravelStyle } from "@/types/review";
import { ReviewPhotoUploader } from "./ReviewPhotoUploader";
import { StarRating } from "./StarRating";

interface ReviewFormProps {
  onSubmit: (payload: CreateReviewPayload, photos: File[]) => Promise<void>;
  isLoading?: boolean;
}

export function ReviewForm({ onSubmit, isLoading }: ReviewFormProps) {
  const [payload, setPayload] = useState<CreateReviewPayload>({
    rating: 5,
    travel_style: "budget",
    actual_cost_bdt: null,
    time_spent_minutes: null,
    review_text: "",
  });
  const [photos, setPhotos] = useState<File[]>([]);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    await onSubmit(payload, photos);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="space-y-2">
        <Label>Star Rating</Label>
        <div className="flex items-center gap-3">
          <StarRating
            value={payload.rating}
            onChange={(rating) => setPayload((prev) => ({ ...prev, rating }))}
            size="lg"
          />
          <span className="text-sm font-medium text-muted-foreground">
            {payload.rating} / 5
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <div className="space-y-2">
          <Label>Travel Style</Label>
          <Select
            value={payload.travel_style}
            onValueChange={(value) =>
              setPayload((prev) => ({
                ...prev,
                travel_style: value as ReviewTravelStyle,
              }))
            }
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="budget">Budget</SelectItem>
              <SelectItem value="luxury">Luxury</SelectItem>
              <SelectItem value="adventure">Adventure</SelectItem>
              <SelectItem value="family">Family</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label htmlFor="actual-cost" className="flex items-center gap-1.5">
            <Coins size={14} />
            Actual Cost
          </Label>
          <Input
            id="actual-cost"
            type="number"
            min={0}
            step={50}
            placeholder="BDT"
            value={payload.actual_cost_bdt ?? ""}
            onChange={(event) =>
              setPayload((prev) => ({
                ...prev,
                actual_cost_bdt: event.target.value
                  ? Number(event.target.value)
                  : null,
              }))
            }
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="time-spent" className="flex items-center gap-1.5">
            <Clock size={14} />
            Time Spent
          </Label>
          <Input
            id="time-spent"
            type="number"
            min={0}
            step={15}
            placeholder="Minutes"
            value={payload.time_spent_minutes ?? ""}
            onChange={(event) =>
              setPayload((prev) => ({
                ...prev,
                time_spent_minutes: event.target.value
                  ? Number(event.target.value)
                  : null,
              }))
            }
          />
        </div>
      </div>

      <div className="space-y-2">
        <Label htmlFor="review-text" className="flex items-center gap-1.5">
          <MessageSquare size={14} />
          Detailed Review
        </Label>
        <Textarea
          id="review-text"
          required
          rows={5}
          className="resize-none"
          placeholder="Share what future travelers should know..."
          value={payload.review_text}
          onChange={(event) =>
            setPayload((prev) => ({
              ...prev,
              review_text: event.target.value,
            }))
          }
        />
      </div>

      <ReviewPhotoUploader
        disabled={isLoading}
        onPhotosChange={setPhotos}
      />

      <div className="flex justify-end">
        <Button
          type="submit"
          size="lg"
          disabled={isLoading || payload.review_text.trim().length === 0}
        >
          {isLoading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Publishing...
            </>
          ) : (
            "Publish Review"
          )}
        </Button>
      </div>
    </form>
  );
}
