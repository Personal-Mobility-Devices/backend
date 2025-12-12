from fastapi import APIRouter, HTTPException
from database import get_db_connection
from pydantic import BaseModel
from psycopg2.extras import Json
from typing import Any, Dict, Optional

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
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT id, description, cv_data FROM cameras;")
        rows = cur.fetchall()
    fields = ["id", "description", "cv_data"]
    return [dict(zip(fields, row)) for row in rows]


@router.get("/cameras/{camera_id}")
def get_camera(camera_id: int):
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id, description, cv_data FROM cameras WHERE id = %s;",
            (camera_id,)
        )
        row = cur.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Camera not found")
    fields = ["id", "description", "cv_data"]
    return dict(zip(fields, row))


@router.post("/cameras", status_code=201)
def create_camera(camera: CameraCreate):
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO cameras (description, cv_data)
            VALUES (%s, %s)
            RETURNING id, description, cv_data;
            """,
            (camera.description, Json(camera.cv_data))
        )
        created = cur.fetchone()
    conn.commit()
    fields = ["id", "description", "cv_data"]
    return dict(zip(fields, created))


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

    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute(
            f"""
            UPDATE cameras
            SET {", ".join(updates)}
            WHERE id = %s
            RETURNING id, description, cv_data;
            """,
            params
        )
        updated = cur.fetchone()
        if updated is None:
            raise HTTPException(status_code=404, detail="Camera not found")
    conn.commit()
    fields = ["id", "description", "cv_data"]
    return dict(zip(fields, updated))