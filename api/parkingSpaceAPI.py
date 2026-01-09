import psycopg2
from fastapi import APIRouter, HTTPException

from dao.parking_space_dao import ParkingSpaceDAO
from schemas.parkingSpaceModels import ParkingSpaceCreate, ParkingSpaceUpdate

router = APIRouter()


@router.get("/parking_spaces/all")
def get_all_parking_spaces():
    try:
        return ParkingSpaceDAO.get_all()
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database error")


@router.get("/parking_space/{space_id}")
def get_parking_space_by_id(space_id: str):  # UUID в БД, поэтому передаем как строку
    try:
        row = ParkingSpaceDAO.get_by_id(space_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Parking space not found")
        return row
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database error")


@router.get("/parking_spaces/by_parking/{parking_id}")
def get_parking_spaces_by_parking_id(parking_id: int):
    try:
        return ParkingSpaceDAO.get_all_by_parking_id(parking_id)
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database error")


@router.post("/parking_space", status_code=201)
def create_parking_space(space: ParkingSpaceCreate):
    try:
        created_space = ParkingSpaceDAO.create(
            space.coordinates.model_dump_json(),
            space.id_parking
        )
        fields = ["id", "id_parking"]
        return dict(zip(fields, created_space))
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database error")


@router.put("/parking_space/{space_id}")
def update_parking_space(space_id: str, space_update: ParkingSpaceUpdate):
    if space_update.coordinates is None:
        raise HTTPException(status_code=400, detail="No fields to update")

    try:
        updated = ParkingSpaceDAO.update(space_id, space_update.coordinates.model_dump_json())
        if updated is None:
            raise HTTPException(status_code=404, detail="Parking space not found")

        fields = ["id", "id_parking"]
        return dict(zip(fields, updated))
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database error")


@router.delete("/parking_space/{space_id}")
def delete_parking_space(space_id: str):
    try:
        deleted = ParkingSpaceDAO.delete(space_id)
        if deleted is None:
            raise HTTPException(status_code=404, detail="Parking space not found")
        return {"status": "deleted", "id": deleted[0]}
    except psycopg2.Error:
        raise HTTPException(status_code=400, detail="Failed to delete parking space")
