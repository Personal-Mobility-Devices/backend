from fastapi import FastAPI, HTTPException
import psycopg2
from pydantic import BaseModel


app = FastAPI()


conn = psycopg2.connect(
    dbname = "parkings_db",
    user = "postgres",
    password = "228336",
    host = "localhost",
    port = "5432"
)

class ParkingUpdate(BaseModel):
    occupancy: int

@app.get("/data/{id_cam}")
def get_cvdata(id_cam: int):

    with conn.cursor() as cur:

        cur.execute("SELECT cvdata FROM cameras WHERE id = %s", (id_cam,))
        row = cur.fetchone()
        if row is None:
            return {"error": "Camera not found"}
        return row

@app.patch("/occupancy/{id_parking}")
def update_occupancy(id_parking: int, parking: ParkingUpdate):

    with conn.cursor() as cur:

        cur.execute("UPDATE parkings SET occupancy = %s WHERE id = %s", (parking.occupancy, id_parking))

        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Parking not found")

        conn.commit()

        return {"message": f"Occupancy for parking ID {id_parking} successfully updated"}

