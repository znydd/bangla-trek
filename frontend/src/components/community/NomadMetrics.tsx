import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { nomadMetricsQueryOptions, submitNomadMetric } from "@/services/nomad-metrics.service";
import type { Carrier, SignalStrength } from "@/types/nomad-metrics";
import {
  Wifi,
  ShieldCheck,
  Smartphone,
  Loader2,
  CheckCircle2,
  Signal,
  Users,
  TrendingUp,
} from "lucide-react";
import { Button } from "@/components/ui/button";

const CARRIERS: Carrier[] = ["GP", "Robi", "Banglalink", "Teletalk"];
const SIGNALS: SignalStrength[] = ["No Signal", "2G", "3G", "4G", "5G"];

const SIGNAL_COLOR: Record<string, string> = {
  "No Signal": "bg-red-500",
  "2G": "bg-orange-400",
  "3G": "bg-yellow-400",
  "4G": "bg-green-400",
  "5G": "bg-emerald-500",
};

const SIGNAL_TEXT_COLOR: Record<string, string> = {
  "No Signal": "text-red-500",
  "2G": "text-orange-400",
  "3G": "text-yellow-400",
  "4G": "text-green-400",
  "5G": "text-emerald-500",
};

const SIGNAL_BG_MUTED: Record<string, string> = {
  "No Signal": "bg-red-500/10 border-red-500/20",
  "2G": "bg-orange-400/10 border-orange-400/20",
  "3G": "bg-yellow-400/10 border-yellow-400/20",
  "4G": "bg-green-400/10 border-green-400/20",
  "5G": "bg-emerald-500/10 border-emerald-500/20",
};

interface NomadMetricsProps {
  entryId: string;
}

export function NomadMetrics({ entryId }: NomadMetricsProps) {
  const queryClient = useQueryClient();
  const { data, isLoading } = useQuery(nomadMetricsQueryOptions(entryId));

  const [carrier, setCarrier] = useState<Carrier>("GP");
  const [signal, setSignal] = useState<SignalStrength>("4G");
  const [safety, setSafety] = useState(3);
  const [bkash, setBkash] = useState(true);
  const [submitted, setSubmitted] = useState(false);

const { mutate, isPending } = useMutation({
    mutationFn: submitNomadMetric,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["nomad-metrics", entryId] });
      setSubmitted(true);
    },
    onError: (error: any) => {
      if (error?.response?.status === 409) {
        setSubmitted(true); // show the thank you screen, they already submitted
      }
    },
  });

  const handleSubmit = () => {
    mutate({
      entry_id: entryId,
      carrier,
      signal_strength: signal,
      safety_rating: safety,
      bkash_available: bkash,
    });
  };

  const hasData = data && data.signal_by_carrier.length > 0;
  const totalVotes = data?.signal_by_carrier.reduce((sum, s) => sum + s.votes, 0) ?? 0;
  const isSubmitted = submitted || Boolean(data?.has_submitted);

  return (
    <section className="w-full mt-10">
      {/* Header Band */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 border border-slate-700/50 px-8 py-8 mb-6">
        {/* Decorative grid overlay */}
        <div
          className="absolute inset-0 opacity-[0.04]"
          style={{
            backgroundImage:
              "linear-gradient(rgba(255,255,255,0.8) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.8) 1px, transparent 1px)",
            backgroundSize: "32px 32px",
          }}
        />
        {/* Glow blob */}
        <div className="absolute -top-12 -right-12 w-48 h-48 rounded-full bg-primary/20 blur-3xl" />
        <div className="absolute -bottom-8 -left-8 w-32 h-32 rounded-full bg-emerald-500/10 blur-2xl" />

        <div className="relative flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <div className="bg-primary/20 border border-primary/30 p-1.5 rounded-lg">
                <Signal size={16} className="text-primary" />
              </div>
              <span className="text-xs font-semibold tracking-[0.15em] uppercase text-primary">
                Community Intelligence
              </span>
            </div>
            <h2 className="text-3xl font-bold text-white tracking-tight">
              Nomad Metrics
            </h2>
            <p className="text-slate-400 text-sm mt-1 max-w-md">
              Real infrastructure data from travelers who've been here — signal strength, safety, and payment availability.
            </p>
          </div>
          {totalVotes > 0 && (
            <div className="flex items-center gap-2 bg-white/5 border border-white/10 rounded-xl px-4 py-3 shrink-0">
              <Users size={16} className="text-slate-400" />
              <div>
                <p className="text-white font-bold text-lg leading-none">{totalVotes}</p>
                <p className="text-slate-400 text-xs">contributions</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-16 gap-3 text-muted-foreground">
          <Loader2 size={20} className="animate-spin" />
          <span className="text-sm">Loading community data...</span>
        </div>
      ) : hasData ? (
        <>
          {/* Metric Cards Row */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
            {/* Safety Rating Card */}
            <div className="bg-card border border-border rounded-2xl p-6 flex flex-col gap-3">
              <div className="flex items-center justify-between">
                <div className="bg-yellow-400/10 border border-yellow-400/20 p-2 rounded-lg">
                  <ShieldCheck size={18} className="text-yellow-400" />
                </div>
                <span className="text-xs font-semibold tracking-wider uppercase text-muted-foreground">
                  Safety
                </span>
              </div>
              <div>
                <div className="text-4xl font-black tracking-tighter text-foreground">
                  {data.avg_safety_rating !== null
                    ? data.avg_safety_rating.toFixed(1)
                    : "—"}
                  <span className="text-xl text-muted-foreground font-normal"> / 5</span>
                </div>
                <p className="text-xs text-muted-foreground mt-1">Solo-female safety rating</p>
              </div>
              <div className="flex gap-0.5 mt-1">
                {[1, 2, 3, 4, 5].map((star) => (
                  <span
                    key={star}
                    className={`text-xl transition-all ${
                      star <= Math.round(data.avg_safety_rating ?? 0)
                        ? "text-yellow-400"
                        : "text-muted-foreground/20"
                    }`}
                  >
                    ★
                  </span>
                ))}
              </div>
            </div>

            {/* bKash Card */}
            <div className="bg-card border border-border rounded-2xl p-6 flex flex-col gap-3">
              <div className="flex items-center justify-between">
                <div className="bg-pink-500/10 border border-pink-500/20 p-2 rounded-lg">
                  <Smartphone size={18} className="text-pink-500" />
                </div>
                <span className="text-xs font-semibold tracking-wider uppercase text-muted-foreground">
                  bKash
                </span>
              </div>
              <div>
                <div className="text-4xl font-black tracking-tighter text-foreground">
                  {data.bkash_available_pct}
                  <span className="text-xl text-muted-foreground font-normal">%</span>
                </div>
                <p className="text-xs text-muted-foreground mt-1">Digital payment available</p>
              </div>
              <div className="h-2 w-full rounded-full bg-muted overflow-hidden mt-1">
                <div
                  className="h-full rounded-full bg-gradient-to-r from-pink-500 to-rose-400 transition-all duration-700"
                  style={{ width: `${data.bkash_available_pct}%` }}
                />
              </div>
            </div>

            {/* Best Signal Card */}
            <div className="bg-card border border-border rounded-2xl p-6 flex flex-col gap-3">
              <div className="flex items-center justify-between">
                <div className="bg-primary/10 border border-primary/20 p-2 rounded-lg">
                  <Wifi size={18} className="text-primary" />
                </div>
                <span className="text-xs font-semibold tracking-wider uppercase text-muted-foreground">
                  Best Signal
                </span>
              </div>
              {(() => {
                const best = data.signal_by_carrier[0];
                return best ? (
                  <div>
                    <div className={`text-4xl font-black tracking-tighter ${SIGNAL_TEXT_COLOR[best.signal] ?? "text-foreground"}`}>
                      {best.signal}
                    </div>
                    <p className="text-xs text-muted-foreground mt-1">
                      via {best.carrier} · {best.votes} vote{best.votes !== 1 ? "s" : ""}
                    </p>
                  </div>
                ) : (
                  <div className="text-muted-foreground text-sm">No data</div>
                );
              })()}
              <div className="flex gap-1.5 mt-1 flex-wrap">
                {SIGNALS.map((s) => {
                  const active = data.signal_by_carrier.some((x) => x.signal === s);
                  return (
                    <span
                      key={s}
                      className={`text-xs px-2 py-0.5 rounded-full border font-medium transition-all ${
                        active
                          ? `${SIGNAL_BG_MUTED[s]} ${SIGNAL_TEXT_COLOR[s]}`
                          : "bg-muted/30 border-transparent text-muted-foreground/40"
                      }`}
                    >
                      {s}
                    </span>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Network by Carrier - Full Width Table */}
          <div className="bg-card border border-border rounded-2xl p-6 mb-6">
            <div className="flex items-center gap-2 mb-5">
              <TrendingUp size={16} className="text-primary" />
              <h3 className="font-semibold text-sm tracking-wider uppercase text-muted-foreground">
                Network Coverage by Carrier
              </h3>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {CARRIERS.map((c) => {
                const top = data.signal_by_carrier.find((s) => s.carrier === c);
                return (
                  <div
                    key={c}
                    className={`rounded-xl border p-4 flex flex-col gap-2 transition-all ${
                      top
                        ? `${SIGNAL_BG_MUTED[top.signal]} `
                        : "bg-muted/20 border-border/50"
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-sm text-foreground">{c}</span>
                      {top && (
                        <span className={`w-2.5 h-2.5 rounded-full ${SIGNAL_COLOR[top.signal]}`} />
                      )}
                    </div>
                    {top ? (
                      <>
                        <span className={`text-xl font-black ${SIGNAL_TEXT_COLOR[top.signal]}`}>
                          {top.signal}
                        </span>
                        <span className="text-xs text-muted-foreground">
                          {top.votes} vote{top.votes !== 1 ? "s" : ""}
                        </span>
                      </>
                    ) : (
                      <span className="text-sm text-muted-foreground/50 italic">No data yet</span>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </>
      ) : (
        <div className="bg-card border border-dashed border-border rounded-2xl p-10 text-center mb-6">
          <div className="bg-muted/50 w-14 h-14 rounded-full flex items-center justify-center mx-auto mb-4">
            <Signal size={24} className="text-muted-foreground" />
          </div>
          <p className="font-semibold text-foreground mb-1">No metrics yet</p>
          <p className="text-sm text-muted-foreground">
            Be the first traveler to report on connectivity, safety, and bKash availability here.
          </p>
        </div>
      )}

      {/* Submission Form */}
      <div className="relative overflow-hidden bg-gradient-to-br from-primary/5 via-card to-card border border-primary/20 rounded-2xl p-8">
        <div className="absolute top-0 right-0 w-64 h-64 bg-primary/5 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2" />

        <div className="relative">
          <div className="mb-6">
            <h3 className="text-xl font-bold text-foreground mb-1">
              Share Your Experience
            </h3>
            <p className="text-sm text-muted-foreground">
              Help fellow travelers by reporting what you found on the ground.
            </p>
          </div>

          {isSubmitted ? (
            <div className="flex flex-col items-center py-8 gap-3">
              <div className="bg-primary/10 border border-primary/20 w-16 h-16 rounded-full flex items-center justify-center">
                <CheckCircle2 size={32} className="text-primary" />
              </div>
              <p className="font-semibold text-foreground text-lg">Thank you!</p>
              <p className="text-sm text-muted-foreground">Your data helps the Nomad community.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-8">
              {/* Left column */}
              <div className="space-y-6">
                {/* Carrier */}
                <div className="space-y-2">
                  <label className="text-xs font-semibold tracking-wider uppercase text-muted-foreground">
                    Your Carrier
                  </label>
                  <div className="flex flex-wrap gap-2">
                    {CARRIERS.map((c) => (
                      <button
                        key={c}
                        onClick={() => setCarrier(c)}
                        className={`px-4 py-2 rounded-xl text-sm font-medium border transition-all ${
                          carrier === c
                            ? "bg-primary text-primary-foreground border-primary shadow-lg shadow-primary/20 scale-105"
                            : "border-border hover:border-primary/50 hover:bg-primary/5"
                        }`}
                      >
                        {c}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Signal */}
                <div className="space-y-2">
                  <label className="text-xs font-semibold tracking-wider uppercase text-muted-foreground">
                    Signal Strength
                  </label>
                  <div className="flex flex-wrap gap-2">
                    {SIGNALS.map((s) => (
                      <button
                        key={s}
                        onClick={() => setSignal(s)}
                        className={`px-4 py-2 rounded-xl text-sm font-medium border transition-all ${
                          signal === s
                            ? `${SIGNAL_BG_MUTED[s]} ${SIGNAL_TEXT_COLOR[s]} border-current scale-105 shadow-sm`
                            : "border-border hover:border-primary/50 hover:bg-primary/5"
                        }`}
                      >
                        {s}
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              {/* Right column */}
              <div className="space-y-6">
                {/* Safety Rating */}
                <div className="space-y-2">
                  <label className="text-xs font-semibold tracking-wider uppercase text-muted-foreground">
                    Solo-Female Safety Rating
                  </label>
                  <div className="flex gap-2 items-center">
                    {[1, 2, 3, 4, 5].map((star) => (
                      <button
                        key={star}
                        onClick={() => setSafety(star)}
                        className="text-3xl transition-all duration-150 hover:scale-125 active:scale-110"
                      >
                        <span className={star <= safety ? "text-yellow-400" : "text-muted-foreground/20"}>
                          ★
                        </span>
                      </button>
                    ))}
                    <span className="text-sm text-muted-foreground ml-2 font-medium">
                      {safety} / 5
                    </span>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    {safety <= 2 ? "Caution advised" : safety === 3 ? "Generally safe" : safety === 4 ? "Quite safe" : "Very safe"}
                  </p>
                </div>

                {/* bKash */}
                <div className="space-y-2">
                  <label className="text-xs font-semibold tracking-wider uppercase text-muted-foreground">
                    bKash Available?
                  </label>
                  <div className="flex gap-3">
                    {[
                      { val: true, label: "✓ Yes, it works", color: "bg-emerald-500/10 border-emerald-500/30 text-emerald-600" },
                      { val: false, label: "✗ Not available", color: "bg-red-500/10 border-red-500/30 text-red-500" },
                    ].map(({ val, label, color }) => (
                      <button
                        key={String(val)}
                        onClick={() => setBkash(val)}
                        className={`flex-1 py-2.5 rounded-xl text-sm font-medium border transition-all ${
                          bkash === val
                            ? `${color} scale-[1.02] shadow-sm`
                            : "border-border hover:border-primary/50 hover:bg-primary/5"
                        }`}
                      >
                        {label}
                      </button>
                    ))}
                  </div>
                </div>

                <Button
                  onClick={handleSubmit}
                  disabled={isPending}
                  size="lg"
                  className="w-full mt-2 font-semibold tracking-wide"
                >
                  {isPending ? (
                    <>
                      <Loader2 size={16} className="mr-2 animate-spin" />
                      Submitting...
                    </>
                  ) : (
                    "Submit to Community Data →"
                  )}
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
