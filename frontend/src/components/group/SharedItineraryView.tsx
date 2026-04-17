import { useQuery } from "@tanstack/react-query";
import { itineraryQueryOptions } from "@/services/itinerary.service";
import { Card } from "@/components/ui/card";
import { Loader2, MapPin, Wallet, FileDown } from "lucide-react";
import { useState } from "react";
import { exportItineraryPdf } from "@/services/itinerary.service";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";

interface SharedItineraryViewProps {
  itineraryId: string;
}

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

export default function SharedItineraryView({ itineraryId }: SharedItineraryViewProps) {
  const { data: itinerary, isLoading } = useQuery(itineraryQueryOptions(itineraryId));
  const [activeDay, setActiveDay] = useState(1);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (!itinerary) {
    return (
      <div className="text-center py-12 text-muted-foreground">
        Itinerary could not be loaded.
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

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-bold">Trip Itinerary</h3>
        <Button 
          variant="outline" 
          size="sm" 
          className="h-8 gap-2 text-xs border-primary/20 hover:bg-primary/5 hover:text-primary transition-all rounded-full"
          onClick={async () => {
            try {
              toast.info("Preparing your PDF...");
              await exportItineraryPdf(itineraryId);
              toast.success("Download started!");
            } catch (err) {
              toast.error("Failed to generate PDF. Please try again.");
            }
          }}
        >
          <FileDown size={14} />
          Export PDF
        </Button>
      </div>

      <div className="flex border-b overflow-x-auto no-scrollbar">
        {dayNumbers.map((day) => (
          <button
            key={day}
            onClick={() => setActiveDay(day)}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors whitespace-nowrap ${
              activeDay === day
                ? "border-primary text-primary"
                : "border-transparent text-muted-foreground hover:text-foreground"
            }`}
          >
            Day {day}
          </button>
        ))}
      </div>

      <div className="space-y-4">
        {dayActivities.map((activity, idx) => (
          <div key={activity.id} className="flex gap-3">
             <div className="w-16 shrink-0 text-right pt-4">
              <p className="text-xs font-mono font-bold">{activity.start_time}</p>
              <p className="text-[10px] text-muted-foreground font-mono">
                {activity.end_time}
              </p>
            </div>
            
            <div className="flex flex-col items-center">
              <div className="w-2.5 h-2.5 rounded-full bg-primary mt-5 shrink-0" />
              {idx < dayActivities.length - 1 && (
                <div className="w-px flex-1 bg-border" />
              )}
            </div>

            <Card className="flex-1 p-3 space-y-2 border-shadow-sm">
              <div className="flex items-start justify-between gap-2">
                <div className="space-y-1">
                  <h4 className="font-semibold text-sm">
                    {CATEGORY_EMOJI[activity.category] || "📍"} {activity.title}
                  </h4>
                  <div className="flex items-center gap-2 flex-wrap">
                    <span
                      className={`inline-flex items-center rounded-full px-1.5 py-0.5 text-[10px] font-medium ${
                        CATEGORY_COLORS[activity.category] || CATEGORY_COLORS.activity
                      }`}
                    >
                      {activity.category}
                    </span>
                    <span className="text-[10px] text-muted-foreground flex items-center gap-1">
                      <MapPin className="h-2.5 w-2.5" />
                      {activity.location}
                    </span>
                  </div>
                </div>
                <div className="text-xs font-bold text-primary">৳{activity.estimated_cost.toLocaleString()}</div>
              </div>
              <p className="text-xs text-muted-foreground">
                {activity.description}
              </p>
            </Card>
          </div>
        ))}
        
        {dayActivities.length === 0 && (
            <p className="text-center text-sm text-muted-foreground py-4">No activities scheduled for this day.</p>
        )}
      </div>

      <div className="p-3 bg-muted/40 rounded-lg flex items-center justify-between text-xs">
        <div className="flex items-center gap-1 text-muted-foreground">
            <Wallet size={12} />
            <span>Itinerary Total Cost</span>
        </div>
        <div className="font-bold">৳{totalCost.toLocaleString()} / ৳{itinerary.budget.toLocaleString()}</div>
      </div>
    </div>
  );
}
