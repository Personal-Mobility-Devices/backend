import psycopg2
from fastapi import APIRouter, HTTPException
from psycopg2.extras import Json

from dao.cameras_dao import CamerasDAO
from schemas.cameraModels import CameraCreate, CameraUpdate

router = APIRouter()


@router.get("/cameras")
async def get_cameras():
    try:
        rows = await CamerasDAO.get_all()
        fields = ["id", "description", "cv_data"]
        return [dict(zip(fields, row)) for row in rows]
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database error")


@router.get("/cameras/{camera_id}")
async def get_camera(camera_id: int):
    try:
        row = await CamerasDAO.get_camera(camera_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Camera not found")
        fields = ["id", "description", "cv_data"]
        return dict(zip(fields, row))
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database error")


@router.post("/cameras", status_code=201)
async def create_camera(camera: CameraCreate):
    try:
        created = await CamerasDAO.create(camera.description, camera.cv_data)
        fields = ["id", "description", "cv_data"]
        return dict(zip(fields, created))
    except psycopg2.Error:
        raise HTTPException(status_code=400, detail="Failed to create camera")


@router.delete("/cameras/{camera_id}")
async def delete_camera(camera_id: int):
    try:
        deleted = await CamerasDAO.delete(camera_id)
        if deleted is None:
            raise HTTPException(status_code=404, detail="Camera not found")
        return {"status": "deleted", "id": deleted[0]}
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database error")


@router.patch("/cameras/{camera_id}")
async def update_camera(camera_id: int, camera: CameraUpdate):
    updates = []
    params = []
    idx = 1

    if camera.description is not None:
        updates.append(f"description = ${idx}")
        params.append(camera.description)
        idx += 1
    if camera.cv_data is not None:
        updates.append(f"cv_data = ${idx}")
        params.append(Json(camera.cv_data))
        idx += 1

    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    params.append(camera_id)

    # В asyncpg нет %s, как это было в psycopg2, для передачи аргументов используется $1, $2 и так далее
    where_idx = idx  # текущий порядковый номер idx для аргумента

    try:
        updated = await CamerasDAO.update(updates, where_idx, params)
        if updated is None:
            raise HTTPException(status_code=404, detail="Camera not found")
        fields = ["id", "description", "cv_data"]
        return dict(zip(fields, updated))
    except psycopg2.Error:
        raise HTTPException(status_code=400, detail="Failed to update camera")
