from pydantic import BaseModel
from typing import Optional

# Класс, содержащий в себе базовые поля, используемые в остальных моделях
class SIMStopBase(BaseModel):
    pass

class SIMStopCreate(SIMStopBase):
    pass

class SIMStopUpdate(BaseModel):
    pass