from pydantic import BaseModel, Field
from typing import Optional
from schemas.utilModels import Coordinates

# Класс, содержащий в себе базовые поля, используемые в остальных моделях
class SIMStopBase(BaseModel):
    description: Optional[str] = Field(None, description="Описание остановки")
    coordinates: Coordinates = Field(..., description="Координаты остановки (lat/lon)")
    adm_area: Optional[str] = Field(None, max_length=100, description="Административный округ")
    district: Optional[str] = Field(None, max_length=100, description="Район")
    free_sims: int = Field(0, description="Количество свободных мест для СИМ")

class SIMStopCreate(SIMStopBase):
    pass

class SIMStopUpdate(BaseModel):
    description: Optional[str] = Field(None, description="Описание остановки")
    coordinates: Optional[Coordinates] = Field(None, description="Координаты остановки (lat/lon)")
    adm_area: Optional[str] = Field(None, max_length=100, description="Административный округ")
    district: Optional[str] = Field(None, max_length=100, description="Район")
    free_sims: Optional[int] = Field(None, description="Количество свободных мест для СИМ")