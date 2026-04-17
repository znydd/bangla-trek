import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { Banknote, Clock3 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { fareEstimateQueryOptions } from "@/services/transit-fare.service";
import type { TransitFareMode, TransitFareModeEstimate } from "@/types/transit-fare";

interface FareEstimateChipsProps {
  origin: string;
  destination: string;
  className?: string;
}

const modeLabel: Record<TransitFareMode, string> = {
  cng: "CNG",
  bus: "Bus",
  train: "Train",
};

const modeOrder: TransitFareMode[] = ["cng", "bus", "train"];

function relativeDaysText(value: string | null): string {
  if (!value) return "no updates";
  const ts = new Date(value).getTime();
  if (Number.isNaN(ts)) return "no updates";
  const days = Math.floor((Date.now() - ts) / (1000 * 60 * 60 * 24));
  if (days <= 0) return "today";
  if (days === 1) return "1 day ago";
  return `${days} days ago`;
}

function getEstimateByMode(
  estimates: TransitFareModeEstimate[] | undefined,
  mode: TransitFareMode,
) {
  return estimates?.find((item) => item.mode === mode) ?? null;
}

export function FareEstimateChips({
  origin,
  destination,
  className,
}: FareEstimateChipsProps) {
  const { data, isLoading } = useQuery(
    fareEstimateQueryOptions(origin, destination),
  );

  const newestUpdate = useMemo(() => {
    const timestamps =
      data?.estimates
        .map((item) => item.last_updated_at)
        .filter((value): value is string => Boolean(value)) ?? [];
    if (timestamps.length === 0) return null;
    const sorted = timestamps.sort();
    return sorted[sorted.length - 1] ?? null;
  }, [data?.estimates]);

  return (
    <div className={className}>
      <div className="mb-2 flex items-center gap-2 text-xs text-muted-foreground">
        <Banknote className="h-3.5 w-3.5" />
        <span className="font-medium">Community Fare Estimate</span>
      </div>

      <div className="flex flex-wrap gap-2">
        {modeOrder.map((mode) => {
          const estimate = getEstimateByMode(data?.estimates, mode);
          return (
            <Badge
              key={mode}
              variant="outline"
              className="h-7 rounded-md px-2 text-xs font-medium"
            >
              {modeLabel[mode]}:{" "}
              {isLoading
                ? "..."
                : estimate?.median_fare_bdt != null
                  ? `৳${estimate.median_fare_bdt.toLocaleString()}`
                  : "N/A"}
            </Badge>
          );
        })}
      </div>

      <div className="mt-2 flex items-center gap-2 text-[11px] text-muted-foreground">
        <Clock3 className="h-3 w-3" />
        <span>
          {isLoading
            ? "Checking latest submissions..."
            : `${data?.estimates.reduce((sum, item) => sum + item.submission_count, 0) ?? 0} submissions, updated ${relativeDaysText(newestUpdate)}`}
        </span>
      </div>
    </div>
  );
}
