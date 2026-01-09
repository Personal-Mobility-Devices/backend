from typing import Optional

from pydantic import BaseModel

from schemas.utilModels import Coordinates


class ParkingCreate(BaseModel):
    description: str
    coordinates: Coordinates
    name: Optional[str] = None
    name_obj: Optional[str] = None
    adm_area: Optional[str] = None
    district: Optional[str] = None
    occupancy: Optional[str] = None  # В БД строка, возможно позже изменим на int


class ParkingUpdate(BaseModel):
    description: Optional[str] = None
    coordinates: Optional[Coordinates] = None
    name: Optional[str] = None
    name_obj: Optional[str] = None
    adm_area: Optional[str] = None
    district: Optional[str] = None
    occupancy: Optional[str] = None
