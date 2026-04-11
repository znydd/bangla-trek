import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { MapPin, Loader2, Calendar } from "lucide-react";
import { toast } from "sonner";
import api from "@/lib/api";

export function CollaborativeItinerary({ tripId }: { tripId: string }) {
  const queryClient = useQueryClient();
  const [isInitializing, setIsInitializing] = useState(false);

  const { data: itinerary, isLoading, error } = useQuery({
    queryKey: ["itinerary", "trip", tripId],
    queryFn: async () => {
      const res = await api.get(`/api/v1/group-trips/${tripId}/itinerary`);
      return res.data;
    },
    retry: false,
    refetchInterval: 5000,
  });

  const generateItineraryMutation = useMutation({
    mutationFn: async () => {
      const res = await api.post(`/api/v1/group-trips/${tripId}/itinerary`);
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["itinerary", "trip", tripId] });
      setIsInitializing(false);
    },
    onError: () => {
      toast.error("Failed to initialize itinerary");
      setIsInitializing(false);
    }
  });

  if (isLoading) return <Skeleton className="h-[400px]" />;

  if (!itinerary) {
    return (
      <Card className="p-8 text-center space-y-4">
        <MapPin className="mx-auto h-12 w-12 text-muted-foreground opacity-50" />
        <div>
          <h3 className="font-semibold text-lg">No Itinerary Yet</h3>
          <p className="text-sm text-muted-foreground">Start collaborating on a travel plan with your group.</p>
        </div>
        <Button 
          onClick={() => {
            setIsInitializing(true);
            generateItineraryMutation.mutate();
          }}
          disabled={isInitializing}
        >
          {isInitializing ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" />Creating...</> : "Start Itinerary"}
        </Button>
      </Card>
    );
  }

  // Very basic rendering. Full editing can be implemented via modals and extra endpoints.
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-bold flex items-center gap-2">
          <Calendar /> Group Itinerary
        </h2>
      </div>
      
      <div className="space-y-4">
        {itinerary.activities?.length === 0 ? (
          <p className="text-sm text-muted-foreground text-center py-8">No activities yet. You can add them here.</p>
        ) : (
          itinerary.activities?.map((activity: any) => (
            <Card key={activity.id} className="p-4 flex gap-4">
              <div className="w-16 shrink-0 text-center">
                <span className="text-xs uppercase font-semibold text-muted-foreground">Day {activity.day_number}</span>
                <div className="font-bold text-lg">{activity.start_time}</div>
              </div>
              <div className="flex-1 space-y-1">
                <h4 className="font-semibold">{activity.title}</h4>
                <p className="text-sm text-muted-foreground">{activity.description}</p>
                <div className="text-xs flex gap-2 mt-2">
                  <span className="bg-muted px-2 py-0.5 rounded">{activity.category}</span>
                  <span className="text-emerald-600 font-medium">{activity.estimated_cost} BDT</span>
                </div>
              </div>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}
