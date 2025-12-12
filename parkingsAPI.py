from fastapi import APIRouter, HTTPException
from database import get_db_connection
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class Coordinates(BaseModel):
    lat: float
    lon: float

class ParkingCreate(BaseModel):
    description: str
    coordinates: Coordinates
    name: Optional[str] = None
    name_obj: Optional[str] = None
    adm_area: Optional[str] = None
    district: Optional[str] = None
    occupancy: Optional[str] = None # В БД строка, возможно позже изменим на int

class ParkingUpdate(BaseModel):
    description: Optional[str] = None
    coordinates: Optional[Coordinates] = None
    name: Optional[str] = None
    name_obj: Optional[str] = None
    adm_area: Optional[str] = None
    district: Optional[str] = None
    occupancy: Optional[str] = None

@router.get("/parkings/all")
def get_all_parkings():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM parkings;")
    data = cur.fetchall()
    return data

@router.get("/parkings/in_area")
def get_parkings_in_area(lat_min: float, lat_max: float, lon_min: float, lon_max: float):
    conn = get_db_connection()
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
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM parkings WHERE id = %s", (parking_id,))
    return cur.fetchone()


@router.get("/parking_fields/{parking_id}")
def get_parking_fields(parking_id: int, fields: str):
    conn = get_db_connection()
    selected = ",".join([f.strip() for f in fields.split(",")])
    cur = conn.cursor()
    cur.execute(f"SELECT {selected} FROM parkings WHERE id = %s", (parking_id,))
    row = cur.fetchone()
    if row is None:
        return {"error": "Parking not found"}
    result = dict(zip(selected.split(","), row))
    return result

# тут поправить если мы храним координаты как [число, число], а не, как я, в виде словаря
@router.get("/parkinggeojson/{parking_id}")
def get_parking_geojson(parking_id: int):
    conn = get_db_connection()
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
@router.post("/parkings", status_code=201)
def create_parking(parking: ParkingCreate):
    conn = get_db_connection()
    cur = conn.cursor()

    # psycopg2 автоматически преобразует BaseModel "Coordinates" в JSONB при использовании %s
    query = """
        INSERT INTO parkings (description, coordinates, name, name_obj, adm_area, district, occupancy)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id, name, coordinates;
    """
    try:
        cur.execute(query, (
            parking.description,
            parking.coordinates.model_dump_json(), # Используем json-строку для jsonb поля
            parking.name,
            parking.name_obj,
            parking.adm_area,
            parking.district,
            parking.occupancy
        ))
        created_parking = cur.fetchone()
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close()

    fields = ["id", "name", "coordinates"]
    return dict(zip(fields, created_parking))


@router.put("/parking/{parking_id}")
def update_parking(parking_id: int, parking: ParkingUpdate):
    conn = get_db_connection()
    cur = conn.cursor()
    updates = []
    params = []

    # Динамически строим запрос UPDATE
    if parking.description is not None:
        updates.append("description = %s")
        params.append(parking.description)
    if parking.coordinates is not None:
        updates.append("coordinates = %s")
        params.append(parking.coordinates.model_dump_json())
    if parking.name is not None:
        updates.append("name = %s")
        params.append(parking.name)
    if parking.name_obj is not None:
        updates.append("name_obj = %s")
        params.append(parking.name_obj)
    if parking.adm_area is not None:
        updates.append("adm_area = %s")
        params.append(parking.adm_area)
    if parking.district is not None:
        updates.append("district = %s")
        params.append(parking.district)
    if parking.occupancy is not None:
        updates.append("occupancy = %s")
        params.append(parking.occupancy)

    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    params.append(parking_id)  # ID в конец параметров для WHERE условия

    query = f"""
        UPDATE parkings
        SET {", ".join(updates)}
        WHERE id = %s
        RETURNING id, name, occupancy;
    """

    cur.execute(query, params)
    updated = cur.fetchone()
    conn.commit()

    if updated is None:
        raise HTTPException(status_code=404, detail="Parking not found")

    fields = ["id", "name", "occupancy"]
    return dict(zip(fields, updated))