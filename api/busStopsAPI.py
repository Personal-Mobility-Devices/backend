from fastapi import APIRouter, HTTPException
import psycopg2

from dao.bus_stops_dao import BusStopsDAO
from schemas.busStopsModels import BusStopCreate, BusStopUpdate

router = APIRouter()


@router.get("/bus_stops/all")
def get_all_bus_stops():
    try:
        rows = BusStopsDAO.get_all()
        result = []

        for row in rows:
            id, description, coordinates, adm_area, district = row

            result.append({
                "id": id,
                "description": description,
                "coordinates": coordinates,
                "adm_area": adm_area,
                "district": district
            })

        return result

    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database error")

@router.get("/bus_stops/in_area")
def get_in_area(
    min_lon: float,
    max_lon: float,
    min_lat: float,
    max_lat: float
):
    pass
@router.get("/bus_stop/{stop_id}")
def get_bus_stop(stop_id: int):
    try:
        row = BusStopsDAO.get_by_id(stop_id)

        if row is None:
            raise HTTPException(status_code=404, detail="Bus stop not found")

        id, description, coordinates, adm_area, district = row

        return {
            "id": id,
            "description": description,
            "coordinates": coordinates,
            "adm_area": adm_area,
            "district": district
        }

    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database error")


@router.post("/bus_stops", status_code=201)
def create_bus_stop(stop: BusStopCreate):
    try:
        created = BusStopsDAO.create(
            stop.description,
            stop.coordinates.model_dump_json(),
            stop.adm_area,
            stop.district
        )

        return {"id": created[0]}

    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database error")


@router.put("/bus_stop/{stop_id}")
def update_bus_stop(stop_id: int, stop: BusStopUpdate):
    try:
        updated = BusStopsDAO.update(stop_id, stop)
        return {"status": "updated", "id": updated[0]}

    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database error")


@router.delete("/bus_stop/{stop_id}")
def delete_bus_stop(stop_id: int):
    try:
        deleted = BusStopsDAO.delete(stop_id)
        return {"status": "deleted", "id": deleted[0]}

    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database error")
