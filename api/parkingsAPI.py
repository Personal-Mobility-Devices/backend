import psycopg2
from fastapi import APIRouter, HTTPException

from dao.parkings_dao import ParkingsDAO
from schemas.parkingModels import ParkingCreate, ParkingUpdate

router = APIRouter()


@router.get("/parkings/all")
async def get_all_parkings():
    try:
        rows = await ParkingsDAO.get_all()
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
async def get_parkings_in_area(lat_min: float, lat_max: float, lon_min: float, lon_max: float):
    try:
        rows = await ParkingsDAO.get_in_area(lat_min, lat_max, lon_min, lon_max)
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
async def get_parking(parking_id: int):
    try:
        row = await ParkingsDAO.get_by_id(parking_id)

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
async def get_parking_fields(parking_id: int, fields: str):
    try:
        selected_fields = ",".join([f.strip() for f in fields.split(",")])
        row = await ParkingsDAO.get_fields(parking_id, selected_fields)

        if row is None:
            return {"error": "Parking not found"}

        result = dict(zip(selected_fields.split(","), row))
        return result

    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database error")


# тут поправить если мы храним координаты как [число, число], а не, как я, в виде словаря
@router.get("/parkinggeojson/{parking_id}")
async def get_parking_geojson(parking_id: int):
    try:
        row = await ParkingsDAO.get_geojson(parking_id)
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
async def create_parking(parking: ParkingCreate):
    try:
        created_parking = await ParkingsDAO.create(
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
async def update_parking(parking_id: int, parking: ParkingUpdate):
    updates = []
    params = []
    idx = 1
    # Динамически строим запрос UPDATE
    if parking.description is not None:
        updates.append(f"description = ${idx}")
        params.append(parking.description)
        idx += 1
    if parking.coordinates is not None:
        updates.append(f"coordinates = ${idx}")
        params.append(parking.coordinates.model_dump_json())
        idx += 1
    if parking.name is not None:
        updates.append(f"name = ${idx}")
        params.append(parking.name)
        idx += 1
    if parking.name_obj is not None:
        updates.append(f"name_obj = ${idx}")
        params.append(parking.name_obj)
        idx += 1
    if parking.adm_area is not None:
        updates.append(f"adm_area = ${idx}")
        params.append(parking.adm_area)
        idx += 1
    if parking.district is not None:
        updates.append(f"district = ${idx}")
        params.append(parking.district)
        idx += 1
    if parking.occupancy is not None:
        updates.append(f"occupancy = ${idx}")
        params.append(parking.occupancy)
        idx += 1

    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    params.append(parking_id)  # ID в конец параметров для WHERE условия

    # В asyncpg нет %s, как это было в psycopg2, для передачи аргументов используется %1, %2 и так далее
    where_idx = idx  # текущий порядковый номер idx для аргумента

    try:
        updated = await ParkingsDAO.update(updates, where_idx, params)
        fields = ["id", "name", "occupancy"]
        return dict(zip(fields, updated))
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database error")


@router.delete("/parking/{parking_id}")
async def delete_parking(parking_id: int):
    try:
        deleted = await ParkingsDAO.delete(parking_id)
        return {"status": "deleted", "id": deleted[0]}
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database error")
