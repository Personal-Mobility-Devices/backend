from pydantic import BaseModel, Field
from typing import Optional
from schemas.utilModels import Coordinates

class BusStopBase(BaseModel):
    description: Optional[str] = Field(None, description="Описание остановки")
    coordinates: Coordinates = Field(..., description="Координаты остановки (lat/lon)")
    adm_area: Optional[str] = Field(None, max_length=100, description="Административный округ")
    district: Optional[str] = Field(None, max_length=100, description="Район")

class BusStopCreate(BusStopBase):
    pass

class BusStopUpdate(BaseModel):
    description: Optional[str] = Field(None, description="Описание остановки")
    coordinates: Optional[Coordinates] = Field(None, description="Координаты остановки (lat/lon)")
    adm_area: Optional[str] = Field(None, max_length=100, description="Административный округ")
    district: Optional[str] = Field(None, max_length=100, description="Район")

