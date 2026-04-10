import { useState } from "react";
import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  groupTripDetailQueryOptions,
  discoverOverlappingQueryOptions,
  updateGroupTrip,
  joinGroupTrip,
  leaveGroupTrip,
  deleteGroupTrip,
} from "@/services/group-trip.service";
import { useAuth } from "@/hooks/useAuth";
import { MemberList } from "@/components/trips/MemberList";
import { DestinationCombobox } from "@/components/trips/DestinationCombobox";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Skeleton } from "@/components/ui/skeleton";
import { Separator } from "@/components/ui/separator";
import { toast } from "sonner";
import {
  MapPin,
  Calendar,
  Users,
  Globe,
  Lock,
  Copy,
  Check,
  LogOut,
  Trash2,
  ArrowLeft,
  UserSearch,
  UsersRound,
  Loader2,
  Pencil,
  X,
  Save,
} from "lucide-react";
import { Link } from "@tanstack/react-router";

export const Route = createFileRoute("/_authenticated/trips/$tripId")({
  component: TripDetailPage,
});

function TripDetailPage() {
  const { tripId } = Route.useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const [copied, setCopied] = useState(false);
  const [editing, setEditing] = useState(false);
  const [editForm, setEditForm] = useState({
    title: "",
    destination: "",
    description: "",
    start_date: "",
    end_date: "",
    visibility: "" as "public" | "private",
  });

  const { data: trip, isLoading, error } = useQuery(
    groupTripDetailQueryOptions(tripId)
  );

  // Discover overlapping public trips at the same destination/dates
  const { data: overlappingTrips } = useQuery({
    ...discoverOverlappingQueryOptions(
      trip?.destination ?? "",
      trip?.start_date ?? "",
      trip?.end_date ?? ""
    ),
    enabled: !!trip,
  });

  const leaveMutation = useMutation({
    mutationFn: () => leaveGroupTrip(tripId),
    onSuccess: () => {
      toast.success("You left the trip.");
      queryClient.invalidateQueries({ queryKey: ["group-trips"] });
      navigate({ to: "/trips" });
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail || "Failed to leave trip.");
    },
  });

  const deleteMutation = useMutation({
    mutationFn: () => deleteGroupTrip(tripId),
    onSuccess: () => {
      toast.success("Trip deleted.");
      queryClient.invalidateQueries({ queryKey: ["group-trips"] });
      navigate({ to: "/trips" });
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail || "Failed to delete trip.");
    },
  });

  const joinMutation = useMutation({
    mutationFn: () => joinGroupTrip(trip!.invite_code),
    onSuccess: () => {
      toast.success("You've joined the trip!");
      queryClient.invalidateQueries({ queryKey: ["group-trips"] });
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail || "Failed to join trip.");
    },
  });

  const updateMutation = useMutation({
    mutationFn: (payload: Parameters<typeof updateGroupTrip>[1]) =>
      updateGroupTrip(tripId, payload),
    onSuccess: () => {
      toast.success("Trip updated!");
      setEditing(false);
      queryClient.invalidateQueries({ queryKey: ["group-trips", tripId] });
      queryClient.invalidateQueries({ queryKey: ["group-trips"] });
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail || "Failed to update trip.");
    },
  });

  const startEditing = () => {
    if (!trip) return;
    setEditForm({
      title: trip.title,
      destination: trip.destination,
      description: trip.description || "",
      start_date: trip.start_date,
      end_date: trip.end_date,
      visibility: trip.visibility,
    });
    setEditing(true);
  };

  const handleEditSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    updateMutation.mutate({
      title: editForm.title,
      destination: editForm.destination,
      description: editForm.description || undefined,
      start_date: editForm.start_date,
      end_date: editForm.end_date,
      visibility: editForm.visibility,
    });
  };

  const copyInviteLink = async () => {
    if (!trip) return;
    const link = `${window.location.origin}/trips/join/${trip.invite_code}`;
    await navigator.clipboard.writeText(link);
    setCopied(true);
    toast.success("Invite link copied!");
    setTimeout(() => setCopied(false), 2000);
  };

  if (isLoading) {
    return (
      <div className="container mx-auto py-8 px-4 space-y-6 max-w-3xl">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-64 rounded-xl" />
        <Skeleton className="h-48 rounded-xl" />
      </div>
    );
  }

  if (error || !trip) {
    return (
      <div className="container mx-auto py-8 px-4 text-center space-y-4">
        <h1 className="text-2xl font-bold">Trip not found</h1>
        <p className="text-muted-foreground">
          This trip doesn't exist or you don't have access to it.
        </p>
        <Button variant="outline" render={<Link to="/trips" />}>
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Trips
        </Button>
      </div>
    );
  }

  const isOwner = user?.id === trip.creator_id;
  const isMember = trip.members.some((m) => m.user_id === user?.id);

  const startDate = new Date(trip.start_date).toLocaleDateString("en-GB", {
    weekday: "short",
    day: "numeric",
    month: "long",
    year: "numeric",
  });
  const endDate = new Date(trip.end_date).toLocaleDateString("en-GB", {
    weekday: "short",
    day: "numeric",
    month: "long",
    year: "numeric",
  });

  return (
    <div className="container mx-auto py-8 px-4 space-y-6 max-w-3xl">
      {/* Back link */}
      <Button variant="ghost" size="sm" render={<Link to="/trips" />}>
        <ArrowLeft className="mr-2 h-4 w-4" />
        All Trips
      </Button>

      {/* Trip header */}
      <Card className="p-6 space-y-4">
        <div className="h-2 -mt-6 -mx-6 mb-4 bg-gradient-to-r from-green-500 to-emerald-400 rounded-t-xl" />

        {editing ? (
          <form onSubmit={handleEditSubmit} className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold">Edit Trip</h2>
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={() => setEditing(false)}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>

            <div className="space-y-2">
              <Label htmlFor="edit-title">Title</Label>
              <Input
                id="edit-title"
                value={editForm.title}
                onChange={(e) =>
                  setEditForm((f) => ({ ...f, title: e.target.value }))
                }
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="edit-destination" className="flex items-center gap-2">
                <MapPin className="h-4 w-4" /> Destination
              </Label>
              <DestinationCombobox
                id="edit-destination"
                value={editForm.destination}
                onChange={(val) =>
                  setEditForm((f) => ({ ...f, destination: val }))
                }
                placeholder="Search Bangladesh destinations..."
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="edit-description">Description</Label>
              <Textarea
                id="edit-description"
                value={editForm.description}
                onChange={(e) =>
                  setEditForm((f) => ({ ...f, description: e.target.value }))
                }
                rows={3}
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="edit-start" className="flex items-center gap-2">
                  <Calendar className="h-4 w-4" /> Start Date
                </Label>
                <Input
                  id="edit-start"
                  type="date"
                  value={editForm.start_date}
                  onChange={(e) =>
                    setEditForm((f) => ({ ...f, start_date: e.target.value }))
                  }
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="edit-end" className="flex items-center gap-2">
                  <Calendar className="h-4 w-4" /> End Date
                </Label>
                <Input
                  id="edit-end"
                  type="date"
                  value={editForm.end_date}
                  min={editForm.start_date}
                  onChange={(e) =>
                    setEditForm((f) => ({ ...f, end_date: e.target.value }))
                  }
                  required
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label>Visibility</Label>
              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={() =>
                    setEditForm((f) => ({ ...f, visibility: "private" }))
                  }
                  className={`
                    flex-1 flex items-center justify-center gap-2 rounded-lg border p-3 text-sm font-medium transition-colors cursor-pointer
                    ${
                      editForm.visibility === "private"
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
                  onClick={() =>
                    setEditForm((f) => ({ ...f, visibility: "public" }))
                  }
                  className={`
                    flex-1 flex items-center justify-center gap-2 rounded-lg border p-3 text-sm font-medium transition-colors cursor-pointer
                    ${
                      editForm.visibility === "public"
                        ? "bg-primary text-primary-foreground border-primary"
                        : "bg-background text-foreground border-input hover:bg-accent"
                    }
                  `}
                >
                  <Globe size={16} />
                  Public
                </button>
              </div>
            </div>

            <div className="flex gap-2 pt-2">
              <Button type="submit" disabled={updateMutation.isPending}>
                {updateMutation.isPending ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Saving...
                  </>
                ) : (
                  <>
                    <Save className="mr-2 h-4 w-4" />
                    Save Changes
                  </>
                )}
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => setEditing(false)}
              >
                Cancel
              </Button>
            </div>
          </form>
        ) : (
          <>
            <div className="flex items-start justify-between gap-3 flex-wrap">
              <div className="space-y-1">
                <h1 className="text-2xl font-bold tracking-tight">{trip.title}</h1>
                <div className="flex items-center gap-1.5 text-muted-foreground">
                  <MapPin size={16} />
                  <span>{trip.destination}</span>
                </div>
              </div>
              <div className="flex items-center gap-2">
                {isOwner && (
                  <Button variant="ghost" size="sm" onClick={startEditing}>
                    <Pencil className="h-4 w-4" />
                  </Button>
                )}
                <Badge
                  variant={trip.visibility === "public" ? "secondary" : "outline"}
                >
                  {trip.visibility === "public" ? (
                    <Globe size={12} className="mr-1" />
                  ) : (
                    <Lock size={12} className="mr-1" />
                  )}
                  {trip.visibility}
                </Badge>
              </div>
            </div>

            {trip.description && (
              <p className="text-muted-foreground">{trip.description}</p>
            )}

            <div className="flex flex-wrap gap-4 text-sm">
              <div className="flex items-center gap-1.5 text-muted-foreground">
                <Calendar size={14} />
                <span>
                  {startDate} - {endDate}
                </span>
              </div>
              <div className="flex items-center gap-1.5 text-muted-foreground">
                <Users size={14} />
                <span>
                  {trip.member_count} member{trip.member_count !== 1 ? "s" : ""}
                </span>
              </div>
            </div>
          </>
        )}

        {!editing && <Separator />}

        {isMember ? (
          <>
            {/* Invite link — only visible to members */}
            <div className="space-y-2">
              <p className="text-sm font-medium">Invite Link</p>
              <div className="flex items-center gap-2">
                <code className="flex-1 text-xs bg-muted px-3 py-2 rounded-md truncate">
                  {window.location.origin}/trips/join/{trip.invite_code}
                </code>
                <Button variant="outline" size="sm" onClick={copyInviteLink}>
                  {copied ? (
                    <Check className="h-4 w-4 text-green-600" />
                  ) : (
                    <Copy className="h-4 w-4" />
                  )}
                </Button>
              </div>
            </div>

            {/* Member actions */}
            <div className="flex gap-2 pt-2">
              {!isOwner && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => leaveMutation.mutate()}
                  disabled={leaveMutation.isPending}
                >
                  <LogOut className="mr-2 h-4 w-4" />
                  Leave Trip
                </Button>
              )}
              {isOwner && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    if (confirm("Are you sure you want to delete this trip?")) {
                      deleteMutation.mutate();
                    }
                  }}
                  disabled={deleteMutation.isPending}
                  className="text-destructive hover:text-destructive"
                >
                  <Trash2 className="mr-2 h-4 w-4" />
                  Delete Trip
                </Button>
              )}
            </div>
          </>
        ) : (
          /* Join button for non-members viewing a public trip */
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
        )}
      </Card>

      {/* Members */}
      <Card className="p-6 space-y-4">
        <h2 className="text-lg font-semibold flex items-center gap-2">
          <Users size={18} />
          Members ({trip.members.length})
        </h2>
        <MemberList members={trip.members} />
      </Card>

      {/* Overlapping public trips at the same destination */}
      {overlappingTrips && overlappingTrips.length > 0 && (
        <Card className="p-6 space-y-4">
          <h2 className="text-lg font-semibold flex items-center gap-2">
            <UserSearch size={18} />
            Other trips to {trip.destination}
          </h2>
          <p className="text-sm text-muted-foreground">
            Public trips with overlapping dates at the same destination.
          </p>
          <div className="space-y-2">
            {overlappingTrips.map((t) => (
              <Link
                key={t.id}
                to="/trips/$tripId"
                params={{ tripId: t.id }}
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
                      {t.member_count} member{t.member_count !== 1 ? "s" : ""}
                    </span>
                  </div>
                  {t.creator_name && (
                    <p className="text-xs text-muted-foreground mt-1">
                      by {t.creator_name}
                    </p>
                  )}
                </div>
                <ArrowLeft
                  size={14}
                  className="shrink-0 text-muted-foreground group-hover:text-foreground transition-colors rotate-180"
                />
              </Link>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
}
