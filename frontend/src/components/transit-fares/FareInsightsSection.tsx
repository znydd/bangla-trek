import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { Banknote, ExternalLink, Loader2, Trash2 } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import {
  bookingLinksQueryOptions,
  createFareContribution,
  deleteFareContribution,
  fareContributionsQueryOptions,
  fareEstimateQueryOptions,
} from "@/services/transit-fare.service";
import type { FareSourceType, TransitFareMode } from "@/types/transit-fare";

interface FareInsightsSectionProps {
  origin: string;
  destination: string;
  showBookingLinks?: boolean;
  className?: string;
}

const modeOptions: { value: TransitFareMode; label: string }[] = [
  { value: "cng", label: "CNG" },
  { value: "bus", label: "Bus" },
  { value: "train", label: "Train" },
];

const sourceOptions: { value: FareSourceType; label: string }[] = [
  { value: "observed", label: "Observed" },
  { value: "quoted", label: "Quoted by driver/counter" },
  { value: "booked", label: "Booked/Paid" },
];

function formatDate(value: string | null) {
  if (!value) return "No updates";
  return new Date(value).toLocaleDateString();
}

export function FareInsightsSection({
  origin,
  destination,
  showBookingLinks = true,
  className,
}: FareInsightsSectionProps) {
  const queryClient = useQueryClient();
  const { user } = useAuth();

  const [mode, setMode] = useState<TransitFareMode>("cng");
  const [fare, setFare] = useState("");
  const [minFare, setMinFare] = useState("");
  const [maxFare, setMaxFare] = useState("");
  const [travelDate, setTravelDate] = useState("");
  const [sourceType, setSourceType] = useState<FareSourceType>("observed");
  const [notes, setNotes] = useState("");

  const estimateQuery = useQuery(fareEstimateQueryOptions(origin, destination));
  const contributionsQuery = useQuery(
    fareContributionsQueryOptions({
      origin,
      destination,
      per_page: 6,
      page: 1,
    }),
  );
  const bookingLinksQuery = useQuery(bookingLinksQueryOptions());

  const createMutation = useMutation({
    mutationFn: createFareContribution,
    onSuccess: () => {
      toast.success("Fare contribution submitted.");
      setFare("");
      setMinFare("");
      setMaxFare("");
      setTravelDate("");
      setNotes("");
      queryClient.invalidateQueries({ queryKey: ["transit-fares"] });
    },
    onError: (error: any) => {
      toast.error(
        error?.response?.data?.detail || "Could not submit fare contribution.",
      );
    },
  });

  const deleteMutation = useMutation({
    mutationFn: deleteFareContribution,
    onSuccess: () => {
      toast.success("Fare contribution removed.");
      queryClient.invalidateQueries({ queryKey: ["transit-fares"] });
    },
    onError: (error: any) => {
      toast.error(
        error?.response?.data?.detail || "Could not delete fare contribution.",
      );
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const fareValue = Number(fare);
    if (!Number.isFinite(fareValue) || fareValue < 0) {
      toast.error("Please enter a valid fare amount.");
      return;
    }

    createMutation.mutate({
      origin,
      destination,
      mode,
      fare_bdt: fareValue,
      min_fare_bdt: minFare ? Number(minFare) : null,
      max_fare_bdt: maxFare ? Number(maxFare) : null,
      source_type: sourceType,
      travel_date: travelDate || null,
      notes: notes.trim() || null,
    });
  };

  const estimateRows = useMemo(() => {
    return modeOptions.map((modeOption) => {
      const estimate =
        estimateQuery.data?.estimates.find((row) => row.mode === modeOption.value) ??
        null;
      return { modeOption, estimate };
    });
  }, [estimateQuery.data?.estimates]);

  return (
    <section className={className}>
      <div className="mb-4 flex items-center gap-2">
        <Banknote className="h-5 w-5 text-primary" />
        <h2 className="text-xl font-semibold">Community Fare Intelligence</h2>
      </div>

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-3">
        <Card className="border-border/50 xl:col-span-2">
          <CardHeader className="pb-3">
            <h3 className="text-sm font-semibold">Route Estimate</h3>
            <p className="text-xs text-muted-foreground">
              {origin} → {destination}
            </p>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="grid grid-cols-1 gap-3 md:grid-cols-3">
              {estimateRows.map(({ modeOption, estimate }) => (
                <div
                  key={modeOption.value}
                  className="rounded-lg border border-border/60 p-3"
                >
                  <p className="text-xs text-muted-foreground">{modeOption.label}</p>
                  <p className="text-lg font-semibold">
                    {estimate?.median_fare_bdt != null
                      ? `৳${estimate.median_fare_bdt.toLocaleString()}`
                      : "N/A"}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {estimate?.submission_count ?? 0} submission
                    {(estimate?.submission_count ?? 0) === 1 ? "" : "s"}
                  </p>
                  {estimate?.is_low_data && (
                    <Badge variant="outline" className="mt-2 h-5 rounded-sm text-[10px]">
                      Low data
                    </Badge>
                  )}
                </div>
              ))}
            </div>

            <p className="text-xs text-muted-foreground">
              Last updated:{" "}
              {formatDate(
                (() => {
                  const values =
                    estimateQuery.data?.estimates
                  .map((e) => e.last_updated_at)
                  .filter((v): v is string => Boolean(v))
                  .sort() ?? [];
                  return values.length > 0 ? values[values.length - 1] : null;
                })(),
              )}
            </p>
          </CardContent>
        </Card>

        <Card className="border-border/50">
          <CardHeader className="pb-3">
            <h3 className="text-sm font-semibold">Contribute Fare</h3>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-3">
              <div className="space-y-1.5">
                <Label htmlFor="fare-mode">Mode</Label>
                <select
                  id="fare-mode"
                  value={mode}
                  onChange={(e) => setMode(e.target.value as TransitFareMode)}
                  className="flex h-8 w-full rounded-lg border border-input bg-transparent px-2.5 text-sm"
                >
                  {modeOptions.map((opt) => (
                    <option key={opt.value} value={opt.value}>
                      {opt.label}
                    </option>
                  ))}
                </select>
              </div>

              <div className="space-y-1.5">
                <Label htmlFor="fare-amount">Fare (BDT)</Label>
                <Input
                  id="fare-amount"
                  type="number"
                  min={0}
                  step="0.01"
                  value={fare}
                  onChange={(e) => setFare(e.target.value)}
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div className="space-y-1.5">
                  <Label htmlFor="fare-min">Min (optional)</Label>
                  <Input
                    id="fare-min"
                    type="number"
                    min={0}
                    step="0.01"
                    value={minFare}
                    onChange={(e) => setMinFare(e.target.value)}
                  />
                </div>
                <div className="space-y-1.5">
                  <Label htmlFor="fare-max">Max (optional)</Label>
                  <Input
                    id="fare-max"
                    type="number"
                    min={0}
                    step="0.01"
                    value={maxFare}
                    onChange={(e) => setMaxFare(e.target.value)}
                  />
                </div>
              </div>

              <div className="space-y-1.5">
                <Label htmlFor="fare-source">Source</Label>
                <select
                  id="fare-source"
                  value={sourceType}
                  onChange={(e) => setSourceType(e.target.value as FareSourceType)}
                  className="flex h-8 w-full rounded-lg border border-input bg-transparent px-2.5 text-sm"
                >
                  {sourceOptions.map((opt) => (
                    <option key={opt.value} value={opt.value}>
                      {opt.label}
                    </option>
                  ))}
                </select>
              </div>

              <div className="space-y-1.5">
                <Label htmlFor="fare-date">Travel Date (optional)</Label>
                <Input
                  id="fare-date"
                  type="date"
                  value={travelDate}
                  onChange={(e) => setTravelDate(e.target.value)}
                />
              </div>

              <div className="space-y-1.5">
                <Label htmlFor="fare-notes">Notes (optional)</Label>
                <Textarea
                  id="fare-notes"
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  rows={3}
                  placeholder="Counter fare, peak-hour differences, or route tips."
                />
              </div>

              <Button type="submit" className="w-full" disabled={createMutation.isPending}>
                {createMutation.isPending ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Submitting...
                  </>
                ) : (
                  "Submit Fare"
                )}
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>

      <div className="mt-6 grid grid-cols-1 gap-6 xl:grid-cols-3">
        <Card className="border-border/50 xl:col-span-2">
          <CardHeader className="pb-3">
            <h3 className="text-sm font-semibold">Recent Contributions</h3>
          </CardHeader>
          <CardContent className="space-y-3">
            {contributionsQuery.isLoading && (
              <p className="text-sm text-muted-foreground">Loading contributions...</p>
            )}
            {contributionsQuery.data?.items.length === 0 && (
              <p className="text-sm text-muted-foreground">
                No fare submissions yet for this route.
              </p>
            )}
            {contributionsQuery.data?.items.map((item) => (
              <div
                key={item.id}
                className="flex items-start justify-between gap-3 rounded-lg border border-border/60 p-3"
              >
                <div className="space-y-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <Badge variant="outline" className="rounded-sm px-1.5 py-0 text-[11px]">
                      {item.mode.toUpperCase()}
                    </Badge>
                    <span className="text-sm font-semibold">
                      ৳{item.fare_bdt.toLocaleString()}
                    </span>
                    <span className="text-xs text-muted-foreground">
                      by {item.author_name}
                    </span>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    {item.source_type} • submitted{" "}
                    {new Date(item.submitted_at).toLocaleDateString()}
                  </p>
                  {item.notes && (
                    <p className="text-sm text-muted-foreground">{item.notes}</p>
                  )}
                </div>

                {item.user_id === user?.id && (
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8 text-destructive"
                    onClick={() => deleteMutation.mutate(item.id)}
                    disabled={deleteMutation.isPending}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                )}
              </div>
            ))}
          </CardContent>
        </Card>

        {showBookingLinks && (
          <Card className="border-border/50">
            <CardHeader className="pb-3">
              <h3 className="text-sm font-semibold">Booking Websites</h3>
            </CardHeader>
            <CardContent className="space-y-2">
              {bookingLinksQuery.data?.items.map((item) => (
                <a
                  key={item.id}
                  href={item.url}
                  target="_blank"
                  rel="noreferrer"
                  className="flex items-center justify-between rounded-lg border border-border/60 px-3 py-2 text-sm hover:bg-muted/40"
                >
                  <span>{item.label}</span>
                  <ExternalLink className="h-3.5 w-3.5 text-muted-foreground" />
                </a>
              ))}
            </CardContent>
          </Card>
        )}
      </div>
    </section>
  );
}
