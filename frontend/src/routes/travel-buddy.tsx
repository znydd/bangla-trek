import { useMemo, useState, type ReactNode, type SubmitEvent } from "react";
import { createFileRoute } from "@tanstack/react-router";
import {
  ArrowRight,
  BusFront,
  CalendarDays,
  Check,
  Clock3,
  Mail,
  MapPin,
  MessageCircle,
  Plus,
  Search,
  Send,
  UserPlus,
  Users,
  WalletCards,
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
import {
  syntheticTrips,
  type CommunicationPlatform,
  type PublicTrip,
} from "@/data/synthetic-trips";

export const Route = createFileRoute("/travel-buddy")({
  // Authentication is intentionally disabled while the Travel Buddy UI is prototyped.
  // Add the auth guard here before connecting join and create actions to the backend.
  component: TravelBuddyPage,
});

const dateFormatter = new Intl.DateTimeFormat("en-BD", {
  day: "numeric",
  month: "short",
  year: "numeric",
});

const timeFormatter = new Intl.DateTimeFormat("en-BD", {
  hour: "numeric",
  minute: "2-digit",
});

function toDate(value: string) {
  return new Date(value);
}

function formatTripDate(trip: PublicTrip) {
  const start = toDate(trip.startAt);
  const end = toDate(trip.endAt);
  const sameDay = start.toDateString() === end.toDateString();

  if (sameDay) return dateFormatter.format(start);
  return `${dateFormatter.format(start)} – ${dateFormatter.format(end)}`;
}

function formatDateTime(value: string) {
  const date = toDate(value);
  return `${dateFormatter.format(date)}, ${timeFormatter.format(date)}`;
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
  const [trips, setTrips] = useState<PublicTrip[]>(syntheticTrips);
  const [query, setQuery] = useState("");
  const [selectedTripId, setSelectedTripId] = useState<string | null>(null);
  const [joinFormOpen, setJoinFormOpen] = useState(false);
  const [joinedTripId, setJoinedTripId] = useState<string | null>(null);
  const [createOpen, setCreateOpen] = useState(false);

  const selectedTrip = trips.find((trip) => trip.id === selectedTripId) ?? null;
  const filteredTrips = useMemo(() => {
    const normalized = query.trim().toLowerCase();
    if (!normalized) return trips;

    return trips.filter((trip) =>
      [trip.destination, trip.origin, trip.title]
        .join(" ")
        .toLowerCase()
        .includes(normalized),
    );
  }, [query, trips]);

  function openTrip(tripId: string) {
    setSelectedTripId(tripId);
    setJoinFormOpen(false);
    setJoinedTripId(null);
  }

  function submitJoinRequest(event: SubmitEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedTrip) return;

    // Login check intentionally disabled for the UI preview.

    const form = new FormData(event.currentTarget);
    const email = String(form.get("email") ?? "").trim();
    if (!email) return;

    setTrips((current) =>
      current.map((trip) =>
        trip.id === selectedTrip.id
          ? {
              ...trip,
              memberCount: Math.min(trip.memberCount + 1, trip.maxMembers),
              participantEmails: trip.participantEmails.includes(email)
                ? trip.participantEmails
                : [...trip.participantEmails, email],
            }
          : trip,
      ),
    );
    setJoinFormOpen(false);
    setJoinedTripId(selectedTrip.id);
    event.currentTarget.reset();
    toast.success("Your join request has been added to this trip.");
  }

  function createTrip(event: SubmitEvent<HTMLFormElement>) {
    event.preventDefault();

    // Login check intentionally disabled for the UI preview.
    const form = new FormData(event.currentTarget);
    const value = (name: string) => String(form.get(name) ?? "").trim();
    const destination = value("destination");
    const id = `${destination.toLowerCase().replace(/[^a-z0-9]+/g, "-")}-${Date.now()}`;
    const requirements = value("requirements")
      .split("\n")
      .map((item) => item.trim())
      .filter(Boolean);

    const newTrip: PublicTrip = {
      id,
      title: value("title"),
      origin: value("origin"),
      destination,
      startAt: value("startAt"),
      endAt: value("endAt"),
      meetingPoint: value("meetingPoint"),
      transport: value("transport"),
      estimatedCost: value("estimatedCost"),
      description: value("description"),
      itinerary: value("itinerary"),
      requirements,
      organizerName: value("organizerName"),
      organizerEmail: value("organizerEmail"),
      communicationPlatform: value("communicationPlatform") as CommunicationPlatform,
      communicationNote: value("communicationNote"),
      memberCount: 1,
      maxMembers: Number(value("maxMembers")) || 6,
      participantEmails: [],
      ownedByViewer: true,
    };

    setTrips((current) => [newTrip, ...current]);
    setCreateOpen(false);
    setSelectedTripId(id);
    event.currentTarget.reset();
    toast.success("Your public trip has been listed.");
  }

  function composeParticipantEmail(trip: PublicTrip) {
    if (!trip.participantEmails.length) {
      toast.error("Nobody has joined this trip yet.");
      return;
    }

    const subject = `${trip.destination} trip — update from ${trip.organizerName}`;
    const body = `Hello travelers,\n\nHere is an update about our ${trip.origin} to ${trip.destination} trip on ${formatTripDate(trip)}.\n\nAdd the ${trip.communicationPlatform} group link and your message here.\n\nThanks,\n${trip.organizerName}`;
    const params = new URLSearchParams({
      bcc: trip.participantEmails.join(","),
      subject,
      body,
    });
    window.location.href = `mailto:?${params.toString()}`;
  }

  return (
    <div className="min-h-[calc(100svh-5rem)] bg-[#f7f7f2] pb-20 pt-12 text-zinc-950">
      <section className="mx-auto max-w-6xl px-5 sm:px-8">
        <div className="flex flex-col gap-7 border-b border-zinc-200 pb-9 md:flex-row md:items-end md:justify-between">
          <div className="max-w-2xl">
            <p className="mb-3 text-xs font-bold uppercase tracking-[0.24em] text-emerald-700">
              Travel together
            </p>
            <h1 className="text-4xl font-black tracking-[-0.045em] sm:text-6xl">
              Find your next travel buddy.
            </h1>
            <p className="mt-4 max-w-xl text-base leading-7 text-zinc-600">
              Discover public group trips around Bangladesh, check the complete plan, and ask to join the organizer.
            </p>
          </div>

          <Button
            type="button"
            onClick={() => setCreateOpen(true)}
            className="h-12 rounded-full bg-zinc-950 px-6 text-white hover:bg-zinc-800"
          >
            <Plus className="size-5" />
            Create a trip
          </Button>
        </div>

        <div className="mt-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="relative w-full max-w-xl">
            <Search className="pointer-events-none absolute left-4 top-1/2 size-5 -translate-y-1/2 text-zinc-400" />
            <Input
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Search a destination, for example Sajek..."
              aria-label="Search trips by destination"
              className="h-13 rounded-full border-zinc-300 bg-white pl-12 pr-5 shadow-sm"
            />
          </div>
          <p className="text-sm text-zinc-500">
            <span className="font-semibold text-zinc-950">{filteredTrips.length}</span>{" "}
            public {filteredTrips.length === 1 ? "trip" : "trips"}
          </p>
        </div>

        {filteredTrips.length ? (
          <div className="mt-8 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {filteredTrips.map((trip) => (
              <TripCard key={trip.id} trip={trip} onOpen={() => openTrip(trip.id)} />
            ))}
          </div>
        ) : (
          <div className="mt-8 rounded-3xl border border-dashed border-zinc-300 bg-white px-6 py-20 text-center">
            <MapPin className="mx-auto size-9 text-zinc-300" />
            <h2 className="mt-4 text-xl font-bold">No trip found for “{query}”</h2>
            <p className="mt-2 text-zinc-500">Try another destination or create the first public trip there.</p>
          </div>
        )}
      </section>

      <TripDetailsDialog
        trip={selectedTrip}
        joinFormOpen={joinFormOpen}
        joined={joinedTripId === selectedTrip?.id}
        onOpenChange={(open) => {
          if (!open) setSelectedTripId(null);
        }}
        onShowJoinForm={() => setJoinFormOpen(true)}
        onCancelJoin={() => setJoinFormOpen(false)}
        onJoin={submitJoinRequest}
        onEmail={() => selectedTrip && composeParticipantEmail(selectedTrip)}
      />

      <CreateTripDialog
        open={createOpen}
        onOpenChange={setCreateOpen}
        onSubmit={createTrip}
      />
    </div>
  );
}

function TripCard({ trip, onOpen }: { trip: PublicTrip; onOpen: () => void }) {
  const remaining = Math.max(trip.maxMembers - trip.memberCount, 0);

  return (
    <button
      type="button"
      onClick={onOpen}
      className="group flex min-h-64 flex-col rounded-[1.75rem] border border-zinc-200 bg-white p-6 text-left shadow-sm transition hover:-translate-y-1 hover:border-zinc-300 hover:shadow-xl hover:shadow-zinc-950/5 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500"
    >
      <div className="flex items-start justify-between gap-3">
        <span className="rounded-full bg-emerald-50 px-3 py-1.5 text-xs font-bold text-emerald-800">
          {remaining ? `${remaining} spots left` : "Trip full"}
        </span>
        {trip.ownedByViewer && (
          <span className="rounded-full border border-zinc-200 px-3 py-1.5 text-xs font-semibold text-zinc-600">
            Your trip
          </span>
        )}
      </div>

      <div className="mt-8">
        <p className="text-xs font-bold uppercase tracking-[0.18em] text-zinc-400">Destination</p>
        <h2 className="mt-2 text-2xl font-black tracking-tight">{trip.destination}</h2>
        <div className="mt-4 flex items-center gap-2 text-sm font-medium text-zinc-600">
          <span>{trip.origin}</span>
          <ArrowRight className="size-4 text-emerald-600 transition-transform group-hover:translate-x-1" />
          <span>{trip.destination}</span>
        </div>
      </div>

      <div className="mt-auto flex items-end justify-between gap-4 border-t border-zinc-100 pt-5">
        <div className="flex items-center gap-2 text-sm font-semibold">
          <CalendarDays className="size-4 text-emerald-700" />
          {formatTripDate(trip)}
        </div>
        <span className="flex size-9 shrink-0 items-center justify-center rounded-full bg-zinc-950 text-white transition-transform group-hover:translate-x-1">
          <ArrowRight className="size-4" />
        </span>
      </div>
    </button>
  );
}

interface TripDetailsDialogProps {
  trip: PublicTrip | null;
  joinFormOpen: boolean;
  joined: boolean;
  onOpenChange: (open: boolean) => void;
  onShowJoinForm: () => void;
  onCancelJoin: () => void;
  onJoin: (event: SubmitEvent<HTMLFormElement>) => void;
  onEmail: () => void;
}

function TripDetailsDialog({
  trip,
  joinFormOpen,
  joined,
  onOpenChange,
  onShowJoinForm,
  onCancelJoin,
  onJoin,
  onEmail,
}: TripDetailsDialogProps) {
  if (!trip) return null;
  const isFull = trip.memberCount >= trip.maxMembers;

  return (
    <Dialog open onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[92svh] overflow-y-auto rounded-[2rem] p-0 [&_[data-slot=dialog-close]]:text-white sm:max-w-3xl">
        <div className="rounded-t-[2rem] bg-zinc-950 px-6 py-7 text-white sm:px-8">
          <p className="text-xs font-bold uppercase tracking-[0.2em] text-emerald-400">Public group trip</p>
          <DialogHeader className="mt-3 pr-10">
            <DialogTitle className="text-3xl font-black tracking-tight sm:text-4xl">{trip.destination}</DialogTitle>
            <DialogDescription className="flex items-center gap-2 text-white/65">
              {trip.origin} <ArrowRight className="size-4" /> {trip.destination}
            </DialogDescription>
          </DialogHeader>
        </div>

        <div className="space-y-7 px-6 pb-2 sm:px-8">
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            <DetailFact icon={<CalendarDays />} label="Starts" value={formatDateTime(trip.startAt)} />
            <DetailFact icon={<Clock3 />} label="Returns" value={formatDateTime(trip.endAt)} />
            <DetailFact icon={<Users />} label="Group" value={`${trip.memberCount} of ${trip.maxMembers} travelers`} />
            <DetailFact icon={<MapPin />} label="Meeting point" value={trip.meetingPoint} />
            <DetailFact icon={<BusFront />} label="Transport" value={trip.transport} />
            <DetailFact icon={<WalletCards />} label="Estimated cost" value={trip.estimatedCost} />
          </div>

          <div>
            <p className="text-xs font-bold uppercase tracking-[0.18em] text-emerald-700">The plan</p>
            <h3 className="mt-2 text-2xl font-black">{trip.title}</h3>
            <p className="mt-3 leading-7 text-zinc-600">{trip.description}</p>
            <p className="mt-4 rounded-2xl bg-zinc-100 p-5 leading-7 text-zinc-700">{trip.itinerary}</p>
          </div>

          <div className="grid gap-5 sm:grid-cols-2">
            <div className="rounded-2xl border border-zinc-200 p-5">
              <h3 className="font-bold">Before you join</h3>
              <ul className="mt-3 space-y-3">
                {trip.requirements.map((requirement) => (
                  <li key={requirement} className="flex gap-2 text-sm leading-6 text-zinc-600">
                    <Check className="mt-1 size-4 shrink-0 text-emerald-700" />
                    {requirement}
                  </li>
                ))}
              </ul>
            </div>

            <div className="rounded-2xl border border-zinc-200 p-5">
              <div className="flex items-center gap-3">
                <span className="flex size-11 items-center justify-center rounded-full bg-emerald-100 text-sm font-black text-emerald-800">
                  {initials(trip.organizerName)}
                </span>
                <div>
                  <p className="text-xs font-semibold uppercase tracking-wide text-zinc-400">Organizer</p>
                  <p className="font-bold">{trip.organizerName}</p>
                </div>
              </div>
              <div className="mt-4 flex gap-2 text-sm leading-6 text-zinc-600">
                <MessageCircle className="mt-1 size-4 shrink-0 text-emerald-700" />
                <p><span className="font-semibold text-zinc-950">{trip.communicationPlatform}:</span> {trip.communicationNote}</p>
              </div>
            </div>
          </div>

          {joined && (
            <div className="flex gap-3 rounded-2xl border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-900">
              <Check className="size-5 shrink-0" />
              <p>Your request is recorded. In the real version, the organizer will confirm it and email the group link.</p>
            </div>
          )}

          {joinFormOpen && !joined && (
            <form onSubmit={onJoin} className="rounded-2xl border border-emerald-200 bg-emerald-50/60 p-5">
              <h3 className="text-lg font-bold">Ask to join this trip</h3>
              <p className="mt-1 text-sm text-zinc-600">Your contact details will only be shared with the organizer.</p>
              <div className="mt-4 grid gap-4 sm:grid-cols-2">
                <Field label="Your name" htmlFor="join-name">
                  <Input id="join-name" name="name" required placeholder="Your full name" className="h-11 bg-white" />
                </Field>
                <Field label="Email" htmlFor="join-email">
                  <Input id="join-email" name="email" type="email" required placeholder="you@example.com" className="h-11 bg-white" />
                </Field>
              </div>
              <Field label="A short note for the organizer (optional)" htmlFor="join-note" className="mt-4">
                <Textarea id="join-note" name="note" placeholder="Introduce yourself or ask anything important..." className="min-h-20 bg-white" />
              </Field>
              <div className="mt-4 flex justify-end gap-2">
                <Button type="button" variant="outline" onClick={onCancelJoin}>Cancel</Button>
                <Button type="submit" className="bg-zinc-950 text-white hover:bg-zinc-800">
                  <Send /> Submit request
                </Button>
              </div>
            </form>
          )}

          {trip.ownedByViewer && (
            <div className="flex flex-col gap-4 rounded-2xl bg-zinc-950 p-5 text-white sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p className="text-xs font-bold uppercase tracking-[0.18em] text-emerald-400">Organizer tools</p>
                <p className="mt-1 font-semibold">{trip.participantEmails.length} traveler emails ready in BCC</p>
              </div>
              <Button type="button" onClick={onEmail} className="h-10 bg-white px-4 text-zinc-950 hover:bg-zinc-100">
                <Mail /> Email participants
              </Button>
            </div>
          )}
        </div>

        {!joinFormOpen && !joined && !trip.ownedByViewer && (
          <DialogFooter className="mx-0 mb-0 rounded-b-[2rem] px-6 sm:px-8">
            <p className="mr-auto self-center text-sm text-zinc-500">
              {isFull ? "This trip has reached its group limit." : `${trip.maxMembers - trip.memberCount} places are still available.`}
            </p>
            <Button
              type="button"
              disabled={isFull}
              onClick={onShowJoinForm}
              className="h-11 bg-zinc-950 px-5 text-white hover:bg-zinc-800"
            >
              <UserPlus /> Request to join
            </Button>
          </DialogFooter>
        )}
      </DialogContent>
    </Dialog>
  );
}

function DetailFact({ icon, label, value }: { icon: ReactNode; label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-4">
      <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wide text-emerald-700 [&_svg]:size-4">
        {icon}
        {label}
      </div>
      <p className="mt-2 text-sm font-semibold leading-5 text-zinc-900">{value}</p>
    </div>
  );
}

function Field({
  label,
  htmlFor,
  className = "",
  children,
}: {
  label: string;
  htmlFor: string;
  className?: string;
  children: ReactNode;
}) {
  return (
    <div className={className}>
      <Label htmlFor={htmlFor} className="mb-2 block font-semibold">{label}</Label>
      {children}
    </div>
  );
}

function CreateTripDialog({
  open,
  onOpenChange,
  onSubmit,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (event: SubmitEvent<HTMLFormElement>) => void;
}) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[92svh] overflow-y-auto rounded-[2rem] p-0 sm:max-w-4xl">
        <div className="border-b border-zinc-200 px-6 py-6 sm:px-8">
          <DialogHeader className="pr-10">
            <p className="text-xs font-bold uppercase tracking-[0.2em] text-emerald-700">Create a public trip</p>
            <DialogTitle className="text-3xl font-black tracking-tight">List the complete plan</DialogTitle>
            <DialogDescription>
              Every trip is visible to everyone. Travelers can request to join, but you decide how and when to confirm them.
            </DialogDescription>
          </DialogHeader>
        </div>

        <form onSubmit={onSubmit} className="space-y-8 px-6 pb-6 sm:px-8">
          <FormSection number="01" title="Route and schedule">
            <div className="grid gap-4 sm:grid-cols-2">
              <Field label="Trip title" htmlFor="trip-title" className="sm:col-span-2">
                <Input id="trip-title" name="title" required placeholder="Cloudy Sajek weekend" className="h-11" />
              </Field>
              <Field label="Leaving from" htmlFor="trip-origin">
                <Input id="trip-origin" name="origin" required placeholder="Dhaka" className="h-11" />
              </Field>
              <Field label="Destination" htmlFor="trip-destination">
                <Input id="trip-destination" name="destination" required placeholder="Sajek Valley" className="h-11" />
              </Field>
              <Field label="Departure date and time" htmlFor="trip-start">
                <Input id="trip-start" name="startAt" type="datetime-local" required className="h-11" />
              </Field>
              <Field label="Return date and time" htmlFor="trip-end">
                <Input id="trip-end" name="endAt" type="datetime-local" required className="h-11" />
              </Field>
              <Field label="Meeting point" htmlFor="trip-meeting" className="sm:col-span-2">
                <Input id="trip-meeting" name="meetingPoint" required placeholder="Exact place where everyone will meet" className="h-11" />
              </Field>
            </div>
          </FormSection>

          <FormSection number="02" title="Trip plan">
            <div className="grid gap-4 sm:grid-cols-2">
              <Field label="How will you travel?" htmlFor="trip-transport">
                <Input id="trip-transport" name="transport" required placeholder="Night bus, then reserved jeep" className="h-11" />
              </Field>
              <Field label="Estimated cost per person" htmlFor="trip-cost">
                <Input id="trip-cost" name="estimatedCost" required placeholder="৳5,000–6,000" className="h-11" />
              </Field>
              <Field label="Maximum group size" htmlFor="trip-size">
                <Input id="trip-size" name="maxMembers" type="number" min="2" max="50" defaultValue="6" required className="h-11" />
              </Field>
              <Field label="Short description" htmlFor="trip-description" className="sm:col-span-2">
                <Textarea id="trip-description" name="description" required placeholder="What kind of trip is this, and who will enjoy it?" className="min-h-24" />
              </Field>
              <Field label="Day-by-day plan" htmlFor="trip-itinerary" className="sm:col-span-2">
                <Textarea id="trip-itinerary" name="itinerary" required placeholder="Explain the route, stops, accommodation and return plan..." className="min-h-28" />
              </Field>
              <Field label="What travelers should know" htmlFor="trip-requirements" className="sm:col-span-2">
                <Textarea id="trip-requirements" name="requirements" required placeholder={"One requirement per line\nCarry a photo ID\nComfortable with shared rooms"} className="min-h-24" />
              </Field>
            </div>
          </FormSection>

          <FormSection number="03" title="Organizer and communication">
            <div className="grid gap-4 sm:grid-cols-2">
              <Field label="Your name" htmlFor="organizer-name">
                <Input id="organizer-name" name="organizerName" required placeholder="Organizer name" className="h-11" />
              </Field>
              <Field label="Your email" htmlFor="organizer-email">
                <Input id="organizer-email" name="organizerEmail" type="email" required placeholder="you@example.com" className="h-11" />
              </Field>
              <Field label="Group communication platform" htmlFor="trip-platform">
                <select
                  id="trip-platform"
                  name="communicationPlatform"
                  className="h-11 w-full rounded-lg border border-input bg-transparent px-3 text-sm outline-none focus:border-ring focus:ring-3 focus:ring-ring/50"
                  defaultValue="WhatsApp"
                >
                  <option>WhatsApp</option>
                  <option>Telegram</option>
                  <option>Messenger</option>
                </select>
              </Field>
              <Field label="How will travelers receive the group link?" htmlFor="trip-communication-note">
                <Input
                  id="trip-communication-note"
                  name="communicationNote"
                  required
                  defaultValue="Confirmed travelers receive the private group link by email."
                  className="h-11"
                />
              </Field>
            </div>
          </FormSection>

          <div className="sticky bottom-0 -mx-6 flex flex-col-reverse gap-2 border-t bg-white/95 px-6 py-4 backdrop-blur sm:-mx-8 sm:flex-row sm:justify-end sm:px-8">
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)} className="h-11 px-5">Cancel</Button>
            <Button type="submit" className="h-11 bg-zinc-950 px-5 text-white hover:bg-zinc-800">
              <Plus /> Publish trip
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}

function FormSection({
  number,
  title,
  children,
}: {
  number: string;
  title: string;
  children: ReactNode;
}) {
  return (
    <section>
      <div className="mb-4 flex items-center gap-3">
        <span className="flex size-8 items-center justify-center rounded-full bg-emerald-100 text-xs font-black text-emerald-800">{number}</span>
        <h3 className="text-lg font-black">{title}</h3>
      </div>
      {children}
    </section>
  );
}
