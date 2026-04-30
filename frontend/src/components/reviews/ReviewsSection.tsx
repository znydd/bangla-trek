import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Loader2, MessageSquarePlus, Star } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  createReview,
  deleteReview,
  entryReviewsQueryOptions,
  uploadReviewPhotos,
} from "@/services/review.service";
import type {
  CreateReviewPayload,
  EntryReviewListParams,
} from "@/types/review";
import { useAuth } from "@/hooks/useAuth";
import { ReviewCard } from "./ReviewCard";
import { ReviewFilters } from "./ReviewFilters";
import { ReviewForm } from "./ReviewForm";
import { StarRating } from "./StarRating";

interface ReviewsSectionProps {
  entryId: string;
  title?: string;
}

const emptySummary = {
  average_rating: null,
  review_count: 0,
  breakdown: { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0 },
  by_travel_style: [],
};

export function ReviewsSection({
  entryId,
  title = "Detailed Reviews",
}: ReviewsSectionProps) {
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const [filters, setFilters] = useState<EntryReviewListParams>({
    page: 1,
    per_page: 6,
    sort_by: "newest",
  });
  const [isDialogOpen, setIsDialogOpen] = useState(false);

  const query = useQuery(entryReviewsQueryOptions(entryId, filters));
  const data = query.data;
  const summary = data?.summary ?? emptySummary;
  const average = summary.average_rating;
  const reviewCount = summary.review_count;
  const canWriteReview = !data?.my_review_id;

  const createMutation = useMutation({
    mutationFn: async ({
      payload,
      photos,
    }: {
      payload: CreateReviewPayload;
      photos: File[];
    }) => {
      const review = await createReview(entryId, payload);
      if (photos.length > 0) {
        await uploadReviewPhotos(entryId, review.id, photos);
      }
      return review;
    },
    onSuccess: () => {
      toast.success("Review published.");
      setIsDialogOpen(false);
      queryClient.invalidateQueries({
        queryKey: ["community-entries", entryId, "reviews"],
      });
    },
    onError: (error: any) => {
      toast.error(
        error?.response?.data?.detail ||
          "Could not publish your review. The review API may not be ready yet.",
      );
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (reviewId: string) => deleteReview(entryId, reviewId),
    onSuccess: () => {
      toast.success("Review deleted.");
      queryClient.invalidateQueries({
        queryKey: ["community-entries", entryId, "reviews"],
      });
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail || "Could not delete review.");
    },
  });

  const handleSubmit = async (
    payload: CreateReviewPayload,
    photos: File[],
  ) => {
    await createMutation.mutateAsync({ payload, photos });
  };

  const showUnavailableState = query.isError;

  return (
    <section className="space-y-5">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <h2 className="text-2xl font-semibold">{title}</h2>
            <span className="rounded-full bg-primary/10 p-1.5 text-primary">
              <Star size={16} />
            </span>
          </div>
          <div className="flex flex-wrap items-center gap-3 text-sm text-muted-foreground">
            <div className="flex items-center gap-2">
              <span className="text-2xl font-bold text-foreground">
                {average != null ? average.toFixed(1) : "-"}
              </span>
              <StarRating value={average ?? 0} size="sm" />
            </div>
            <span>
              {reviewCount} review{reviewCount === 1 ? "" : "s"}
            </span>
          </div>
        </div>

        <Button
          type="button"
          onClick={() => setIsDialogOpen(true)}
          disabled={showUnavailableState || !canWriteReview}
        >
          <MessageSquarePlus className="mr-2 h-4 w-4" />
          {canWriteReview ? "Write Review" : "Review Added"}
        </Button>
      </div>

      {!showUnavailableState && (
        <ReviewFilters filters={filters} onChange={setFilters} />
      )}

      {query.isLoading && (
        <div className="flex items-center justify-center gap-3 rounded-xl border border-border/50 bg-muted/20 py-12 text-muted-foreground">
          <Loader2 className="h-5 w-5 animate-spin" />
          <span className="text-sm">Loading reviews...</span>
        </div>
      )}

      {showUnavailableState && (
        <div className="rounded-xl border border-dashed border-border bg-muted/20 p-6 text-sm text-muted-foreground">
          Detailed reviews are ready in the frontend, but the backend review API
          is not available yet.
        </div>
      )}

      {data && data.items.length === 0 && (
        <div className="rounded-xl border border-dashed border-border bg-muted/20 p-8 text-center">
          <MessageSquarePlus className="mx-auto mb-3 h-8 w-8 text-muted-foreground/40" />
          <h3 className="font-semibold">No detailed reviews yet</h3>
          <p className="mx-auto mt-1 max-w-md text-sm text-muted-foreground">
            Be the first to share actual cost, time spent, photos, and practical
            tips for future travelers.
          </p>
        </div>
      )}

      {data && data.items.length > 0 && (
        <div className="space-y-4">
          {data.items.map((review) => (
            <ReviewCard
              key={review.id}
              review={review}
              canManage={review.user_id === user?.id}
              onDelete={(reviewId) => deleteMutation.mutate(reviewId)}
            />
          ))}
        </div>
      )}

      {data && data.total_pages > 1 && (
        <div className="flex items-center justify-center gap-2">
          <Button
            variant="outline"
            size="sm"
            disabled={(filters.page ?? 1) <= 1}
            onClick={() =>
              setFilters((prev) => ({
                ...prev,
                page: Math.max((prev.page ?? 1) - 1, 1),
              }))
            }
          >
            Previous
          </Button>
          <span className="text-sm text-muted-foreground">
            Page {data.page} of {data.total_pages}
          </span>
          <Button
            variant="outline"
            size="sm"
            disabled={data.page >= data.total_pages}
            onClick={() =>
              setFilters((prev) => ({
                ...prev,
                page: (prev.page ?? 1) + 1,
              }))
            }
          >
            Next
          </Button>
        </div>
      )}

      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent className="max-h-[90vh] overflow-y-auto sm:max-w-2xl">
          <DialogHeader>
            <DialogTitle>Write a Detailed Review</DialogTitle>
            <DialogDescription>
              Add the trip details future travelers need: rating, actual cost,
              time spent, photos, and practical tips.
            </DialogDescription>
          </DialogHeader>
          <ReviewForm
            onSubmit={handleSubmit}
            isLoading={createMutation.isPending}
          />
        </DialogContent>
      </Dialog>
    </section>
  );
}
