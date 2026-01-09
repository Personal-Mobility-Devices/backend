from typing import Optional

from pydantic import BaseModel

from schemas.utilModels import Coordinates


class ParkingSpaceCreate(BaseModel):
    coordinates: Coordinates
    id_parking: int


class ParkingSpaceUpdate(BaseModel):
    coordinates: Optional[Coordinates] = None
