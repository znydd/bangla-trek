from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class LocationPoint(BaseModel):
    name: str
    lat: float
    lng: float

class LegEstimate(BaseModel):
    origin_name: str
    destination_name: str
    duration: float  # minutes
    distance: float  # km
    mode: str
    fallback: bool = False
    geometry: Optional[Dict[str, Any]] = None

class OptimizedDay(BaseModel):
    day_number: int
    locations: List[LocationPoint]
    legs: List[LegEstimate]
    needs_transit_blueprint: bool = False

class OptimizationRequest(BaseModel):
    start_location: LocationPoint
    end_location: LocationPoint
    waypoints: List[LocationPoint] = []
    num_days: int = 1
    mode: str = "driving"

class OptimizationResponse(BaseModel):
    days: List[OptimizedDay]
    status: str = "success"