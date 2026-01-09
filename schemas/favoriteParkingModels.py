from pydantic import BaseModel


class FavoriteParkingAdd(BaseModel):
    id_user: int
    id_parking: int
