import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { SocialMapMap } from "@/components/social-map/SocialMapMap";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { communityMapPointsQueryOptions } from "@/services/community.service";
import {
  deleteMyLocation,
  myUserLocationQueryOptions,
  nearbyUserLocationsQueryOptions,
  upsertMyLocation,
} from "@/services/user-location.service";
import type { UserLocation, UserTravelStatus } from "@/types/user-location";

const DEFAULT_CENTER = { latitude: 23.8103, longitude: 90.4125 }; // Dhaka

export const Route = createFileRoute("/_authenticated/social-map/")({
  component: SocialMapPage,
});

type MapTilerPlace = {
  id?: string;
  place_name?: string;
  center?: [number, number];
};

function SocialMapPage() {
  const queryClient = useQueryClient();
  const [showUsers, setShowUsers] = useState(true);
  const [showEntries, setShowEntries] = useState(true);
  const [center, setCenter] = useState(DEFAULT_CENTER);
  const [status, setStatus] = useState<UserTravelStatus>("traveling");
  const [message, setMessage] = useState("");
  const [placeQuery, setPlaceQuery] = useState("");
  const [placeResults, setPlaceResults] = useState<MapTilerPlace[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [isGpsLoading, setIsGpsLoading] = useState(false);
  const [locationNotice, setLocationNotice] = useState<string | null>(null);
  const [optimisticMyLocation, setOptimisticMyLocation] = useState<UserLocation | null>(null);

  const { data: myLoc } = useQuery(myUserLocationQueryOptions());

  // Center the map on my saved location (if any)
  useEffect(() => {
    if (!myLoc) return;
    setCenter({ latitude: myLoc.latitude, longitude: myLoc.longitude });
    setStatus((myLoc.status as UserTravelStatus) ?? "traveling");
    setMessage(myLoc.message ?? "");
    setOptimisticMyLocation(null);
  }, [myLoc]);

  const upsertMutation = useMutation({
    mutationFn: upsertMyLocation,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["user-locations"] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: deleteMyLocation,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["user-locations"] });
    },
  });

  const { data: users = [] } = useQuery(
    nearbyUserLocationsQueryOptions({
      lat: center.latitude,
      lng: center.longitude,
      radius_km: 50,
    }),
  );

  const { data: entries = [] } = useQuery(
    communityMapPointsQueryOptions({
      limit: 2000,
    }),
  );

  const mapTilerKey = import.meta.env.VITE_MAPTILER_KEY as string | undefined;

  const effectiveMyLocation = myLoc ?? optimisticMyLocation;
  const hasMyLocation = Boolean(effectiveMyLocation);
  const communityPinsCount = entries.filter(
    (e) => e.latitude != null && e.longitude != null,
  ).length;

  const saveLocation = async (lat: number, lng: number) => {
    const saved = await upsertMutation.mutateAsync({
      latitude: lat,
      longitude: lng,
      status,
      message: message.trim() ? message.trim() : null,
    });
    setOptimisticMyLocation(saved);
    setLocationNotice("Location shared successfully.");
  };

  const shareGps = async () => {
    if (isGpsLoading || upsertMutation.isPending) return;
    setLocationNotice(null);
    if (!("geolocation" in navigator)) {
      setLocationNotice("Geolocation is not available in this browser.");
      return;
    }
    setIsGpsLoading(true);
    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        const lat = pos.coords.latitude;
        const lng = pos.coords.longitude;
        setCenter({ latitude: lat, longitude: lng });
        try {
          await saveLocation(lat, lng);
        } finally {
          setIsGpsLoading(false);
        }
      },
      (err) => {
        setIsGpsLoading(false);
        if (err.code === 1) {
          setLocationNotice("Location permission denied. Allow location access and try again.");
        } else if (err.code === 2) {
          setLocationNotice("Could not detect your current location.");
        } else if (err.code === 3) {
          setLocationNotice("Location request timed out. Try again.");
        } else {
          setLocationNotice("Failed to get your GPS location.");
        }
      },
      { enableHighAccuracy: true, timeout: 10_000 },
    );
  };

  const searchPlaces = useMemo(() => {
    let t: number | undefined;
    return (q: string) => {
      if (!mapTilerKey) return;
      window.clearTimeout(t);
      t = window.setTimeout(async () => {
        const trimmed = q.trim();
        if (trimmed.length < 3) {
          setPlaceResults([]);
          return;
        }
        setIsSearching(true);
        try {
          const url = new URL(
            `https://api.maptiler.com/geocoding/${encodeURIComponent(trimmed)}.json`,
          );
          url.searchParams.set("key", mapTilerKey);
          url.searchParams.set("country", "bd");
          url.searchParams.set("limit", "8");
          const res = await fetch(url.toString());
          const data = (await res.json()) as { features?: MapTilerPlace[] };
          setPlaceResults(data.features ?? []);
        } catch {
          setPlaceResults([]);
        } finally {
          setIsSearching(false);
        }
      }, 350);
    };
  }, [mapTilerKey]);

  useEffect(() => {
    if (!placeQuery) {
      setPlaceResults([]);
      return;
    }
    searchPlaces(placeQuery);
  }, [placeQuery, searchPlaces]);

  return (
    <div className="container mx-auto py-8 px-4">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Social Map</h1>
          <p className="text-muted-foreground mt-1">
            See where travelers are now, and explore community places with map pins.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant={showUsers ? "default" : "secondary"}
            onClick={() => setShowUsers((v) => !v)}
          >
            Users
          </Button>
          <Button
            variant={showEntries ? "default" : "secondary"}
            onClick={() => setShowEntries((v) => !v)}
          >
            Community
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-9">
          <div className="h-[70vh] min-h-[520px]">
            <SocialMapMap
              center={center}
              myLocation={effectiveMyLocation}
              users={users}
              entries={entries}
              showUsers={showUsers}
              showEntries={showEntries}
              onCenterChanged={(next) => {
                const diff =
                  Math.abs(next.latitude - center.latitude) +
                  Math.abs(next.longitude - center.longitude);
                // Avoid noisy refetches when only zoom changes or center drift is tiny.
                if (diff < 0.001) return;
                setCenter(next);
              }}
            />
          </div>
        </div>

        <div className="lg:col-span-3 space-y-4">
          <Card className="p-4 space-y-3">
            <div className="text-sm font-semibold">Share your location</div>

            <div className="space-y-2">
              <div className="text-xs text-muted-foreground">Status</div>
              <Select value={status} onValueChange={(v) => setStatus(v as UserTravelStatus)}>
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Select status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectGroup>
                    <SelectItem value="traveling">Traveling</SelectItem>
                    <SelectItem value="planning">Planning</SelectItem>
                    <SelectItem value="offline">Offline</SelectItem>
                  </SelectGroup>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <div className="text-xs text-muted-foreground">Message (optional)</div>
              <Input
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Looking for a travel buddy…"
              />
            </div>

            <div className="flex flex-col gap-2">
              <Button
                variant="default"
                onClick={shareGps}
                disabled={isGpsLoading || upsertMutation.isPending}
              >
                {isGpsLoading ? "Getting GPS..." : "Share GPS location"}
              </Button>
              <div className="text-xs text-muted-foreground">Or search a place</div>
              <Input
                value={placeQuery}
                onChange={(e) => setPlaceQuery(e.target.value)}
                placeholder={mapTilerKey ? "Search in Bangladesh…" : "Missing VITE_MAPTILER_KEY"}
                disabled={!mapTilerKey || upsertMutation.isPending}
              />
              {isSearching ? (
                <div className="text-xs text-muted-foreground">Searching…</div>
              ) : null}
              {placeResults.length ? (
                <div className="max-h-48 overflow-auto rounded-lg border bg-background">
                  {placeResults.slice(0, 8).map((p, idx) => {
                    const lng = Number(p.center?.[0]);
                    const lat = Number(p.center?.[1]);
                    const label = p.place_name ?? "Unnamed place";
                    const disabled = !Number.isFinite(lat) || !Number.isFinite(lng);
                    return (
                      <button
                        key={`${p.id ?? idx}`}
                        type="button"
                        disabled={disabled}
                        onClick={async () => {
                          if (!Number.isFinite(lat) || !Number.isFinite(lng)) return;
                          setCenter({ latitude: lat, longitude: lng });
                          setPlaceQuery(label);
                          setPlaceResults([]);
                          await saveLocation(lat, lng);
                        }}
                        className="w-full text-left px-3 py-2 text-sm hover:bg-muted disabled:opacity-50 disabled:hover:bg-transparent"
                      >
                        {label || "Unnamed place"}
                      </button>
                    );
                  })}
                </div>
              ) : null}

              {hasMyLocation ? (
                <Button
                  variant="secondary"
                  onClick={() => {
                    setOptimisticMyLocation(null);
                    setLocationNotice("Stopped sharing your location.");
                    deleteMutation.mutate();
                  }}
                  disabled={deleteMutation.isPending}
                >
                  Stop sharing
                </Button>
              ) : null}
              {locationNotice ? (
                <div className="text-xs text-muted-foreground">{locationNotice}</div>
              ) : null}
            </div>
          </Card>

          <Card className="p-4">
            <div className="text-sm font-semibold mb-2">Nearby travelers</div>
            <div className="text-sm text-muted-foreground">
              {users.length} other user{users.length === 1 ? "" : "s"} in view
            </div>
            <div className="text-xs text-muted-foreground mt-1">
              Your own pin is shown separately as "You".
            </div>
          </Card>

          <Card className="p-4">
            <div className="text-sm font-semibold mb-2">Community pins</div>
            <div className="text-sm text-muted-foreground">
              {communityPinsCount} entries with coordinates
            </div>
            {communityPinsCount === 0 ? (
              <div className="text-xs text-muted-foreground mt-1">
                Add community entries with latitude/longitude to see pins.
              </div>
            ) : null}
          </Card>
        </div>
      </div>
    </div>
  );
}

