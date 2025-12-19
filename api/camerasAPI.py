from typing import Any, Dict, Optional

import psycopg2
from fastapi import APIRouter, HTTPException
from psycopg2.extras import Json
from pydantic import BaseModel

from dao.cameras_dao import CamerasDAO

router = APIRouter()


class CameraBase(BaseModel):
    description: str
    cv_data: Dict[str, Any]


class CameraCreate(CameraBase):
    pass


class CameraUpdate(BaseModel):
    description: Optional[str] = None
    cv_data: Optional[Dict[str, Any]] = None


@router.get("/cameras")
def get_cameras():
    try:
        rows = CamerasDAO.get_all()
        fields = ["id", "description", "cv_data"]
        return [dict(zip(fields, row)) for row in rows]
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database error")


@router.get("/cameras/{camera_id}")
def get_camera(camera_id: int):
    try:
        row = CamerasDAO.get_camera(camera_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Camera not found")
        fields = ["id", "description", "cv_data"]
        return dict(zip(fields, row))
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database error")


@router.post("/cameras", status_code=201)
def create_camera(camera: CameraCreate):
    try:
        created = CamerasDAO.create(camera.description, camera.cv_data)
        fields = ["id", "description", "cv_data"]
        return dict(zip(fields, created))
    except psycopg2.Error:
        raise HTTPException(status_code=400, detail="Failed to create camera")


@router.delete("/cameras/{camera_id}")
def delete_camera(camera_id: int):
    try:
        deleted = CamerasDAO.delete(camera_id)
        if deleted is None:
            raise HTTPException(status_code=404, detail="Camera not found")
        return {"status": "deleted", "id": deleted[0]}
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database error")


@router.patch("/cameras/{camera_id}")
def update_camera(camera_id: int, camera: CameraUpdate):
    updates = []
    params = []

    if camera.description is not None:
        updates.append("description = %s")
        params.append(camera.description)
    if camera.cv_data is not None:
        updates.append("cv_data = %s")
        params.append(Json(camera.cv_data))

    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    params.append(camera_id)

    try:
        updated = CamerasDAO.update(updates, params)
        if updated is None:
            raise HTTPException(status_code=404, detail="Camera not found")
        fields = ["id", "description", "cv_data"]
        return dict(zip(fields, updated))
    except psycopg2.Error:
        raise HTTPException(status_code=400, detail="Failed to update camera")
