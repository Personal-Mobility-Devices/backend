from fastapi import APIRouter, HTTPException
import  psycopg2

from dao.bus_dao import BusDAO
from schemas.busModels import BusCreate

router = APIRouter()

@router.get("/bus/all")
def get_all_bus():
    pass

@router.get("/bus/{bus_id}")
def get_by_id(bus_id: int):
    pass

@router.post("/bus")
def create_bus(bus: BusCreate):
    pass

@router.put("/bus/{bus_id}")
def update_bus(bus_id: int, bus: BusCreate):
    pass

@router.delete("/bus/{bus_id}")
def delete_bus(bus_id: int):
    pass