import { useEffect, useMemo, useRef, useState } from "react";
import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";

interface LocationMapProps {
  latitude?: number | null;
  longitude?: number | null;
  locationQuery: string;
  name: string;
}

type Coordinate = {
  latitude: number;
  longitude: number;
};

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
  layers: [
    {
      id: "osm",
      type: "raster",
      source: "osm",
    },
  ],
};

function parseCoordinate(value: unknown): number | null {
  if (typeof value === "number" && Number.isFinite(value)) {
    return value;
  }
  if (typeof value === "string") {
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : null;
  }
  return null;
}

export function LocationMap({ latitude, longitude, locationQuery, name }: LocationMapProps) {
  const mapContainer = useRef<HTMLDivElement>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);
  const markerRef = useRef<maplibregl.Marker | null>(null);
  const usingFallbackRef = useRef(false);
  const key = import.meta.env.VITE_BARIKOI_API_KEY;

  const [resolvedCoord, setResolvedCoord] = useState<Coordinate | null>(null);
  const [isResolving, setIsResolving] = useState(false);

  const explicitCoord = useMemo<Coordinate | null>(() => {
    const lat = parseCoordinate(latitude);
    const lng = parseCoordinate(longitude);
    if (lat === null || lng === null) {
      return null;
    }
    return { latitude: lat, longitude: lng };
  }, [latitude, longitude]);

  useEffect(() => {
    if (explicitCoord) {
      setResolvedCoord(explicitCoord);
      return;
    }

    const query = locationQuery?.trim();
    if (!query || !key) {
      setResolvedCoord(null);
      return;
    }

    let cancelled = false;
    const controller = new AbortController();

    const resolveLocation = async () => {
      setIsResolving(true);
      try {
        const url = new URL("https://barikoi.xyz/v2/api/search/autocomplete/place");
        url.searchParams.set("api_key", key);
        url.searchParams.set("q", query);
        url.searchParams.set("country_code", "bd");

        const res = await fetch(url.toString(), { signal: controller.signal });
        if (!res.ok) {
          throw new Error(`Geocode failed with status ${res.status}`);
        }

        const data = await res.json();
        const firstPlace = Array.isArray(data?.places) ? data.places[0] : null;

        const lat = parseCoordinate(firstPlace?.latitude);
        const lng = parseCoordinate(firstPlace?.longitude);

        if (!cancelled && lat !== null && lng !== null) {
          setResolvedCoord({ latitude: lat, longitude: lng });
        }
      } catch {
        if (!cancelled) {
          setResolvedCoord(null);
        }
      } finally {
        if (!cancelled) {
          setIsResolving(false);
        }
      }
    };

    resolveLocation();

    return () => {
      cancelled = true;
      controller.abort();
    };
  }, [explicitCoord, key, locationQuery]);

  useEffect(() => {
    return () => {
      mapRef.current?.remove();
      mapRef.current = null;
      markerRef.current = null;
    };
  }, []);

  useEffect(() => {
    if (!mapContainer.current || !resolvedCoord) {
      return;
    }

    const center: [number, number] = [resolvedCoord.longitude, resolvedCoord.latitude];
    const barikoiStyle = key
      ? `https://map.barikoi.com/styles/barikoi/style.json?key=${key}`
      : OSM_FALLBACK_STYLE;

    if (!mapRef.current) {
      const map = new maplibregl.Map({
        container: mapContainer.current,
        style: barikoiStyle,
        center,
        zoom: 13,
      });

      if (key) {
        map.on("error", () => {
          if (!usingFallbackRef.current) {
            usingFallbackRef.current = true;
            map.setStyle(OSM_FALLBACK_STYLE);
          }
        });
      }

      map.addControl(new maplibregl.NavigationControl(), "top-right");
      mapRef.current = map;

      markerRef.current = new maplibregl.Marker({ color: "#16a34a" })
        .setLngLat(center)
        .setPopup(new maplibregl.Popup().setText(name))
        .addTo(map);

      return;
    }

    mapRef.current.flyTo({ center, zoom: 13 });
    markerRef.current?.setLngLat(center).setPopup(new maplibregl.Popup().setText(name));
  }, [resolvedCoord, name, key]);

  const mapUnavailable = !resolvedCoord && !isResolving;

  return (
    <div className="rounded-2xl overflow-hidden border border-border shadow-sm">
      <div ref={mapContainer} style={{ height: "320px", width: "100%" }} />
      {isResolving && (
        <p className="px-3 py-2 text-xs text-muted-foreground border-t border-border/60">
          Resolving location for map...
        </p>
      )}
      {mapUnavailable && (
        <p className="px-3 py-2 text-xs text-muted-foreground border-t border-border/60">
          Map preview unavailable for this location text.
        </p>
      )}
    </div>
  );
}
