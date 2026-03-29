from fastapi import APIRouter, HTTPException
import  psycopg2

from dao.bus_dao import BusDAO
from schemas.busModels import BusCreate, BusUpdate

router = APIRouter()

def _row_to_dict(row) -> dict:
    id, name, description = row
    return {
        "id": id,
        "name": name,
        "description": description
    }

@router.get("/bus/all")
def get_all_bus():
    try:
        rows = BusDAO.get_all()
        return [_row_to_dict(row) for row in rows]
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database error")

@router.get("/bus/{bus_id}")
def get_by_id(bus_id: int):
    try:
        row = BusDAO.get_by_id(bus_id)
        if row is None:
            raise HTTPException(status_code=404, detail="SIM stop not found")
        return _row_to_dict(row)
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database error")

@router.post("/bus")
def create_bus(bus: BusCreate):
    try:
        row = BusDAO.create(
            name=bus.name,
            description=bus.description
        )
        return _row_to_dict(row)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/bus/{bus_id}")
def update_bus(bus_id: int, bus: BusUpdate):
    try:
        row = BusDAO.update(bus_id, bus)
        if row is None:
            raise HTTPException(status_code=404, detail="Bus not found")
        return _row_to_dict(row)
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database error")

@router.delete("/bus/{bus_id}")
def delete_bus(bus_id: int):
    try:
        deleted = BusDAO.delete(bus_id)
        if deleted is None:
            raise HTTPException(status_code=404, detail="Bus not found")
        return {"status": "deleted", "id": deleted[0]}
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database error")