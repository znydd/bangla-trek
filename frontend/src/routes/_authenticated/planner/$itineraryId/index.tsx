import { createFileRoute, Link } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { itineraryQueryOptions } from "@/services/itinerary.service";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { PlannerFarePanel } from "@/components/transit-fares/PlannerFarePanel";
import {
  ArrowLeft,
  MapPin,
  Clock,
  Wallet,
  Loader2,
  BedDouble,
} from "lucide-react";
import { useState } from "react";

export const Route = createFileRoute("/_authenticated/planner/$itineraryId/")({
  component: ItineraryViewPage,
});

const CATEGORY_COLORS: Record<string, string> = {
  food: "bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300",
  sightseeing: "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300",
  transport: "bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-300",
  rest: "bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300",
  activity: "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300",
  shopping: "bg-pink-100 text-pink-800 dark:bg-pink-900/30 dark:text-pink-300",
  culture: "bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-300",
};

const CATEGORY_EMOJI: Record<string, string> = {
  food: "🍛",
  sightseeing: "🏞️",
  transport: "🚐",
  rest: "😴",
  activity: "🎯",
  shopping: "🛍️",
  culture: "🎭",
};

function ItineraryViewPage() {
  const { itineraryId } = Route.useParams();
  const { data: itinerary, isLoading } = useQuery(
    itineraryQueryOptions(itineraryId)
  );
  const [activeDay, setActiveDay] = useState(1);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (!itinerary) {
    return (
      <div className="container mx-auto py-8 px-4 text-center">
        <p className="text-muted-foreground">Itinerary not found.</p>
        <Button variant="outline" className="mt-4" render={<Link to="/planner" />}>
          <ArrowLeft className="mr-2 h-4 w-4" /> Back to Planner
        </Button>
      </div>
    );
  }

  const dayNumbers = [...new Set(itinerary.activities.map((a) => a.day_number))].sort(
    (a, b) => a - b
  );
  const dayActivities = itinerary.activities.filter(
    (a) => a.day_number === activeDay
  );
  const totalCost = itinerary.activities.reduce(
    (sum, a) => sum + a.estimated_cost,
    0
  );
  const dayCost = dayActivities.reduce((sum, a) => sum + a.estimated_cost, 0);

  return (
    <div className="container mx-auto py-8 px-4 space-y-8">
      {/* Navigation */}
      <div className="flex items-center justify-between">
        <Button variant="ghost" size="sm" render={<Link to="/planner" />}>
          <ArrowLeft className="mr-2 h-4 w-4" /> Back to Planner
        </Button>
        <Button
          variant="outline"
          size="sm"
          render={
            <Link
              to="/planner/$itineraryId/accommodations"
              params={{ itineraryId }}
            />
          }
        >
          <BedDouble className="mr-2 h-4 w-4" /> Accommodations
        </Button>
      </div>

      {/* Header */}
      <div className="space-y-3">
        <div className="flex items-center gap-3 flex-wrap">
          <h1 className="text-3xl font-bold tracking-tight">
            {itinerary.destination}
          </h1>
          <Badge variant="secondary">{itinerary.travel_style}</Badge>
          <Badge variant="outline">{itinerary.group_type}</Badge>
        </div>
        <div className="flex flex-wrap gap-4 text-sm text-muted-foreground">
          <span className="flex items-center gap-1">
            <Clock className="h-4 w-4" />
            {itinerary.duration_days} day{itinerary.duration_days > 1 ? "s" : ""}
          </span>
          <span className="flex items-center gap-1">
            <Wallet className="h-4 w-4" />
            Budget: ৳{itinerary.budget.toLocaleString()}
          </span>
          <span className="flex items-center gap-1">
            <Wallet className="h-4 w-4" />
            Estimated Total: ৳{totalCost.toLocaleString()}
          </span>
        </div>
        {itinerary.interests.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {itinerary.interests.map((interest) => (
              <Badge key={interest} variant="outline" className="text-xs">
                {interest}
              </Badge>
            ))}
          </div>
        )}
      </div>

      {/* Day Tabs */}
      <div className="flex gap-2 overflow-x-auto pb-2">
        {dayNumbers.map((day) => (
          <button
            key={day}
            onClick={() => setActiveDay(day)}
            className={`
              px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap
              transition-colors cursor-pointer
              ${activeDay === day
                ? "bg-primary text-primary-foreground"
                : "bg-muted text-muted-foreground hover:bg-accent"
              }
            `}
          >
            Day {day}
          </button>
        ))}
      </div>

      {/* Day Cost Summary */}
      <div className="flex items-center justify-between text-sm text-muted-foreground border-b pb-3">
        <span className="font-medium">Day {activeDay} Activities</span>
        <span>Day cost: ৳{dayCost.toLocaleString()}</span>
      </div>

      {/* Timeline */}
      <div className="space-y-4">
        {dayActivities.map((activity, idx) => (
          <div key={activity.id} className="flex gap-4">
            {/* Time column */}
            <div className="w-20 shrink-0 text-right pt-4">
              <p className="text-sm font-mono font-semibold">{activity.start_time}</p>
              <p className="text-xs text-muted-foreground font-mono">
                {activity.end_time}
              </p>
            </div>

            {/* Timeline line */}
            <div className="flex flex-col items-center">
              <div className="w-3 h-3 rounded-full bg-primary mt-5 shrink-0" />
              {idx < dayActivities.length - 1 && (
                <div className="w-0.5 flex-1 bg-border" />
              )}
            </div>

            {/* Content */}
            <Card className="flex-1 p-4 space-y-2">
              <div className="flex items-start justify-between gap-2">
                <div className="space-y-1">
                  <h3 className="font-semibold">
                    {CATEGORY_EMOJI[activity.category] || "📍"} {activity.title}
                  </h3>
                  <div className="flex items-center gap-2 flex-wrap">
                    <span
                      className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${CATEGORY_COLORS[activity.category] || CATEGORY_COLORS.activity
                        }`}
                    >
                      {activity.category}
                    </span>
                    <span className="text-xs text-muted-foreground flex items-center gap-1">
                      <MapPin className="h-3 w-3" />
                      {activity.location}
                    </span>
                  </div>
                </div>
                <Badge variant="secondary" className="shrink-0">
                  ৳{activity.estimated_cost.toLocaleString()}
                </Badge>
              </div>
              <p className="text-sm text-muted-foreground leading-relaxed">
                {activity.description}
              </p>
              {activity.category === "transport" && (
                <PlannerFarePanel
                  origin={
                    idx > 0
                      ? dayActivities[idx - 1].location
                      : itinerary.destination
                  }
                  destination={activity.location}
                />
              )}
            </Card>
          </div>
        ))}
      </div>

      {/* Total Summary */}
      <Card className="p-4 bg-primary/5">
        <div className="flex items-center justify-between">
          <div>
            <p className="font-semibold">Total Estimated Cost</p>
            <p className="text-sm text-muted-foreground">
              For {itinerary.duration_days} day{itinerary.duration_days > 1 ? "s" : ""} in{" "}
              {itinerary.destination}
            </p>
          </div>
          <div className="text-right">
            <p className="text-2xl font-bold">৳{totalCost.toLocaleString()}</p>
            <p className="text-sm text-muted-foreground">
              Budget: ৳{itinerary.budget.toLocaleString()}
            </p>
          </div>
        </div>
      </Card>
    </div>
  );
}
