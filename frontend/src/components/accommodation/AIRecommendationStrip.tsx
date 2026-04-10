import { useQuery } from "@tanstack/react-query";
import { aiRecommendationsQueryOptions } from "@/services/accommodation.service";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Sparkles,
  Loader2,
  MapPin,
  Wallet,
  Star,
  RefreshCw,
  AlertTriangle,
  Hotel,
  Building2,
  Home,
} from "lucide-react";
import type { AIAccommodationRecommendation } from "@/types/accommodation";

interface AIRecommendationStripProps {
  itineraryId: string;
}

function getCategoryIcon(category: string) {
  switch (category) {
    case "hotel":
      return <Hotel size={16} className="text-blue-500" />;
    case "guesthouse":
      return <Building2 size={16} className="text-emerald-500" />;
    case "homestay":
      return <Home size={16} className="text-amber-500" />;
    default:
      return <Building2 size={16} />;
  }
}

function ConvenienceBar({ score }: { score: number }) {
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-500"
          style={{
            width: `${score * 10}%`,
            backgroundColor:
              score >= 8
                ? "var(--color-chart-2)"
                : score >= 5
                  ? "var(--color-chart-4)"
                  : "var(--color-destructive)",
          }}
        />
      </div>
      <span className="text-xs font-semibold tabular-nums w-8">{score}/10</span>
    </div>
  );
}

function RecommendationCard({ rec, index }: { rec: AIAccommodationRecommendation; index: number }) {
  const rankColors = [
    "from-amber-500/20 to-amber-500/5 border-amber-500/30",
    "from-slate-400/20 to-slate-400/5 border-slate-400/30",
    "from-orange-600/20 to-orange-600/5 border-orange-600/30",
  ];
  const rankLabels = ["🥇 Best Pick", "🥈 Runner Up", "🥉 Good Option"];

  return (
    <Card
      className={`p-5 bg-gradient-to-br ${rankColors[index] || rankColors[2]} border transition-all hover:shadow-md`}
    >
      <div className="space-y-3">
        {/* Header */}
        <div className="flex items-start justify-between gap-2">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold">{rankLabels[index]}</span>
            </div>
            <h4 className="font-semibold text-lg flex items-center gap-2">
              {getCategoryIcon(rec.category)}
              {rec.name}
            </h4>
          </div>
          <Badge variant="secondary" className="shrink-0 text-sm">
            ৳{rec.estimated_cost_per_night.toLocaleString()}/night
          </Badge>
        </div>

        {/* Location */}
        <div className="flex items-center gap-1.5 text-sm text-muted-foreground">
          <MapPin size={14} className="shrink-0" />
          <span>{rec.location}</span>
        </div>

        {/* Reasoning */}
        <p className="text-sm text-foreground/80 leading-relaxed">
          {rec.reasoning}
        </p>

        {/* Metrics */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
          <div className="space-y-1">
            <span className="text-xs font-medium text-muted-foreground flex items-center gap-1">
              <Star size={12} /> Travel Convenience
            </span>
            <ConvenienceBar score={rec.travel_convenience_score} />
          </div>
          <div className="space-y-1">
            <span className="text-xs font-medium text-muted-foreground flex items-center gap-1">
              <Wallet size={12} /> Cost-Benefit
            </span>
            <p className="text-xs leading-relaxed">{rec.cost_benefit_summary}</p>
          </div>
        </div>
      </div>
    </Card>
  );
}

export function AIRecommendationStrip({ itineraryId }: AIRecommendationStripProps) {
  const {
    data,
    isLoading,
    isError,
    error,
    refetch,
    isFetching,
  } = useQuery(aiRecommendationsQueryOptions(itineraryId));

  return (
    <div className="space-y-4">
      {/* Section Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="p-2 bg-primary/10 rounded-lg">
            <Sparkles size={20} className="text-primary" />
          </div>
          <div>
            <h2 className="text-lg font-semibold">AI Accommodation Picks</h2>
            <p className="text-xs text-muted-foreground">
              Strategically chosen to minimize your daily travel distances
            </p>
          </div>
        </div>
        {data && (
          <Button
            variant="ghost"
            size="sm"
            onClick={() => refetch()}
            disabled={isFetching}
            className="text-muted-foreground"
          >
            <RefreshCw size={14} className={`mr-1.5 ${isFetching ? "animate-spin" : ""}`} />
            Refresh
          </Button>
        )}
      </div>

      {/* Loading state */}
      {isLoading && (
        <Card className="p-8 flex flex-col items-center justify-center gap-3 bg-muted/20 border-dashed">
          <Loader2 size={24} className="animate-spin text-primary" />
          <div className="text-center">
            <p className="font-medium text-sm">Analyzing your itinerary...</p>
            <p className="text-xs text-muted-foreground">
              Our AI is finding the best-positioned accommodations for your trip
            </p>
          </div>
        </Card>
      )}

      {/* Error state */}
      {isError && (
        <Card className="p-6 flex items-center gap-3 bg-destructive/5 border-destructive/20">
          <AlertTriangle size={20} className="text-destructive shrink-0" />
          <div className="flex-1">
            <p className="font-medium text-sm">Failed to load AI recommendations</p>
            <p className="text-xs text-muted-foreground">
              {(error as Error)?.message || "Please try again later."}
            </p>
          </div>
          <Button variant="outline" size="sm" onClick={() => refetch()}>
            Retry
          </Button>
        </Card>
      )}

      {/* Results */}
      {data && (
        <div className="space-y-4">
          {/* Summary */}
          <Card className="p-4 bg-primary/5 border-primary/10">
            <p className="text-sm text-foreground/80 leading-relaxed">
              <span className="font-semibold">💡 AI Strategy: </span>
              {data.summary}
            </p>
          </Card>

          {/* Recommendation cards */}
          {data.recommendations.length > 0 ? (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
              {data.recommendations.map((rec, idx) => (
                <RecommendationCard
                  key={rec.accommodation_id}
                  rec={rec}
                  index={idx}
                />
              ))}
            </div>
          ) : (
            <Card className="p-6 text-center bg-muted/20 border-dashed">
              <p className="text-sm text-muted-foreground">
                No accommodations found in our database for this destination.
                Check back later as travelers contribute more data!
              </p>
            </Card>
          )}
        </div>
      )}
    </div>
  );
}
