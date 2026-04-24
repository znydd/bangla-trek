import { createFileRoute, Link } from "@tanstack/react-router";
import { useState, useEffect, useRef } from "react";
import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import { 
  optimizeRoute, 
  fetchSavedItineraries, 
  OptimizationResponse, 
  LocationPoint 
} from "../../services/route-optimizer.service";
import { Search, MapPin, Flag, Plus, Trash2, Navigation, Loader2 } from "lucide-react";

export const Route = createFileRoute("/_authenticated/route-optimizer")({
  component: RouteOptimizerPage,
});

function RouteOptimizerPage() {
  const [startLoc, setStartLoc] = useState<LocationPoint | null>(null);
  const [endLoc, setEndLoc] = useState<LocationPoint | null>(null);
  const [waypoints, setWaypoints] = useState<LocationPoint[]>([]);
  const [numDays, setNumDays] = useState(1);
  const [mode, setMode] = useState<"driving" | "walking" | "cycling">("driving");
  
  const [result, setResult] = useState<OptimizationResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const [activeSearchType, setActiveSearchType] = useState<"start" | "end" | "waypoint" | null>(null);
  const [queries, setQueries] = useState({ start: "", end: "", waypoint: "" });
  const [searchResults, setSearchResults] = useState<any[]>([]);
  
  const [showImportModal, setShowImportModal] = useState(false);
  const [savedTrips, setSavedTrips] = useState<any[]>([]);

  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<maplibregl.Map | null>(null);
  const markers = useRef<maplibregl.Marker[]>([]);

  useEffect(() => {
    if (map.current || !mapContainer.current) return;

    map.current = new maplibregl.Map({
      container: mapContainer.current,
      style: `https://api.maptiler.com/maps/streets-v2/style.json?key=${import.meta.env.VITE_MAPTILER_KEY}`,
      center: [90.4125, 23.8103],
      zoom: 7,
    });

    map.current.addControl(new maplibregl.NavigationControl(), "top-right");
  }, []);

  useEffect(() => {
    if (!map.current || !result) return;

    markers.current.forEach(m => m.remove());
    markers.current = [];

    const combinedCoordinates: any[] = [];
    const uniqueLocations: LocationPoint[] = [];

    result.days.forEach(day => {
      day.locations.forEach(loc => {
        if (!uniqueLocations.find(l => l.name === loc.name)) {
          uniqueLocations.push(loc);
        }
      });

      day.legs.forEach((leg, i) => {
        if (leg.geometry && leg.geometry.coordinates) {
          combinedCoordinates.push(...leg.geometry.coordinates);
        } else {
          const origin = day.locations[i];
          const dest = day.locations[i+1];
          if (origin && dest) {
            combinedCoordinates.push([origin.lng, origin.lat]);
            combinedCoordinates.push([dest.lng, dest.lat]);
          }
        }
      });
    });

    if (uniqueLocations.length === 0) return;

    uniqueLocations.forEach((loc, i) => {
      const isStart = i === 0;
      const isEnd = i === uniqueLocations.length - 1;
      
      const marker = new maplibregl.Marker({ 
        color: isStart ? "#22c55e" : isEnd ? "#ef4444" : "#3b82f6" 
      })
        .setLngLat([loc.lng, loc.lat])
        .setPopup(new maplibregl.Popup({ offset: 25 }).setHTML(`<b>${i + 1}. ${loc.name}</b>`))
        .addTo(map.current!);
      
      markers.current.push(marker);
    });

    const geojsonData: GeoJSON.Feature<GeoJSON.Geometry> = {
      type: 'Feature',
      properties: {},
      geometry: {
        type: 'LineString',
        coordinates: combinedCoordinates
      }
    };

    if (map.current.getSource('route')) {
      (map.current.getSource('route') as maplibregl.GeoJSONSource).setData(geojsonData);
    } else {
      map.current.addSource('route', { type: 'geojson', data: geojsonData });
      map.current.addLayer({
        id: 'route-line',
        type: 'line',
        source: 'route',
        layout: { 'line-join': 'round', 'line-cap': 'round' },
        paint: {
          'line-color': '#2563eb', 
          'line-width': 5,
          'line-opacity': 0.8
        }
      });
    }

    const bounds = new maplibregl.LngLatBounds();
    uniqueLocations.forEach(loc => bounds.extend([loc.lng, loc.lat]));
    map.current.fitBounds(bounds, { padding: 80 });
  }, [result]);

  const triggerSearch = async (type: "start" | "end" | "waypoint") => {
    const query = queries[type];
    if (!query.trim()) return;
    
    setActiveSearchType(type);
    const apiKey = import.meta.env.VITE_MAPTILER_KEY;
    const res = await fetch(`https://api.maptiler.com/geocoding/${encodeURIComponent(query)}.json?key=${apiKey}&limit=5`);
    const data = await res.json();
    setSearchResults(data.features || []);
  };

  const selectLocation = (feature: any) => {
    const loc: LocationPoint = { 
      name: feature.place_name, 
      lng: feature.geometry.coordinates[0], 
      lat: feature.geometry.coordinates[1] 
    };

    if (activeSearchType === "start") setStartLoc(loc);
    else if (activeSearchType === "end") setEndLoc(loc);
    else if (activeSearchType === "waypoint") setWaypoints([...waypoints, loc]);

    setSearchResults([]);
    setActiveSearchType(null);
    setQueries({ ...queries, [activeSearchType!]: "" });
  };

  const handleImportLocation = async (placeName: string, type: "start" | "end" | "waypoint") => {
    setShowImportModal(false);
    setIsLoading(true);
    
    try {
      const apiKey = import.meta.env.VITE_MAPTILER_KEY;
      const res = await fetch(`https://api.maptiler.com/geocoding/${encodeURIComponent(placeName)}.json?key=${apiKey}&limit=1`);
      const data = await res.json();
      
      if (data.features && data.features.length > 0) {
        const feature = data.features[0];
        const loc: LocationPoint = {
          name: feature.place_name,
          lng: feature.geometry.coordinates[0],
          lat: feature.geometry.coordinates[1]
        };

        if (type === "start") setStartLoc(loc);
        if (type === "end") setEndLoc(loc);
        if (type === "waypoint") setWaypoints([...waypoints, loc]);
      } else {
        alert(`Could not find map coordinates for ${placeName}`);
      }
    } catch (error) {
      console.error("Failed to geocode imported location:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleOptimize = async () => {
    if (!startLoc || !endLoc) return;
    setIsLoading(true);
    try {
      const res = await optimizeRoute({
        start_location: startLoc, end_location: endLoc,
        waypoints, num_days: numDays, mode
      });
      setResult(res);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-[calc(100vh-64px)] w-full overflow-hidden bg-background">
      <div className="w-[400px] flex flex-col border-r shadow-lg z-10 bg-card overflow-hidden">
        <div className="p-6 overflow-y-auto flex-1 custom-scrollbar">
          <div className="flex items-center gap-2 mb-6 text-primary">
            <Navigation className="w-6 h-6" />
            <h1 className="text-2xl font-bold tracking-tight">Route Optimizer</h1>
          </div>

          <div className="space-y-6">
            <div className="relative">
              <label className="text-xs font-bold uppercase text-muted-foreground flex items-center gap-1 mb-2">
                <MapPin className="w-3 h-3 text-green-500" /> Starting From
              </label>
              <div className="flex gap-2">
                <input 
                  className="flex-1 p-2 text-sm border rounded-md"
                  placeholder={startLoc ? startLoc.name : "e.g. Dhaka"}
                  value={queries.start}
                  onChange={e => setQueries({...queries, start: e.target.value})}
                  onKeyDown={e => e.key === 'Enter' && triggerSearch("start")}
                />
                <button onClick={() => triggerSearch("start")} className="p-2 bg-secondary rounded-md hover:bg-secondary/80">
                  <Search className="w-4 h-4" />
                </button>
              </div>
              {activeSearchType === "start" && searchResults.length > 0 && (
                <div className="absolute z-50 w-full mt-1 bg-popover border rounded-md shadow-xl max-h-48 overflow-y-auto">
                  {searchResults.map((f, i) => (
                    <button key={i} onClick={() => selectLocation(f)} className="w-full text-left p-2 text-sm hover:bg-accent border-b last:border-0 italic">
                      {f.place_name}
                    </button>
                  ))}
                </div>
              )}
            </div>

            <div className="relative">
              <label className="text-xs font-bold uppercase text-muted-foreground flex items-center gap-1 mb-2">
                <Flag className="w-3 h-3 text-red-500" /> Final Destination
              </label>
              <div className="flex gap-2">
                <input 
                  className="flex-1 p-2 text-sm border rounded-md"
                  placeholder={endLoc ? endLoc.name : "e.g. Cox's Bazar"}
                  value={queries.end}
                  onChange={e => setQueries({...queries, end: e.target.value})}
                  onKeyDown={e => e.key === 'Enter' && triggerSearch("end")}
                />
                <button onClick={() => triggerSearch("end")} className="p-2 bg-secondary rounded-md hover:bg-secondary/80">
                  <Search className="w-4 h-4" />
                </button>
              </div>
              {activeSearchType === "end" && searchResults.length > 0 && (
                <div className="absolute z-50 w-full mt-1 bg-popover border rounded-md shadow-xl max-h-48 overflow-y-auto">
                  {searchResults.map((f, i) => (
                    <button key={i} onClick={() => selectLocation(f)} className="w-full text-left p-2 text-sm hover:bg-accent border-b last:border-0 italic">
                      {f.place_name}
                    </button>
                  ))}
                </div>
              )}
            </div>

            <div className="relative">
              <label className="text-xs font-bold uppercase text-muted-foreground flex items-center gap-1 mb-2">
                <Plus className="w-3 h-3" /> Add Stops In-Between
              </label>
              <div className="flex gap-2">
                <input 
                  className="flex-1 p-2 text-sm border rounded-md"
                  placeholder="e.g. Chittagong"
                  value={queries.waypoint}
                  onChange={e => setQueries({...queries, waypoint: e.target.value})}
                  onKeyDown={e => e.key === 'Enter' && triggerSearch("waypoint")}
                />
                <button onClick={() => triggerSearch("waypoint")} className="p-2 bg-secondary rounded-md hover:bg-secondary/80">
                  <Search className="w-4 h-4" />
                </button>
              </div>
              
              {activeSearchType === "waypoint" && searchResults.length > 0 && (
                <div className="absolute z-50 w-full mt-1 bg-popover border rounded-md shadow-xl max-h-48 overflow-y-auto">
                  {searchResults.map((f, i) => (
                    <button key={i} onClick={() => selectLocation(f)} className="w-full text-left p-2 text-sm hover:bg-accent border-b last:border-0 italic">
                      {f.place_name}
                    </button>
                  ))}
                </div>
              )}

              <div className="mt-3 space-y-2">
                {waypoints.map((w, idx) => (
                  <div key={idx} className="flex justify-between items-center bg-muted/40 p-2 rounded-md text-sm border border-dashed">
                    <span className="truncate pr-2">• {w.name}</span>
                    <button onClick={() => setWaypoints(waypoints.filter((_, i) => i !== idx))}>
                      <Trash2 className="w-3 h-3 text-destructive hover:scale-110 transition-transform" />
                    </button>
                  </div>
                ))}
              </div>
            </div>

            <hr />

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-xs font-bold uppercase text-muted-foreground">Days</label>
                <input type="number" min="1" max="14" value={numDays} onChange={e => setNumDays(parseInt(e.target.value))} className="w-full p-2 mt-1 border rounded-md text-sm" />
              </div>
              <div>
                <label className="text-xs font-bold uppercase text-muted-foreground">Mode</label>
                <select value={mode} onChange={e => setMode(e.target.value as any)} className="w-full p-2 mt-1 border rounded-md text-sm">
                  <option value="driving">Driving</option>
                  <option value="cycling">Cycling</option>
                  <option value="walking">Walking</option>
                </select>
              </div>
            </div>

            <button 
              onClick={handleOptimize}
              disabled={!startLoc || !endLoc || isLoading}
              className="w-full bg-primary text-primary-foreground py-3 rounded-xl font-bold hover:bg-primary/90 transition-all disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {isLoading ? <Loader2 className="animate-spin" /> : "Optimize My Journey"}
            </button>

            <button 
              onClick={async () => { setShowImportModal(true); setSavedTrips(await fetchSavedItineraries()); }}
              className="w-full text-center text-xs text-muted-foreground hover:text-primary transition-colors"
            >
              Import from Saved AI Itineraries
            </button>
          </div>

          {result && (
            <div className="mt-10 pb-10 space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
              <h2 className="text-lg font-bold border-b pb-2">Your Optimized Path</h2>
              {result.days.map(day => (
                <div key={day.day_number} className="relative pl-6 border-l-2 border-primary/20">
                  <div className="absolute -left-[9px] top-0 w-4 h-4 rounded-full bg-primary" />
                  <h3 className="font-extrabold text-primary mb-4">DAY {day.day_number}</h3>
                  
                  <div className="space-y-4">
                    {day.locations.map((loc, i) => (
                      <div key={i}>
                        <div className="flex items-start gap-2">
                          <div className="mt-1 w-2 h-2 rounded-full bg-muted-foreground" />
                          <p className="text-sm font-semibold">{loc.name}</p>
                        </div>
                        {day.legs[i] && (
                          <div className="my-3 ml-3 p-2 bg-accent/30 rounded-md border-l-2 border-accent text-[11px] text-muted-foreground">
                            <span className="font-bold">Travel:</span> {Math.round(day.legs[i].duration)} mins • {day.legs[i].distance.toFixed(1)} km
                            
                            {day.legs[i].fallback && (
                              <span className="block text-amber-600 font-bold mt-1">
                                ⚠️ Estimated (Direct map route unavailable)
                              </span>
                            )}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>

                  {day.needs_transit_blueprint && (
                    <div className="mt-4 p-3 bg-destructive/10 border border-destructive/20 rounded-md text-xs">
                      <p className="font-bold text-destructive mb-1">Road route unavailable.</p>
                      <Link to="/transit-blueprints" className="text-primary font-bold hover:underline">Open Transit Blueprint →</Link>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="flex-1 bg-muted relative">
        <div ref={mapContainer} className="absolute inset-0 h-full w-full" />
      </div>

      {showImportModal && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <div className="bg-card w-full max-w-md p-6 rounded-2xl shadow-2xl border">
            <h2 className="text-xl font-bold mb-4">Import Saved Trip</h2>
            <div className="space-y-3 max-h-80 overflow-y-auto p-1">
              
              {/* FIX 7: Modal items safely enclosed in closing </div> tags */}
              {savedTrips.map(t => (
                <div key={t.id} className="w-full text-left p-4 border rounded-xl hover:bg-accent/30 transition-colors">
                  <div className="font-bold">{t.destination}</div>
                  <div className="text-xs text-muted-foreground mb-3">{t.activity_count} saved places</div>
                  <div className="flex gap-2">
                    <button onClick={() => handleImportLocation(t.destination, "start")} className="flex-1 py-1.5 bg-green-100 text-green-700 hover:bg-green-200 rounded-md text-xs font-bold transition-colors">Set Start</button>
                    <button onClick={() => handleImportLocation(t.destination, "waypoint")} className="flex-1 py-1.5 bg-blue-100 text-blue-700 hover:bg-blue-200 rounded-md text-xs font-bold transition-colors">Add Stop</button>
                    <button onClick={() => handleImportLocation(t.destination, "end")} className="flex-1 py-1.5 bg-red-100 text-red-700 hover:bg-red-200 rounded-md text-xs font-bold transition-colors">Set End</button>
                  </div>
                </div>
              ))}

            </div>
            <button onClick={() => setShowImportModal(false)} className="w-full mt-6 py-2 text-sm text-muted-foreground hover:text-foreground">Close</button>
          </div>
        </div>
      )}
    </div>
  );
}
