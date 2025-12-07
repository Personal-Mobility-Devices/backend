from fastapi import APIRouter
import psycopg2
from typing import List

router = APIRouter()

conn = psycopg2.connect(
    dbname="parkings_db",
    user="postgres",
    password="228336",
    host="localhost",
    port="5432"
)


@router.get("/parkings/all")
def get_all_parkings():
    cur = conn.cursor()
    cur.execute("SELECT * FROM parkings;")
    data = cur.fetchall()
    return data

@router.get("/parkings/in_area")
def get_parkings_in_area(lat_min: float, lat_max: float, lon_min: float, lon_max: float):
    cur = conn.cursor()
    query = """
        SELECT id, coordinates
        FROM parkings
        WHERE (coordinates->>'lat')::float BETWEEN %s AND %s
        AND   (coordinates->>'lon')::float BETWEEN %s AND %s;
    """
    cur.execute(query, (lat_min, lat_max, lon_min, lon_max))
    data = cur.fetchall()
    return data


@router.get("/parking/{parking_id}")
def get_parking(parking_id: int):
    cur = conn.cursor()
    cur.execute("SELECT * FROM parkings WHERE id = %s", (parking_id,))
    return cur.fetchone()


@router.get("/parking_fields/{parking_id}")
def get_parking_fields(parking_id: int, fields: str):
    selected = ",".join([f.strip() for f in fields.split(",")])
    cur = conn.cursor()
    cur.execute(f"SELECT {selected} FROM parkings WHERE id = %s", (parking_id,))
    row = cur.fetchone()
    if row is None:
        return {"error": "Parking not found"}
    result = dict(zip(selected.split(","), row))
    return result


@router.get("/favorite_by_user/{user_id}")
def get_favorites(user_id: int):
    cur = conn.cursor()
    query = """
        SELECT p.id, p.name, p.coordinates
        FROM favorite_parkings fp
        JOIN parkings p ON p.id = fp.id_parking
        WHERE fp.id_user = %s;
    """
    cur.execute(query, (user_id,))
    return cur.fetchall()

# тут поправить если мы храним координаты как [число, число], а не, как я, в виде словаря
@router.get("/parkinggeojson/{parking_id}")
def get_parking_geojson(parking_id: int):
    cur = conn.cursor()
    cur.execute("""
        SELECT id, description, coordinates, name, name_obj, adm_area, district, occupancy
        FROM parkings
        WHERE id = %s
    """, (parking_id,))
    
    row = cur.fetchone()
    if row is None:
        return {"error": "Parking not found"}

    (
        id,
        description,
        coordinates,
        name,
        name_obj,
        adm_area,
        district,
        occupancy
    ) = row

    lat = float(coordinates["lat"])
    lon = float(coordinates["lon"])

    feature = {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [lon, lat]
        },
        "properties": {
            "id": id,
            "name": name,
            "description": description,
            "name_obj": name_obj,
            "adm_area": adm_area,
            "district": district,
            "occupancy": occupancy
        }
    }

    return feature
