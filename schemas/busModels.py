from pydantic import BaseModel
from typing import Optional

# Класс, содержащий в себе базовые поля, используемые в остальных моделях
class BusBase(BaseModel):
    pass

class BusCreate(BusBase):
    pass

class BusUpdate(BaseModel):
    pass


