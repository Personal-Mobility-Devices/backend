from fastapi import APIRouter, HTTPException
import psycopg2

from schemas.simStopsModels import SIMStopCreate, SIMStopUpdate

router = APIRouter()

@router.get("/sim_stops/all")
def get_all_sim_stops():
    pass

@router.get("/sim_stops/{stop_id}")
def get_sim_stop(stop_id: int):
    pass

@router.get("/sim_stops/in_area")
def get_in_area(
    min_lon: float,
    max_lon: float,
    min_lat: float,
    max_lat: float
):
    pass

@router.post("/sim_stops")
def create_sim_stops(sim_stops: SIMStopCreate):
    pass

@router.put("sim_stops/{stop_id}")
def update_sim_stops(stop_id: int, sim_stop: SIMStopUpdate):
    pass

@router.delete("sim_stops/{stop_id}")
def delete_sim_stop(stop_id: int):
    pass