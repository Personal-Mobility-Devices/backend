from fastapi import APIRouter, HTTPException
from database import get_db_connection
from pydantic import BaseModel


router = APIRouter()

conn = get_db_connection()


class ParkingUpdate(BaseModel):
    occupancy: int

@router.get("/data/{id_cam}")
def get_cvdata(id_cam: int):

    with conn.cursor() as cur:

        cur.execute("SELECT cvdata FROM cameras WHERE id = %s", (id_cam,))
        row = cur.fetchone()
        if row is None:
            return {"error": "Camera not found"}
        return row

@router.patch("/occupancy/{id_parking}")
def update_occupancy(id_parking: int, parking: ParkingUpdate):

    with conn.cursor() as cur:

        cur.execute("UPDATE parkings SET occupancy = %s WHERE id = %s", (parking.occupancy, id_parking))

        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Parking not found")

        conn.commit()

        return {"message": f"Occupancy for parking ID {id_parking} successfully updated"}

