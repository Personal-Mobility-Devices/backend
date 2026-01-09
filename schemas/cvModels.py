from pydantic import BaseModel


class ParkingUpdate(BaseModel):
    occupancy: int
