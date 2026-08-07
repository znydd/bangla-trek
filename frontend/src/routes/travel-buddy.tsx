import { useMemo, useState, type SubmitEvent } from "react";
import { createFileRoute } from "@tanstack/react-router";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import {
  CalendarDays,
  Mail,
  MapPin,
  Plus,
  Search,
  Users,
  WalletCards,
  Loader2,
  Trash2,
} from "lucide-react";

import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
export type CommunicationPlatform = "WhatsApp" | "Telegram" | "Messenger" | "Email / BCC Draft";

export interface PublicTrip {
  id: string;
  creatorId?: string;
  isHost?: boolean;
  title: string;
  origin: string;
  destination: string;
  startAt: string;
  endAt: string;
  meetingPoint: string;
  transport: string;
  estimatedCost: string;
  description: string;
  itinerary: string;
  requirements: string[];
  organizerName: string;
  organizerInitials?: string;
  organizerEmail?: string;
  communicationPlatform: CommunicationPlatform;
  communicationNote: string;
  memberCount: number;
  maxMembers: number;
  participantEmails?: string[];
  ownedByViewer?: boolean;
}
import { useAuth } from "@/hooks/useAuth";
import { LoginModal } from "@/components/ui/login-modal";
import {
  fetchPublicTrips,
  createTrip as apiCreateTrip,
  joinTrip as apiJoinTrip,
  deleteTrip as apiDeleteTrip,
  fetchOrganizerEmailDraft,
  type TravelTripRead,
} from "@/services/group-trip.service";

export const Route = createFileRoute("/travel-buddy")({
  component: TravelBuddyPage,
});

const dateFormatter = new Intl.DateTimeFormat("en-BD", {
  day: "numeric",
  month: "short",
  year: "numeric",
});

function toDate(value: string) {
  return new Date(value);
}

function formatTripDate(startAt: string, endAt: string) {
  const start = toDate(startAt);
  const end = toDate(endAt);
  const sameDay = start.toDateString() === end.toDateString();

  if (sameDay) return dateFormatter.format(start);
  return `${dateFormatter.format(start)} – ${dateFormatter.format(end)}`;
}

function initials(name: string) {
  return name
    .split(" ")
    .map((part) => part[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();
}

function TravelBuddyPage() {
  const { user, isAuthenticated } = useAuth();
  const queryClient = useQueryClient();

  const [query, setQuery] = useState("");
  const [selectedTripId, setSelectedTripId] = useState<string | null>(null);
  const [createOpen, setCreateOpen] = useState(false);
  const [loginOpen, setLoginOpen] = useState(false);
  const [loginAction, setLoginAction] = useState("");
  const [joiningTripId, setJoiningTripId] = useState<string | null>(null);
  const [deletingTripId, setDeletingTripId] = useState<string | null>(null);

  // Fetch real trips from backend
  const { data: apiTrips, isLoading } = useQuery({
    queryKey: ["travel-trips", "public", query],
    queryFn: () => fetchPublicTrips({ destination: query }),
  });

  // Convert backend trips with Host checks
  const mappedApiTrips: PublicTrip[] = useMemo(() => {
    if (!apiTrips) return [];
    return apiTrips.map((t: TravelTripRead) => ({
      id: t.id,
      creatorId: t.creator_id,
      isHost: user?.id === t.creator_id,
      title: t.title,
      organizerName: t.creator_name,
      organizerInitials: initials(t.creator_name),
      organizerEmail: "organizer@banglatrek.com",
      participantEmails: [],
      origin: t.origin,
      destination: t.destination,
      startAt: t.start_at,
      endAt: t.end_at,
      meetingPoint: "City Center",
      transport: t.transport || "Public Transport",
      estimatedCost: t.estimated_cost_min_bdt ? `৳${t.estimated_cost_min_bdt} - ৳${t.estimated_cost_max_bdt}` : "Budget shared",
      description: "Travel together with Bongo Vromon community.",
      itinerary: "Day 1: Arrival and local explore.",
      maxMembers: t.max_members,
      memberCount: t.joined_members_count,
      communicationPlatform: "Email / BCC Draft" as CommunicationPlatform,
      communicationNote: "Organizer will send email before trip departure.",
      requirements: ["Friendly attitude", "Timely arrival"],
    }));
  }, [apiTrips, user?.id]);

  const selectedTrip = mappedApiTrips.find((trip) => trip.id === selectedTripId) ?? null;

  const handleJoinTrip = async (tripId: string) => {
    if (!isAuthenticated) {
      setLoginAction("join a group trip");
      setLoginOpen(true);
      return;
    }

    setJoiningTripId(tripId);
    try {
      await apiJoinTrip(tripId);
      toast.success("Successfully joined the trip!");
      setSelectedTripId(null); // Pop-up automatically closes after successful join
      await queryClient.invalidateQueries({ queryKey: ["travel-trips"] });
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || "Failed to join trip";
      toast.error(msg);
    } finally {
      setJoiningTripId(null);
    }
  };

  const handleOpenHostGmail = async (tripId: string) => {
    try {
      const draft = await fetchOrganizerEmailDraft(tripId);
      if (draft.gmail_url) {
        window.open(draft.gmail_url, "_blank");
      } else if (draft.mailto_url) {
        window.open(draft.mailto_url, "_blank");
      } else {
        toast.error("No member emails found to send.");
      }
    } catch {
      toast.error("Only the trip host can email members.");
    }
  };

  const handleDeleteTrip = async (tripId: string) => {
    if (!isAuthenticated) return;
    setDeletingTripId(tripId);
    try {
      await apiDeleteTrip(tripId);
      toast.success("Trip post deleted successfully!");
      setSelectedTripId(null);
      await queryClient.invalidateQueries({ queryKey: ["travel-trips"] });
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || "Failed to delete trip";
      toast.error(msg);
    } finally {
      setDeletingTripId(null);
    }
  };

  const handleCreateTripSubmit = async (event: SubmitEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!isAuthenticated) {
      setLoginAction("create a group trip");
      setLoginOpen(true);
      return;
    }

    const form = new FormData(event.currentTarget);
    const value = (name: string) => String(form.get(name) ?? "").trim();

    try {
      await apiCreateTrip({
        title: value("title"),
        origin: value("origin"),
        destination: value("destination"),
        start_at: new Date(value("startAt")).toISOString(),
        end_at: new Date(value("endAt")).toISOString(),
        meeting_point: value("meetingPoint"),
        transport: value("transport"),
        estimated_cost_min_bdt: parseFloat(value("costMin")) || 2000,
        estimated_cost_max_bdt: parseFloat(value("costMax")) || 5000,
        description: value("description"),
        max_members: parseInt(value("maxMembers")) || 5,
        communication_platform: "Email / BCC Draft",
        communication_note: value("note"),
        requirements: value("requirements").split("\n").filter(Boolean),
      });

      toast.success("Public travel trip created!");
      setCreateOpen(false);
      await queryClient.invalidateQueries({ queryKey: ["travel-trips"] });
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || "Failed to create trip";
      toast.error(msg);
    }
  };

  return (
    <div className="min-h-screen bg-[#f7f7f2] pb-24">
      <LoginModal
        open={loginOpen}
        onOpenChange={setLoginOpen}
        action={loginAction}
      />
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {/* Header Banner */}
        <section className="relative overflow-hidden rounded-[2.5rem] bg-zinc-950 px-6 py-12 text-white sm:px-10 lg:px-16">
          <div className="relative z-10 max-w-3xl">
            <div className="inline-flex items-center gap-2 rounded-full border border-white/20 bg-white/10 px-4 py-1.5 text-xs font-semibold text-emerald-300">
              <Users size={14} />
              Travel Buddy Trips
            </div>
            <h1 className="mt-5 text-4xl font-black tracking-tight sm:text-5xl lg:text-6xl">
              Travel together. Split costs. Stay safe.
            </h1>
            <p className="mt-4 text-base leading-7 text-white/70 sm:text-lg">
              Find public trips organized by verified travelers or propose your own plan across Bangladesh.
            </p>
            <div className="mt-8 flex flex-wrap gap-4">
              <Button
                onClick={() => {
                  if (!isAuthenticated) {
                    setLoginAction("organize a trip");
                    setLoginOpen(true);
                  } else {
                    setCreateOpen(true);
                  }
                }}
                size="lg"
                className="h-12 rounded-xl bg-emerald-500 px-6 text-zinc-950 font-bold hover:bg-emerald-400"
              >
                <Plus size={18} className="mr-1" />
                Organize a trip
              </Button>
            </div>
          </div>
        </section>

        {/* Search Bar */}
        <div className="mt-8 flex items-center gap-3 rounded-2xl border border-black/10 bg-white p-2 shadow-sm">
          <Search size={20} className="ml-3 text-muted-foreground" />
          <Input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search destination, origin or trip title..."
            className="h-11 border-0 shadow-none focus-visible:ring-0"
          />
        </div>

        {/* Trips Grid */}
        <section className="mt-8">
          {isLoading && (
            <div className="flex items-center justify-center py-20">
              <Loader2 size={32} className="animate-spin text-emerald-600" />
            </div>
          )}

          {!isLoading && (
            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {mappedApiTrips.map((trip) => (
                <div
                  key={trip.id}
                  className="flex flex-col justify-between rounded-3xl border border-black/10 bg-white p-6 shadow-sm transition-shadow hover:shadow-md"
                >
                  <div>
                    <div className="flex items-center justify-between">
                      <span className="rounded-full bg-emerald-100 px-3 py-1 text-xs font-bold text-emerald-800">
                        {trip.memberCount} / {trip.maxMembers} Members
                      </span>
                      <span className="text-xs font-medium text-zinc-500">
                        {trip.transport}
                      </span>
                    </div>

                    <h3 className="mt-4 text-xl font-bold tracking-tight text-zinc-900">
                      {trip.title}
                    </h3>

                    <div className="mt-3 space-y-2 text-sm text-zinc-600">
                      <p className="flex items-center gap-2">
                        <MapPin size={16} className="text-emerald-600" />
                        {trip.origin} → {trip.destination}
                      </p>
                      <p className="flex items-center gap-2">
                        <CalendarDays size={16} className="text-emerald-600" />
                        {formatTripDate(trip.startAt, trip.endAt)}
                      </p>
                      <p className="flex items-center gap-2">
                        <WalletCards size={16} className="text-emerald-600" />
                        {trip.estimatedCost}
                      </p>
                    </div>
                  </div>

                  <div className="mt-6 flex items-center justify-between border-t pt-4">
                    <div className="flex items-center gap-2">
                      <div className="flex size-8 items-center justify-center rounded-full bg-zinc-900 text-xs font-bold text-white">
                        {trip.organizerInitials}
                      </div>
                      <span className="text-xs font-semibold text-zinc-800">
                        {trip.organizerName} {trip.isHost && "(Host)"}
                      </span>
                    </div>

                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => setSelectedTripId(trip.id)}
                        className="rounded-lg text-xs"
                      >
                        Details
                      </Button>
                      {trip.isHost ? (
                        <div className="flex gap-1.5">
                          <Button
                            size="sm"
                            onClick={() => void handleOpenHostGmail(trip.id)}
                            className="rounded-lg bg-emerald-600 text-xs font-semibold text-white hover:bg-emerald-700"
                            title="Open Gmail to email members"
                          >
                            <Mail size={13} className="mr-1" />
                            Email
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            disabled={deletingTripId === trip.id}
                            onClick={() => void handleDeleteTrip(trip.id)}
                            className="rounded-lg border-red-200 bg-red-50 p-2 text-xs font-semibold text-red-600 hover:bg-red-100 hover:text-red-700 disabled:opacity-50"
                            title="Delete your trip post"
                          >
                            {deletingTripId === trip.id ? (
                              <Loader2 size={13} className="animate-spin text-red-600" />
                            ) : (
                              <Trash2 size={13} />
                            )}
                          </Button>
                        </div>
                      ) : (
                        <Button
                          size="sm"
                          disabled={joiningTripId === trip.id}
                          onClick={() => void handleJoinTrip(trip.id)}
                          className="rounded-lg bg-emerald-600 text-xs font-semibold text-white hover:bg-emerald-700 disabled:opacity-50"
                        >
                          {joiningTripId === trip.id ? (
                            <>
                              <Loader2 size={13} className="mr-1 animate-spin" />
                              Joining...
                            </>
                          ) : (
                            "Join Trip"
                          )}
                        </Button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      </div>

      {/* Trip Detail Dialog */}
      {selectedTrip && (
        <Dialog open={!!selectedTrip} onOpenChange={() => setSelectedTripId(null)}>
          <DialogContent className="max-w-2xl rounded-3xl">
            <DialogHeader>
              <div className="flex items-center justify-between pr-6">
                <DialogTitle className="text-2xl font-bold">{selectedTrip.title}</DialogTitle>
                {selectedTrip.isHost && (
                  <span className="rounded-full bg-emerald-100 px-3 py-1 text-xs font-bold text-emerald-800">
                    Host (You)
                  </span>
                )}
              </div>
              <DialogDescription>
                Organized by {selectedTrip.organizerName} · {selectedTrip.origin} to {selectedTrip.destination}
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-4 py-4 text-sm">
              <div className="rounded-2xl bg-zinc-50 p-4 space-y-2">
                <p><strong>Dates:</strong> {formatTripDate(selectedTrip.startAt, selectedTrip.endAt)}</p>
                <p><strong>Transport:</strong> {selectedTrip.transport}</p>
                <p><strong>Cost Estimate:</strong> {selectedTrip.estimatedCost}</p>
                <p><strong>Description:</strong> {selectedTrip.description}</p>
              </div>

              <div>
                <h4 className="font-semibold mb-2">Requirements</h4>
                <ul className="list-disc pl-5 text-zinc-600 space-y-1">
                  {selectedTrip.requirements.map((req, idx) => (
                    <li key={idx}>{req}</li>
                  ))}
                </ul>
              </div>
            </div>

            <DialogFooter className="flex justify-between items-center gap-2">
              {selectedTrip.isHost ? (
                <div className="flex w-full items-center justify-between gap-2">
                  <Button
                    variant="outline"
                    disabled={deletingTripId === selectedTrip.id}
                    onClick={() => void handleDeleteTrip(selectedTrip.id)}
                    className="border-red-200 bg-red-50 text-red-600 hover:bg-red-100 hover:text-red-700 font-semibold disabled:opacity-50"
                  >
                    {deletingTripId === selectedTrip.id ? (
                      <>
                        <Loader2 size={16} className="mr-1.5 animate-spin text-red-600" />
                        Deleting...
                      </>
                    ) : (
                      <>
                        <Trash2 size={16} className="mr-1.5" />
                        Delete Trip
                      </>
                    )}
                  </Button>
                  <Button
                    onClick={() => void handleOpenHostGmail(selectedTrip.id)}
                    className="bg-emerald-600 text-white hover:bg-emerald-700 font-semibold"
                  >
                    <Mail size={16} className="mr-1.5" />
                    Email Members (CC via Gmail)
                  </Button>
                </div>
              ) : (
                <Button
                  disabled={joiningTripId === selectedTrip.id}
                  onClick={() => void handleJoinTrip(selectedTrip.id)}
                  className="bg-emerald-600 text-white hover:bg-emerald-700 font-semibold disabled:opacity-50"
                >
                  {joiningTripId === selectedTrip.id ? (
                    <>
                      <Loader2 size={16} className="mr-1.5 animate-spin" />
                      Joining Trip...
                    </>
                  ) : (
                    "Join Trip"
                  )}
                </Button>
              )}
            </DialogFooter>
          </DialogContent>
        </Dialog>
      )}



      {/* Create Trip Dialog */}
      <Dialog open={createOpen} onOpenChange={setCreateOpen}>
        <DialogContent className="max-w-xl rounded-3xl">
          <DialogHeader>
            <DialogTitle className="text-2xl font-bold">Organize a Public Trip</DialogTitle>
            <DialogDescription>
              Share your travel details for other Bangla Trek members to join.
            </DialogDescription>
          </DialogHeader>

          <form onSubmit={handleCreateTripSubmit} className="space-y-4 py-2">
            <div>
              <Label htmlFor="title">Trip Title</Label>
              <Input id="title" name="title" required placeholder="e.g. Sajek Valley Stargazing Camping" />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="origin">Origin City</Label>
                <Input id="origin" name="origin" required placeholder="Dhaka" />
              </div>
              <div>
                <Label htmlFor="destination">Destination</Label>
                <Input id="destination" name="destination" required placeholder="Sajek" />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="startAt">Start Date</Label>
                <Input id="startAt" name="startAt" type="date" required />
              </div>
              <div>
                <Label htmlFor="endAt">End Date</Label>
                <Input id="endAt" name="endAt" type="date" required />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="transport">Mode of Transport</Label>
                <Input id="transport" name="transport" placeholder="Chander Gari / Train" />
              </div>
              <div>
                <Label htmlFor="maxMembers">Max Capacity</Label>
                <Input id="maxMembers" name="maxMembers" type="number" min="2" max="50" defaultValue="5" />
              </div>
            </div>

            <div>
              <Label htmlFor="description">Trip Description</Label>
              <Textarea id="description" name="description" placeholder="Describe the plan, meeting point, and rules." />
            </div>

            <div>
              <Label htmlFor="requirements">Requirements (1 per line)</Label>
              <Textarea id="requirements" name="requirements" placeholder="Carry NID copy&#10;Warm jacket" />
            </div>

            <DialogFooter className="mt-4">
              <Button type="submit" className="bg-emerald-600 text-white hover:bg-emerald-700 font-semibold w-full">
                Publish Public Trip
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}
