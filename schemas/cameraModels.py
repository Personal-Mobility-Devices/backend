from typing import Dict, Any, Optional

from pydantic import BaseModel


class CameraBase(BaseModel):
    description: str
    cv_data: Dict[str, Any]


class CameraCreate(CameraBase):
    pass


class CameraUpdate(BaseModel):
    description: Optional[str] = None
    cv_data: Optional[Dict[str, Any]] = None
