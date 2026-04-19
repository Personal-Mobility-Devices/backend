from pydantic import BaseModel


class Coordinates(BaseModel):
    lat: float
    lon: float

class PolygonCooridinates(BaseModel):
    coords: list[Coordinates]