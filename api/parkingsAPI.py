from typing import Optional

import psycopg2
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from dao.parkings_dao import ParkingsDAO

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
    occupancy: Optional[str] = None  # В БД строка, возможно позже изменим на int


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
    try:
        rows = ParkingsDAO.get_all()
        result = []
        for row in rows:
            (
                pid,
                description,
                coordinates,
                name,
                name_obj,
                adm_area,
                district,
                occupancy,
            ) = row

            coords = coordinates
            try:
                if isinstance(coordinates, str):
                    import json

                    coords = json.loads(coordinates)
            except Exception:
                coords = coordinates

            result.append(
                {
                    "id": pid,
                    "description": description,
                    "coordinates": coords,
                    "name": name,
                    "name_obj": name_obj,
                    "adm_area": adm_area,
                    "district": district,
                    "occupancy": occupancy,
                }
            )
        return result
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database error")


@router.get("/parkings/in_area")
def get_parkings_in_area(lat_min: float, lat_max: float, lon_min: float, lon_max: float):
    try:
        rows = ParkingsDAO.get_in_area(lat_min, lat_max, lon_min, lon_max)
        result = []
        for row in rows:
            (
                pid,
                description,
                coordinates,
                name,
                name_obj,
                adm_area,
                district,
                occupancy,
            ) = row

            coords = coordinates
            try:
                if isinstance(coordinates, str):
                    import json

                    coords = json.loads(coordinates)
            except Exception:
                coords = coordinates

            result.append(
                {
                    "id": pid,
                    "description": description,
                    "coordinates": coords,
                    "name": name,
                    "name_obj": name_obj,
                    "adm_area": adm_area,
                    "district": district,
                    "occupancy": occupancy,
                }
            )
        return result
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database error")


@router.get("/parking/{parking_id}")
def get_parking(parking_id: int):
    try:
        row = ParkingsDAO.get_by_id(parking_id)

        if row is None:
            raise HTTPException(status_code=404, detail="Parking not found")

        (
            pid,
            description,
            coordinates,
            name,
            name_obj,
            adm_area,
            district,
            occupancy,
        ) = row

        coords = coordinates
        try:
            if isinstance(coordinates, str):
                import json

                coords = json.loads(coordinates)
        except Exception:
            coords = coordinates

        return {
            "id": pid,
            "description": description,
            "coordinates": coords,
            "name": name,
            "name_obj": name_obj,
            "adm_area": adm_area,
            "district": district,
            "occupancy": occupancy,
        }
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database error")


@router.get("/parking_fields/{parking_id}")
def get_parking_fields(parking_id: int, fields: str):
    try:
        selected_fields = ",".join([f.strip() for f in fields.split(",")])
        row = ParkingsDAO.get_fields(parking_id, selected_fields)

        if row is None:
            return {"error": "Parking not found"}

        result = dict(zip(selected_fields.split(","), row))
        return result

    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database error")


# тут поправить если мы храним координаты как [число, число], а не, как я, в виде словаря
@router.get("/parkinggeojson/{parking_id}")
def get_parking_geojson(parking_id: int):
    try:
        row = ParkingsDAO.get_geojson(parking_id)
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
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database error")


@router.post("/parkings", status_code=201)
def create_parking(parking: ParkingCreate):
    try:
        created_parking = ParkingsDAO.create(
            parking.description,
            parking.coordinates.model_dump_json(),  # Используем json-строку для jsonb поля
            parking.name,
            parking.name_obj,
            parking.adm_area,
            parking.district,
            parking.occupancy
        )
        fields = ["id", "name", "coordinates"]
        return dict(zip(fields, created_parking))
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database error")


@router.put("/parking/{parking_id}")
def update_parking(parking_id: int, parking: ParkingUpdate):
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
