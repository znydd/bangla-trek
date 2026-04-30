from typing import List, Dict, Any
import math
from fastapi import APIRouter
from app.services.route_optimizer import RouteOptimizerService
from app.schemas.route_optimizer import OptimizationRequest, OptimizationResponse, OptimizedDay, LegEstimate

router = APIRouter(prefix="/route-optimizer", tags=["route-optimizer"])

@router.post("/optimize", response_model=OptimizationResponse)
async def optimize_route(request: OptimizationRequest):
    service = RouteOptimizerService()
    
    start_dict = request.start_location.model_dump()
    end_dict = request.end_location.model_dump()
    waypoint_dicts = [w.model_dump() for w in request.waypoints]
    
    ordered_route = service.sort_linear_route(start_dict, end_dict, waypoint_dicts)
    
    all_legs = []
    avg_speeds = {"driving": 35, "cycling": 15, "walking": 5}
    speed = avg_speeds.get(request.mode, 35)

    for i in range(len(ordered_route) - 1):
        origin = ordered_route[i]
        dest = ordered_route[i+1]
        estimate = await service.get_travel_estimates(origin, dest, request.mode)
        
        if estimate.get("needs_transit"):
            dist = estimate.get("fallback_distance", service.haversine_distance(origin['lat'], origin['lng'], dest['lat'], dest['lng']))
            duration = (dist / speed) * 60 if speed > 0 else 0
            
            all_legs.append(LegEstimate(
                origin_name=origin["name"], destination_name=dest["name"], 
                duration=round(duration, 1), distance=round(dist, 1), 
                mode=request.mode, fallback=True, geometry=None
            ))
        else:
            all_legs.append(LegEstimate(
                origin_name=origin["name"], destination_name=dest["name"], 
                duration=round(estimate["duration"], 1), distance=round(estimate["distance"], 1), 
                mode=request.mode, fallback=False, geometry=estimate.get("geometry")
            ))

    num_days = max(1, request.num_days)
    total_legs = max(1, len(all_legs)) 
    legs_per_day = math.ceil(total_legs / num_days)
    
    optimized_days = []
    
    for i in range(num_days):
        start_leg_idx = i * legs_per_day
        end_leg_idx = min((i + 1) * legs_per_day, len(all_legs))
        
        if start_leg_idx >= len(all_legs):
            day_locations = [ordered_route[-1]]
            day_legs = []
            day_needs_transit = False
        else:
            day_legs = all_legs[start_leg_idx:end_leg_idx]
            day_needs_transit = any(leg.fallback for leg in day_legs)

            # FIX 4: Build day_locations correctly based on the legs in this specific day
            loc_names_seen = set()
            day_locations = []
            for leg in day_legs:
                for name in [leg.origin_name, leg.destination_name]:
                    if name not in loc_names_seen:
                        loc_names_seen.add(name)
                        match = next((p for p in ordered_route if p["name"] == name), None)
                        if match:
                            day_locations.append(match)
        
        optimized_days.append(OptimizedDay(
            day_number=i+1, 
            locations=day_locations, 
            legs=day_legs, 
            needs_transit_blueprint=day_needs_transit
        ))
        
    return OptimizationResponse(days=optimized_days, status="success")