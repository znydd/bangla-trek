import { useQuery } from "@tanstack/react-query";
import { ExternalLink } from "lucide-react";
import { bookingLinksQueryOptions } from "@/services/transit-fare.service";
import { FareEstimateChips } from "./FareEstimateChips";

interface PlannerFarePanelProps {
  origin: string;
  destination: string;
}

export function PlannerFarePanel({ origin, destination }: PlannerFarePanelProps) {
  const bookingLinksQuery = useQuery(bookingLinksQueryOptions());

  return (
    <div className="mt-3 rounded-lg border border-border/60 bg-muted/20 p-3">
      <FareEstimateChips origin={origin} destination={destination} />

      <div className="mt-3 flex flex-wrap gap-2">
        {bookingLinksQuery.data?.items.map((item) => (
          <a
            key={item.id}
            href={item.url}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-1 rounded-md border border-border/70 px-2 py-1 text-xs hover:bg-muted"
          >
            {item.label}
            <ExternalLink className="h-3 w-3" />
          </a>
        ))}
      </div>
    </div>
  );
}
