import { useEffect } from "react";
import { toast } from "sonner";
import { useQueryClient } from "@tanstack/react-query";

interface MessagingEvent {
  type: "POLL_VOTED" | "POLL_CREATED" | "ITINERARY_UPDATED" | "MEMBER_JOINED";
  message: string;
  tripId: string;
}

/**
 * A mock hook representing the Messaging API integration for real-time updates.
 * In a real implementation, this would connect to a WebSocket endpoint.
 */
export function useMessagingAPI(tripId: string) {
  const queryClient = useQueryClient();

  useEffect(() => {
    // This is where we would connect to the WebSocket:
    // const ws = new WebSocket(`ws://localhost:8000/ws/${tripId}`);
    // ws.onmessage = (event) => { handleEvent }
    
    // For demonstration of the UI, we simulate occasional real-time events.
    const interval = setInterval(() => {
      const events: MessagingEvent[] = [
        { type: "POLL_VOTED", message: "Rafiq just voted on 'Which hotel?'", tripId },
        { type: "ITINERARY_UPDATED", message: "Nusrat added a new activity to the itinerary.", tripId },
        { type: "MEMBER_JOINED", message: "A new member joined the trip!", tripId }
      ];
      
      const randomEvent = events[Math.floor(Math.random() * events.length)];
      
      // Show collaboration alert
      toast.info(randomEvent.message, {
        icon: randomEvent.type === "POLL_VOTED" ? "📊" : 
              randomEvent.type === "ITINERARY_UPDATED" ? "🗓️" : "👋"
      });
      
      // Trigger real-time updates in the UI
      if (randomEvent.type.startsWith("POLL")) {
        queryClient.invalidateQueries({ queryKey: ["polls", tripId] });
      } else if (randomEvent.type === "ITINERARY_UPDATED") {
        queryClient.invalidateQueries({ queryKey: ["itinerary", "trip", tripId] });
      }
      
    }, 15000); // Simulate every 15 seconds

    return () => clearInterval(interval);
  }, [tripId, queryClient]);

}
