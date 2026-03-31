import psycopg2
from fastapi import APIRouter, HTTPException

from dao.cv_dao import CvDAO
from schemas.cvModels import ParkingUpdate

from redis_client import redis_client as redis

router = APIRouter()

OCCUPANCY_CACHE_TTL = 60

@router.get("/data/")
def get_cvdata():
    try:
        row = CvDAO.get_data()
        if row is None:
            raise HTTPException(status_code=404, detail="Camera not found")
        return row
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database error")


@router.patch("/occupancy/{id_parking}")
def update_occupancy(id_parking: int, parking: ParkingUpdate):
    # Обновляем кэш с TTL — теперь данные автоматически устаревают через OCCUPANCY_CACHE_TTL секунд
    redis.set(f"parking:{id_parking}:occupancy", parking.occupancy, ex=OCCUPANCY_CACHE_TTL)

    try:
        row_count = CvDAO.update_occupancy(id_parking, parking.occupancy)
        if row_count == 0:
            raise HTTPException(status_code=404, detail="Parking not found")
        return {"message": f"Occupancy for parking ID {id_parking} successfully updated"}
    except psycopg2.Error:
        raise HTTPException(status_code=400, detail="Failed to update occupancy")


@router.get("/parking/{id_parking}/status")
def get_status(id_parking: int):
    occupancy = redis.get(f"parking:{id_parking}:occupancy")

    if occupancy is not None:
        # Данные есть в кэше и они ещё актуальны (TTL не истёк)
        return {
            "id_parking": id_parking,
            "occupancy": int(occupancy),
            "source": "cache",
        }

    # Кэш пуст (либо TTL истёк) — берём актуальные данные из БД
    try:
        row = CvDAO.get_status(id_parking)
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database error")

    if row is None or row[0] is None:
        raise HTTPException(
            status_code=404,
            detail="Parking not found in cache or DB"
        )

    # Кладём свежие данные в кэш с TTL
    try:
        redis.set(f"parking:{id_parking}:occupancy", row[0], ex=OCCUPANCY_CACHE_TTL)
    except Exception:
        pass

    return {
        "id_parking": id_parking,
        "occupancy": int(row[0]),
        "source": "db",
    }