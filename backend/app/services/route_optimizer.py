import math
import httpx
import logging
from typing import List, Dict, Any
from app.config import settings

logger = logging.getLogger(__name__)

class RouteOptimizerService:
    def __init__(self, maptiler_key: str = settings.MAPTILER_KEY):
        self.api_key = maptiler_key
        # FIX 1: Use OSRM-style URL for proper routing
        self.base_url = "https://api.maptiler.com/routing/route/v1"

    def haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Fast math to sort places, saving API quota and acting as a fallback"""
        R = 6371
        d_lat = math.radians(lat2 - lat1)
        d_lon = math.radians(lon2 - lon1)
        a = (math.sin(d_lat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    def sort_linear_route(self, start: dict, end: dict, waypoints: List[dict]) -> List[dict]:
        ordered = [start]
        unvisited = waypoints[:]
        current = start

        while unvisited:
            distances = [self.haversine_distance(current['lat'], current['lng'], w['lat'], w['lng']) for w in unvisited]
            closest_idx = distances.index(min(distances))
            current = unvisited.pop(closest_idx)
            ordered.append(current)

        ordered.append(end)
        return ordered

    async def get_travel_estimates(self, origin: Dict[str, Any], destination: Dict[str, Any], mode: str = "driving") -> Dict[str, Any]:
        fallback_dist = self.haversine_distance(origin['lat'], origin['lng'], destination['lat'], destination['lng'])
        coords = f"{origin['lng']},{origin['lat']};{destination['lng']},{destination['lat']}"
        
        # FIX 3: Map frontend modes to MapTiler/OSRM accepted profiles
        profile_map = {"driving": "car", "cycling": "bike", "walking": "foot"}
        profile = profile_map.get(mode, "car")
        
        try:
            async with httpx.AsyncClient() as client:
                # FIX 3: overview=full is required for geometry to be returned
                url = f"{self.base_url}/{profile}/{coords}?overview=full&geometries=geojson&key={self.api_key}"
                response = await client.get(url)
                
                if response.status_code == 200:
                    data = response.json()
                    if "routes" in data and len(data["routes"]) > 0:
                        route = data["routes"][0]
                        return {
                            "distance": route["distance"] / 1000,
                            "duration": route["duration"] / 60, # FIX 2: Added duration 
                            "needs_transit": False,
                            "geometry": route["geometry"]
                        }
                
                # If API fails gracefully
                return {"needs_transit": True, "fallback_distance": fallback_dist}
                
        except Exception as e:
            logger.error(f"MapTiler exception: {e}")
            return {"needs_transit": True, "fallback_distance": fallback_dist}