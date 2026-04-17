import { useEffect, useMemo, useRef } from "react";
import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";

import type { CommunityMapPoint } from "@/types/community";
import type { UserLocation, UserLocationPoint } from "@/types/user-location";

type Coordinate = { latitude: number; longitude: number };

const OSM_FALLBACK_STYLE: maplibregl.StyleSpecification = {
  version: 8,
  sources: {
    osm: {
      type: "raster",
      tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
      tileSize: 256,
      attribution: "&copy; OpenStreetMap contributors",
    },
  },
  layers: [{ id: "osm", type: "raster", source: "osm" }],
};

function createDot(color: string) {
  const el = document.createElement("div");
  el.style.width = "12px";
  el.style.height = "12px";
  el.style.borderRadius = "9999px";
  el.style.background = color;
  el.style.border = "2px solid white";
  el.style.boxShadow = "0 2px 10px rgba(0,0,0,0.25)";
  return el;
}

export type SocialMapMapProps = {
  center: Coordinate;
  zoom?: number;
  myLocation?: UserLocation | null;
  users: UserLocationPoint[];
  entries: CommunityMapPoint[];
  showUsers: boolean;
  showEntries: boolean;
  onCenterChanged?: (next: Coordinate) => void;
};

export function SocialMapMap({
  center,
  zoom = 11,
  myLocation,
  users,
  entries,
  showUsers,
  showEntries,
  onCenterChanged,
}: SocialMapMapProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);
  const onCenterChangedRef = useRef<typeof onCenterChanged>(onCenterChanged);
  const myMarkerRef = useRef<maplibregl.Marker | null>(null);
  const userMarkersRef = useRef<Map<string, maplibregl.Marker>>(new Map());
  const entryMarkersRef = useRef<Map<string, maplibregl.Marker>>(new Map());

  useEffect(() => {
    onCenterChangedRef.current = onCenterChanged;
  }, [onCenterChanged]);

  const style = useMemo(() => {
    const key = import.meta.env.VITE_MAPTILER_KEY as string | undefined;
    if (key) {
      return `https://api.maptiler.com/maps/streets-v2/style.json?key=${key}`;
    }
    return OSM_FALLBACK_STYLE;
  }, []);

  // Initialize map once
  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;

    const map = new maplibregl.Map({
      container: containerRef.current,
      style,
      center: [center.longitude, center.latitude],
      zoom,
    });
    mapRef.current = map;

    map.addControl(new maplibregl.NavigationControl({ showCompass: false }), "top-right");

    map.on("moveend", () => {
      if (!onCenterChangedRef.current) return;
      const c = map.getCenter();
      onCenterChangedRef.current({ latitude: c.lat, longitude: c.lng });
    });

    return () => {
      map.remove();
      mapRef.current = null;
    };
  }, [style, zoom]);

  // Fly map if center prop changes (after initialization)
  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;
    const current = map.getCenter();
    const dist =
      Math.abs(current.lat - center.latitude) + Math.abs(current.lng - center.longitude);
    if (dist < 0.0001) return;
    map.easeTo({ center: [center.longitude, center.latitude], duration: 500 });
  }, [center.latitude, center.longitude]);

  // Update user markers
  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;

    // remove if hidden
    if (!showUsers) {
      userMarkersRef.current.forEach((m) => m.remove());
      userMarkersRef.current.clear();
      return;
    }

    const nextIds = new Set(users.map((u) => u.user_id));

    // remove old
    for (const [id, marker] of userMarkersRef.current.entries()) {
      if (!nextIds.has(id)) {
        marker.remove();
        userMarkersRef.current.delete(id);
      }
    }

    // add/update
    for (const u of users) {
      const id = u.user_id;
      const popup = new maplibregl.Popup({ offset: 16 }).setHTML(
        `<div style="min-width:180px">
           <div style="font-weight:600">${u.user_name ?? "Traveler"}</div>
           <div style="font-size:12px;opacity:0.8">${u.status ?? "traveling"}</div>
           ${u.message ? `<div style="margin-top:6px;font-size:12px">${u.message}</div>` : ""}
         </div>`,
      );

      const existing = userMarkersRef.current.get(id);
      if (existing) {
        existing.setLngLat([u.longitude, u.latitude]).setPopup(popup);
        continue;
      }

      const marker = new maplibregl.Marker({ element: createDot("#2563eb") })
        .setLngLat([u.longitude, u.latitude])
        .setPopup(popup)
        .addTo(map);

      userMarkersRef.current.set(id, marker);
    }
  }, [showUsers, users]);

  // Always show current user's own shared location (if present)
  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;

    if (!myLocation || !showUsers) {
      myMarkerRef.current?.remove();
      myMarkerRef.current = null;
      return;
    }

    const popup = new maplibregl.Popup({ offset: 16 }).setHTML(
      `<div style="min-width:180px">
         <div style="font-weight:600">You</div>
         <div style="font-size:12px;opacity:0.8">${myLocation.status ?? "traveling"}</div>
         ${myLocation.message ? `<div style="margin-top:6px;font-size:12px">${myLocation.message}</div>` : ""}
       </div>`,
    );

    if (myMarkerRef.current) {
      myMarkerRef.current
        .setLngLat([myLocation.longitude, myLocation.latitude])
        .setPopup(popup);
      return;
    }

    myMarkerRef.current = new maplibregl.Marker({ element: createDot("#ef4444") })
      .setLngLat([myLocation.longitude, myLocation.latitude])
      .setPopup(popup)
      .addTo(map);
  }, [myLocation, showUsers]);

  // Update community entry markers
  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;

    if (!showEntries) {
      entryMarkersRef.current.forEach((m) => m.remove());
      entryMarkersRef.current.clear();
      return;
    }

    const withCoords = entries.filter(
      (e) => typeof e.latitude === "number" && typeof e.longitude === "number",
    );
    const nextIds = new Set(withCoords.map((e) => e.id));

    for (const [id, marker] of entryMarkersRef.current.entries()) {
      if (!nextIds.has(id)) {
        marker.remove();
        entryMarkersRef.current.delete(id);
      }
    }

    for (const e of withCoords) {
      const popup = new maplibregl.Popup({ offset: 16 }).setHTML(
        `<div style="min-width:180px">
           <div style="font-weight:600">${e.name}</div>
           <div style="font-size:12px;opacity:0.8">${e.location}</div>
           <div style="margin-top:6px">
             <a href="/community/${e.id}" style="font-size:12px;color:#16a34a;text-decoration:underline">View entry</a>
           </div>
         </div>`,
      );

      const existing = entryMarkersRef.current.get(e.id);
      if (existing) {
        existing
          .setLngLat([e.longitude as number, e.latitude as number])
          .setPopup(popup);
        continue;
      }

      const marker = new maplibregl.Marker({ element: createDot("#16a34a") })
        .setLngLat([e.longitude as number, e.latitude as number])
        .setPopup(popup)
        .addTo(map);

      entryMarkersRef.current.set(e.id, marker);
    }
  }, [entries, showEntries]);

  return <div ref={containerRef} className="w-full h-full rounded-xl border" />;
}

