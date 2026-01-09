import psycopg2
from fastapi import APIRouter, Depends, HTTPException, status

from dao.favorite_parkings_dao import FavoriteParkingsDAO
from schemas.favoriteParkingModels import FavoriteParkingAdd
from auth import get_current_user_id

router = APIRouter()


@router.get("/favorites/{user_id}")
def get_favorites(user_id: int, current_user_id: int = Depends(get_current_user_id)):
    if user_id != current_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    try:
        return FavoriteParkingsDAO.get(user_id)
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database error")


@router.post("/favorites", status_code=201)
def add_favorite_parking(
    fav_data: FavoriteParkingAdd,
    current_user_id: int = Depends(get_current_user_id),
):
    if fav_data.id_user != current_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    try:
        fav_id = FavoriteParkingsDAO.add(fav_data.id_user, fav_data.id_parking)[0]
        return {"id": fav_id, "message": "Parking added to favorites"}
    except psycopg2.errors.UniqueViolation:
        raise HTTPException(status_code=409, detail="Parking is already in user's favorites")
    except psycopg2.errors.ForeignKeyViolation:
        raise HTTPException(status_code=404, detail="User or Parking not found")
    except psycopg2.Error:
        raise HTTPException(status_code=400, detail="Failed to add favorite")


@router.delete("/favorites", status_code=204)
def remove_favorite_parking(
    id_user: int,
    id_parking: int,
    current_user_id: int = Depends(get_current_user_id),
):
    if id_user != current_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    try:
        deleted = FavoriteParkingsDAO.delete(id_user, id_parking)
        if deleted is None:
            raise HTTPException(status_code=404, detail="Favorite relationship not found")
    except psycopg2.Error:
        raise HTTPException(status_code=400, detail="Failed to delete favorite")
