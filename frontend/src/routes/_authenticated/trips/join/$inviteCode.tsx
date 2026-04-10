import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  invitePreviewQueryOptions,
  joinGroupTrip,
} from "@/services/group-trip.service";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { toast } from "sonner";
import {
  MapPin,
  Calendar,
  Users,
  Globe,
  Lock,
  Loader2,
  UsersRound,
  ArrowLeft,
} from "lucide-react";
import { Link } from "@tanstack/react-router";

export const Route = createFileRoute(
  "/_authenticated/trips/join/$inviteCode"
)({
  component: JoinTripPage,
});

function JoinTripPage() {
  const { inviteCode } = Route.useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const {
    data: preview,
    isLoading,
    error,
  } = useQuery(invitePreviewQueryOptions(inviteCode));

  const joinMutation = useMutation({
    mutationFn: () => joinGroupTrip(inviteCode),
    onSuccess: (data) => {
      toast.success("You've joined the trip!");
      queryClient.invalidateQueries({ queryKey: ["group-trips"] });
      navigate({ to: "/trips/$tripId", params: { tripId: data.id } });
    },
    onError: (error: any) => {
      const detail = error?.response?.data?.detail || "";
      if (detail.includes("Already a member")) {
        toast.info("You're already a member of this trip.");
        if (preview) {
          navigate({ to: "/trips/$tripId", params: { tripId: preview.id } });
        }
      } else {
        toast.error(detail || "Failed to join trip.");
      }
    },
  });

  if (isLoading) {
    return (
      <div className="container mx-auto py-16 px-4 max-w-lg">
        <Skeleton className="h-64 rounded-xl" />
      </div>
    );
  }

  if (error || !preview) {
    return (
      <div className="container mx-auto py-16 px-4 text-center space-y-4">
        <h1 className="text-2xl font-bold">Invalid Invite Link</h1>
        <p className="text-muted-foreground">
          This invite link is invalid or has expired.
        </p>
        <Button variant="outline" render={<Link to="/trips" />}>
          <ArrowLeft className="mr-2 h-4 w-4" />
          Browse Trips
        </Button>
      </div>
    );
  }

  const startDate = new Date(preview.start_date).toLocaleDateString("en-GB", {
    day: "numeric",
    month: "long",
    year: "numeric",
  });
  const endDate = new Date(preview.end_date).toLocaleDateString("en-GB", {
    day: "numeric",
    month: "long",
    year: "numeric",
  });

  return (
    <div className="container mx-auto py-16 px-4 max-w-lg space-y-6">
      <div className="text-center space-y-2">
        <UsersRound className="h-12 w-12 mx-auto text-primary" />
        <h1 className="text-2xl font-bold">You're invited!</h1>
        <p className="text-muted-foreground">
          You've been invited to join a group trip.
        </p>
      </div>

      <Card className="p-6 space-y-4">
        <div className="h-2 -mt-6 -mx-6 mb-4 bg-gradient-to-r from-green-500 to-emerald-400 rounded-t-xl" />

        <div className="flex items-start justify-between gap-3">
          <h2 className="text-xl font-bold">{preview.title}</h2>
          <Badge
            variant={preview.visibility === "public" ? "secondary" : "outline"}
          >
            {preview.visibility === "public" ? (
              <Globe size={12} className="mr-1" />
            ) : (
              <Lock size={12} className="mr-1" />
            )}
            {preview.visibility}
          </Badge>
        </div>

        <div className="flex items-center gap-1.5 text-muted-foreground">
          <MapPin size={16} />
          <span>{preview.destination}</span>
        </div>

        {preview.description && (
          <p className="text-sm text-muted-foreground">
            {preview.description}
          </p>
        )}

        <div className="flex flex-wrap gap-4 text-sm text-muted-foreground">
          <div className="flex items-center gap-1.5">
            <Calendar size={14} />
            <span>
              {startDate} - {endDate}
            </span>
          </div>
          <div className="flex items-center gap-1.5">
            <Users size={14} />
            <span>
              {preview.member_count} member
              {preview.member_count !== 1 ? "s" : ""}
            </span>
          </div>
        </div>

        <div className="flex items-center gap-2 text-sm text-muted-foreground pt-2 border-t">
          {preview.creator_picture_url ? (
            <img
              src={preview.creator_picture_url}
              alt={preview.creator_name}
              className="h-5 w-5 rounded-full"
            />
          ) : null}
          <span>Created by {preview.creator_name}</span>
        </div>

        <Button
          className="w-full"
          onClick={() => joinMutation.mutate()}
          disabled={joinMutation.isPending}
        >
          {joinMutation.isPending ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Joining...
            </>
          ) : (
            <>
              <UsersRound className="mr-2 h-4 w-4" />
              Join This Trip
            </>
          )}
        </Button>
      </Card>
    </div>
  );
}
