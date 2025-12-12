from fastapi import APIRouter, HTTPException
from database import get_db_connection
from pydantic import BaseModel
from psycopg2.extras import Json
from typing import Any, Dict, Optional
from redis_client import redis_client as redis

router = APIRouter()


class ParkingUpdate(BaseModel):
    occupancy: int

@router.get("/data/{id_cam}")
def get_cvdata(id_cam: int):
    conn = get_db_connection()
    with conn.cursor() as cur:

        cur.execute("SELECT cv_data FROM cameras WHERE id = %s", (id_cam,))
        row = cur.fetchone()
        if row is None:
            return {"error": "Camera not found"}
        return row[0]

@router.patch("/occupancy/{id_parking}")
def update_occupancy(id_parking: int, parking: ParkingUpdate):
    
    redis.set(f"parking:{id_parking}:occupancy", parking.occupancy)

    conn = get_db_connection()
    with conn.cursor() as cur:

        cur.execute("UPDATE parkings SET occupancy = %s WHERE id = %s", (parking.occupancy, id_parking))

        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Parking not found")

        conn.commit()

        return {"message": f"Occupancy for parking ID {id_parking} successfully updated"}

@router.get("/parking/{id_parking}/status")
def get_status(id_parking: int):
    occupancy = redis.get(f"parking:{id_parking}:occupancy")
    if occupancy is None:
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT occupancy FROM parkings WHERE id = %s", (id_parking,))
                row = cur.fetchone()
        finally:
            try:
                conn.close()
            except Exception:
                pass

        if row is None or row[0] is None:
            raise HTTPException(status_code=404, detail="Parking not found in cache or DB")

        try:
            redis.set(f"parking:{id_parking}:occupancy", row[0])
        except Exception:
            pass

        return {"id_parking": id_parking, "occupancy": int(row[0])}

    return {"id_parking": id_parking, "occupancy": int(occupancy)}