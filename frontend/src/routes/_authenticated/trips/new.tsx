import { useState } from "react";
import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  createGroupTrip,
  discoverOverlappingQueryOptions,
} from "@/services/group-trip.service";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { toast } from "sonner";
import {
  MapPin,
  Calendar,
  Globe,
  Lock,
  Loader2,
  UsersRound,
  Search,
  Users,
  ExternalLink,
} from "lucide-react";
import { Link } from "@tanstack/react-router";
import { DestinationCombobox } from "@/components/trips/DestinationCombobox";
import type { CreateGroupTripPayload } from "@/types/group-trip";

export const Route = createFileRoute("/_authenticated/trips/new")({
  component: NewTripPage,
});

function NewTripPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const [title, setTitle] = useState("");
  const [destination, setDestination] = useState("");
  const [description, setDescription] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [visibility, setVisibility] = useState<"public" | "private">("private");
  const [checkOverlap, setCheckOverlap] = useState(false);

  const { data: overlappingTrips, isFetching: isCheckingOverlap } = useQuery({
    ...discoverOverlappingQueryOptions(destination, startDate, endDate),
    enabled: checkOverlap && !!destination && !!startDate && !!endDate,
  });

  const mutation = useMutation({
    mutationFn: createGroupTrip,
    onSuccess: (data) => {
      toast.success("Trip created! Share the invite link with friends.");
      queryClient.invalidateQueries({ queryKey: ["group-trips"] });
      navigate({ to: "/trips/$tripId", params: { tripId: data.id } });
    },
    onError: (error: any) => {
      toast.error(
        error?.response?.data?.detail || "Failed to create trip."
      );
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() || !destination.trim() || !startDate || !endDate) {
      toast.error("Please fill in all required fields.");
      return;
    }

    const payload: CreateGroupTripPayload = {
      title: title.trim(),
      destination: destination.trim(),
      description: description.trim() || undefined,
      start_date: startDate,
      end_date: endDate,
      visibility,
    };
    mutation.mutate(payload);
  };

  return (
    <div className="container mx-auto py-8 px-4 space-y-8">
      {/* Header */}
      <div className="text-center space-y-2">
        <div className="flex items-center justify-center gap-2">
          <UsersRound className="h-8 w-8 text-primary" />
          <h1 className="text-3xl font-bold tracking-tight">Create Group Trip</h1>
        </div>
        <p className="text-muted-foreground max-w-xl mx-auto">
          Set up a trip and invite friends with a shareable link.
        </p>
      </div>

      {/* Form */}
      <Card className="max-w-2xl mx-auto p-6">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Title */}
          <div className="space-y-2">
            <Label htmlFor="title">Trip Title</Label>
            <Input
              id="title"
              placeholder="e.g. Weekend in Sylhet"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
            />
          </div>

          {/* Destination */}
          <div className="space-y-2">
            <Label htmlFor="destination" className="flex items-center gap-2">
              <MapPin className="h-4 w-4" /> Destination
            </Label>
            <DestinationCombobox
              id="destination"
              value={destination}
              onChange={(val) => {
                setDestination(val);
                setCheckOverlap(false);
              }}
              placeholder="Search Bangladesh destinations..."
              required
            />
          </div>

          {/* Description */}
          <div className="space-y-2">
            <Label htmlFor="description">Description (optional)</Label>
            <Textarea
              id="description"
              placeholder="What's the plan? Any details for the group..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={3}
            />
          </div>

          {/* Dates */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="start_date" className="flex items-center gap-2">
                <Calendar className="h-4 w-4" /> Start Date
              </Label>
              <Input
                id="start_date"
                type="date"
                value={startDate}
                onChange={(e) => {
                  setStartDate(e.target.value);
                  setCheckOverlap(false);
                }}
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="end_date" className="flex items-center gap-2">
                <Calendar className="h-4 w-4" /> End Date
              </Label>
              <Input
                id="end_date"
                type="date"
                value={endDate}
                min={startDate}
                onChange={(e) => {
                  setEndDate(e.target.value);
                  setCheckOverlap(false);
                }}
                required
              />
            </div>
          </div>

          {/* Visibility */}
          <div className="space-y-2">
            <Label>Visibility</Label>
            <div className="flex gap-3">
              <button
                type="button"
                onClick={() => setVisibility("private")}
                className={`
                  flex-1 flex items-center justify-center gap-2 rounded-lg border p-3 text-sm font-medium transition-colors cursor-pointer
                  ${
                    visibility === "private"
                      ? "bg-primary text-primary-foreground border-primary"
                      : "bg-background text-foreground border-input hover:bg-accent"
                  }
                `}
              >
                <Lock size={16} />
                Private
              </button>
              <button
                type="button"
                onClick={() => setVisibility("public")}
                className={`
                  flex-1 flex items-center justify-center gap-2 rounded-lg border p-3 text-sm font-medium transition-colors cursor-pointer
                  ${
                    visibility === "public"
                      ? "bg-primary text-primary-foreground border-primary"
                      : "bg-background text-foreground border-input hover:bg-accent"
                  }
                `}
              >
                <Globe size={16} />
                Public
              </button>
            </div>
            <p className="text-xs text-muted-foreground">
              {visibility === "private"
                ? "Only people with the invite link can see and join this trip."
                : "Anyone can discover and view this trip. Invite link still works."}
            </p>
          </div>

          {/* Check overlapping trips */}
          <div className="space-y-3">
            <Button
              type="button"
              variant="outline"
              className="w-full"
              disabled={!destination || !startDate || !endDate || isCheckingOverlap}
              onClick={() => setCheckOverlap(true)}
            >
              {isCheckingOverlap ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Checking...
                </>
              ) : (
                <>
                  <Search className="mr-2 h-4 w-4" />
                  Check Overlapping Trips
                </>
              )}
            </Button>

            {checkOverlap && overlappingTrips && overlappingTrips.length > 0 && (
              <Card className="p-4 space-y-3 border-dashed">
                <p className="text-sm font-medium text-muted-foreground">
                  {overlappingTrips.length} existing trip{overlappingTrips.length !== 1 ? "s" : ""} found at{" "}
                  <span className="font-semibold text-foreground">{destination}</span> with overlapping dates:
                </p>
                <div className="space-y-2">
                  {overlappingTrips.map((t) => (
                    <Link
                      key={t.id}
                      to="/trips/$tripId"
                      params={{ tripId: t.id }}
                      target="_blank"
                      className="flex items-center justify-between gap-3 p-3 rounded-lg border hover:bg-muted/50 transition-colors group"
                    >
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium truncate">{t.title}</p>
                        <div className="flex items-center gap-3 text-xs text-muted-foreground mt-1">
                          <span className="flex items-center gap-1">
                            <Calendar size={12} />
                            {new Date(t.start_date).toLocaleDateString()} -{" "}
                            {new Date(t.end_date).toLocaleDateString()}
                          </span>
                          <span className="flex items-center gap-1">
                            <Users size={12} />
                            {t.member_count}
                          </span>
                        </div>
                      </div>
                      <ExternalLink
                        size={14}
                        className="shrink-0 text-muted-foreground group-hover:text-foreground transition-colors"
                      />
                    </Link>
                  ))}
                </div>
                <p className="text-xs text-muted-foreground">
                  You can join an existing trip or still create your own below.
                </p>
              </Card>
            )}

            {checkOverlap && overlappingTrips && overlappingTrips.length === 0 && (
              <p className="text-sm text-muted-foreground text-center py-2">
                No overlapping trips found. You'll be the first!
              </p>
            )}
          </div>

          {/* Submit */}
          <Button
            type="submit"
            className="w-full"
            disabled={mutation.isPending}
          >
            {mutation.isPending ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Creating Trip...
              </>
            ) : (
              <>
                <UsersRound className="mr-2 h-4 w-4" />
                Create Trip
              </>
            )}
          </Button>
        </form>
      </Card>
    </div>
  );
}
