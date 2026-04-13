import psycopg2
from fastapi import APIRouter, HTTPException

from dao.parkings_dao import ParkingsDAO
from schemas.parkingModels import ParkingCreate, ParkingUpdate

router = APIRouter()


def _row_to_dict(row) -> dict:
    pid, description, lon, lat, name, name_obj, adm_area, district, occupancy, all_spaces= row
    return {
        "id": pid,
        "description": description,
        "coordinates": {"lon": lon, "lat": lat},
        "name": name,
        "name_obj": name_obj,
        "adm_area": adm_area,
        "district": district,
        "occupancy": occupancy,
        "all_spaces": all_spaces,
    }


@router.get("/parkings/all")
def get_all_parkings():
    try:
        rows = ParkingsDAO.get_all()
        return [_row_to_dict(row) for row in rows]
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database error")


@router.get("/parkings/in_area")
def get_parkings_in_area(lat_min: float, lat_max: float, lon_min: float, lon_max: float):
    try:
        rows = ParkingsDAO.get_in_area(lat_min, lat_max, lon_min, lon_max)
        return [_row_to_dict(row) for row in rows]
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database error")


@router.get("/parking/{parking_id}")
def get_parking(parking_id: int):
    try:
        row = ParkingsDAO.get_by_id(parking_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Parking not found")
        return _row_to_dict(row)
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database error")


@router.get("/parking_fields/{parking_id}")
def get_parking_fields(parking_id: int, fields: str):
    try:
        selected_fields = ",".join([f.strip() for f in fields.split(",")])
        row = ParkingsDAO.get_fields(parking_id, selected_fields)
        if row is None:
            return {"error": "Parking not found"}
        return dict(zip(selected_fields.split(","), row))
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database error")


@router.get("/parkinggeojson/{parking_id}")
def get_parking_geojson(parking_id: int):
    try:
        row = ParkingsDAO.get_geojson(parking_id)
        if row is None:
            return {"error": "Parking not found"}

        pid, description, lon, lat, name, name_obj, adm_area, district, occupancy, all_spaces = row

        return {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [lon, lat],
            },
            "properties": {
                "id": pid,
                "name": name,
                "description": description,
                "name_obj": name_obj,
                "adm_area": adm_area,
                "district": district,
                "occupancy": occupancy,
                "all_spaces": all_spaces
            },
        }
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database error")


@router.post("/parkings", status_code=201)
def create_parking(parking: ParkingCreate):
    try:
        row = ParkingsDAO.create(
            description=parking.description,
            lat=parking.coordinates.lat,
            lon=parking.coordinates.lon,
            name=parking.name,
            name_obj=parking.name_obj,
            adm_area=parking.adm_area,
            district=parking.district,
            occupancy=parking.occupancy,
            all_spaces=parking.all_spaces,
        )
        pid, name, lon, lat = row
        return {"id": pid, "name": name, "coordinates": {"lon": lon, "lat": lat}}
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database error")


@router.put("/parking/{parking_id}")
def update_parking(parking_id: int, parking: ParkingUpdate):
    updates = []
    params = []

    if parking.description is not None:
        updates.append("description = %s")
        params.append(parking.description)
    if parking.coordinates is not None:
        # Для geometry используем ST_SetSRID(ST_MakePoint(lon, lat), 4326)
        updates.append("coordinates = ST_SetSRID(ST_MakePoint(%s, %s), 4326)")
        params.append(parking.coordinates.lon)
        params.append(parking.coordinates.lat)
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
    if parking.all_spaces is not None:
        updates.append("all_spaces = %s")
        params.append(parking.all_spaces)

    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    params.append(parking_id)

    try:
        updated = ParkingsDAO.update(updates, params)
        fields = ["id", "name", "occupancy"]
        return dict(zip(fields, updated))
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database error")


@router.delete("/parking/{parking_id}")
def delete_parking(parking_id: int):
    try:
        deleted = ParkingsDAO.delete(parking_id)
        return {"status": "deleted", "id": deleted[0]}
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database error")