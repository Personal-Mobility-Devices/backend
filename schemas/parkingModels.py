from typing import Optional

from pydantic import BaseModel

from schemas.utilModels import Coordinates, PolygonCooridinates


class ParkingCreate(BaseModel):
    description: str
    coordinates: PolygonCooridinates
    name: Optional[str] = None
    name_obj: Optional[str] = None
    adm_area: Optional[str] = None
    district: Optional[str] = None
    occupancy: Optional[int] = None
    all_spaces: Optional[int] = None


class ParkingUpdate(BaseModel):
    description: Optional[str] = None
    coordinates: Optional[PolygonCooridinates] = None
    name: Optional[str] = None
    name_obj: Optional[str] = None
    adm_area: Optional[str] = None
    district: Optional[str] = None
    occupancy: Optional[int] = None
    all_spaces: Optional[int] = None
