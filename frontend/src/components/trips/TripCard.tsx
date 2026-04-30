import { Link } from "@tanstack/react-router";
import { Card, CardContent, CardFooter, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { GroupTrip } from "@/types/group-trip";
import { MapPin, Calendar, Users, Lock, Globe } from "lucide-react";

interface TripCardProps {
  trip: GroupTrip;
}

export function TripCard({ trip }: TripCardProps) {
  const startDate = new Date(trip.start_date).toLocaleDateString("en-GB", {
    day: "numeric",
    month: "short",
  });
  const endDate = new Date(trip.end_date).toLocaleDateString("en-GB", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });

  return (
    <Link
      to="/trips/$tripId"
      params={{ tripId: trip.id }}
      className="block group"
    >
      <Card className="overflow-hidden h-full transition-all hover:shadow-md border-border/50 group-hover:border-primary/20">
        {/* Colored header bar */}
        <div className="h-2 bg-gradient-to-r from-green-500 to-emerald-400" />

        <CardHeader className="p-4 pb-2">
          <div className="flex items-start justify-between gap-2">
            <h3 className="font-semibold text-lg leading-tight group-hover:text-primary transition-colors line-clamp-1">
              {trip.title}
            </h3>
            <Badge
              variant={trip.visibility === "public" ? "secondary" : "outline"}
              className="shrink-0"
            >
              {trip.visibility === "public" ? (
                <Globe size={12} className="mr-1" />
              ) : (
                <Lock size={12} className="mr-1" />
              )}
              {trip.visibility}
            </Badge>
          </div>
          <div className="flex items-center gap-1.5 text-sm text-muted-foreground">
            <MapPin size={14} className="shrink-0" />
            <span className="line-clamp-1">{trip.destination}</span>
          </div>
        </CardHeader>

        <CardContent className="p-4 pt-0 pb-2 space-y-2">
          {trip.description && (
            <p className="text-sm text-muted-foreground line-clamp-2">
              {trip.description}
            </p>
          )}
          <div className="flex items-center gap-3 text-xs font-medium text-muted-foreground">
            <div className="flex items-center gap-1">
              <Calendar size={12} />
              <span>
                {startDate} - {endDate}
              </span>
            </div>
            <div className="flex items-center gap-1">
              <Users size={12} />
              <span>
                {trip.member_count} member{trip.member_count !== 1 ? "s" : ""}
              </span>
            </div>
          </div>
        </CardContent>

        <CardFooter className="p-4 pt-2 text-xs text-muted-foreground flex justify-between items-center border-t mt-1">
          <div className="flex items-center gap-1.5">
            {trip.creator_picture_url ? (
              <img
                src={trip.creator_picture_url}
                alt={trip.creator_name}
                className="h-4 w-4 rounded-full"
              />
            ) : null}
            <span>by {trip.creator_name}</span>
          </div>
          <span>{new Date(trip.created_at).toLocaleDateString()}</span>
        </CardFooter>
      </Card>
    </Link>
  );
}
