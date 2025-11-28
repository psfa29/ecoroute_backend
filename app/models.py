from typing import List, Optional
from pydantic import BaseModel, Field


class Point(BaseModel):
    lat: float = Field(..., description="Latitude in decimal degrees")
    lng: float = Field(..., description="Longitude in decimal degrees")
    id: Optional[str] = None
    address: Optional[str] = None
    distrito: Optional[str] = None
    priority: Optional[float] = None

class OptimizeRequest(BaseModel):
    depot: Point
    stops: List[Point]
    return_to_depot: bool = True
    average_speed_kmh: float = 25.0
    liters_per_km: float = 0.4

class Leg(BaseModel):
    from_index: int
    to_index: int
    distance_km: float
    duration_min: float

class OptimizeResponse(BaseModel):
    order: List[int]
    legs: List[Leg]
    total_distance_km: float
    total_duration_min: float
    co2_kg: float
    geojson: dict
    mst_geojson: dict

#  NUEVOS MODELOS PARA USUARIOS 
class UserRegister(BaseModel):
    username: str
    password: str
    email: str
    fullName: str

class UserLogin(BaseModel):
    username: str
    password: str