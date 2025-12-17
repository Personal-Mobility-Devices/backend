from fastapi import APIRouter, HTTPException
from database import get_db_connection
from pydantic import BaseModel
from psycopg2.extras import Json
from typing import Any, Dict, Optional
from redis_client import redis_client as redis
import psycopg2

router = APIRouter()


class ParkingUpdate(BaseModel):
    occupancy: int

@router.get("/data/{id_cam}")
def get_cvdata(id_cam: int):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT cv_data FROM cameras WHERE id = %s", (id_cam,))
                row = cur.fetchone()
                if row is None:
                    raise HTTPException(status_code=404, detail="Camera not found")
                return row[0]
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database error")

@router.patch("/occupancy/{id_parking}")
def update_occupancy(id_parking: int, parking: ParkingUpdate):
    
    redis.set(f"parking:{id_parking}:occupancy", parking.occupancy)

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE parkings SET occupancy = %s WHERE id = %s",
                    (parking.occupancy, id_parking)
                )
                if cur.rowcount == 0:
                    raise HTTPException(status_code=404, detail="Parking not found")
            conn.commit()
        return {"message": f"Occupancy for parking ID {id_parking} successfully updated"}
    except psycopg2.Error:
        raise HTTPException(status_code=400, detail="Failed to update occupancy")

@router.get("/parking/{id_parking}/status")
def get_status(id_parking: int):
    occupancy = redis.get(f"parking:{id_parking}:occupancy")

    if occupancy is None:
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT occupancy FROM parkings WHERE id = %s",
                        (id_parking,)
                    )
                    row = cur.fetchone()
        except psycopg2.Error:
            raise HTTPException(status_code=500, detail="Database error")

        if row is None or row[0] is None:
            raise HTTPException(
                status_code=404,
                detail="Parking not found in cache or DB"
            )

        try:
            redis.set(f"parking:{id_parking}:occupancy", row[0])
        except Exception:
            pass

        return {
            "id_parking": id_parking,
            "occupancy": int(row[0])
        }

    return {
        "id_parking": id_parking,
        "occupancy": int(occupancy)
    }
