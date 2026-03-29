from pydantic import BaseModel, Field
from typing import Optional

# Класс, содержащий в себе базовые поля, используемые в остальных моделях
class BusBase(BaseModel):
    name: str = Field(None, description="Номер маршрута")
    description: Optional[str] = Field(None, description="Описание парковки")

class BusCreate(BusBase):
    pass

class BusUpdate(BaseModel):
    name: str = Field(None, description="Номер маршрута")
    description: Optional[str] = Field(None, description="Описание парковки")


