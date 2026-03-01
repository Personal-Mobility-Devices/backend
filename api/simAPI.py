from fastapi import APIRouter, HTTPException
import psycopg2

from dao.sim_stops_dao import SimStopsDAO
from schemas.simStopsModels import SIMStopCreate, SIMStopUpdate

router = APIRouter()


def _row_to_dict(row) -> dict:
    id, description, lon, lat, adm_area, district, free_sims = row
    return {
        "id": id,
        "description": description,
        "coordinates": {"lon": lon, "lat": lat},
        "adm_area": adm_area,
        "district": district,
        "free_sims": free_sims,
    }


@router.get("/sim_stops/all")
def get_all_sim_stops():
    try:
        rows = SimStopsDAO.get_all()
        return [_row_to_dict(row) for row in rows]
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database error")


@router.get("/sim_stops/in_area")
def get_in_area(
    min_lat: float,
    max_lat: float,
    min_lon: float,
    max_lon: float,
):
    """
    Поиск остановок СИМ в прямоугольной зоне видимости карты.
    Параметры — границы видимой области: min_lat, max_lat, min_lon, max_lon.
    """
    try:
        rows = SimStopsDAO.get_in_area(min_lat, max_lat, min_lon, max_lon)
        return [_row_to_dict(row) for row in rows]
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database error")


@router.get("/sim_stops/{stop_id}")
def get_sim_stop(stop_id: int):
    try:
        row = SimStopsDAO.get_by_id(stop_id)
        if row is None:
            raise HTTPException(status_code=404, detail="SIM stop not found")
        return _row_to_dict(row)
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database error")


@router.post("/sim_stops", status_code=201)
def create_sim_stop(sim_stop: SIMStopCreate):
    try:
        row = SimStopsDAO.create(
            description=sim_stop.description,
            lat=sim_stop.coordinates.lat,
            lon=sim_stop.coordinates.lon,
            adm_area=sim_stop.adm_area,
            district=sim_stop.district,
            free_sims=sim_stop.free_sims,
        )
        return _row_to_dict(row)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/sim_stops/{stop_id}")
def update_sim_stop(stop_id: int, sim_stop: SIMStopUpdate):
    try:
        row = SimStopsDAO.update(stop_id, sim_stop)
        if row is None:
            raise HTTPException(status_code=404, detail="SIM stop not found")
        return _row_to_dict(row)
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database error")


@router.delete("/sim_stops/{stop_id}")
def delete_sim_stop(stop_id: int):
    try:
        deleted = SimStopsDAO.delete(stop_id)
        if deleted is None:
            raise HTTPException(status_code=404, detail="SIM stop not found")
        return {"status": "deleted", "id": deleted[0]}
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database error")