from fastapi import FastAPI

from api.camerasAPI import router as cameras_router
from api.cvAPI import router as cv_router
from api.favoriteParkingsAPI import router as favorite_parkings_router
from api.parkingSpaceAPI import router as parking_space_router
from api.parkingsAPI import router as parking_router
from api.usersAPI import router as user_router
from database import init_db, close_db

app = FastAPI()


# Инициализация пула соединений к БД в FastAPI
@app.on_event("startup")
async def startup():
    await init_db()


@app.on_event("shutdown")
async def shutdown():
    await close_db()


@app.get("/")
def home():
    return {"status": "System is running"}


app.include_router(parking_router, prefix="/api", tags=["Parkings"])
app.include_router(parking_space_router, prefix="/parking_spaces", tags=["Parking spaces"])
app.include_router(favorite_parkings_router, prefix="/favorite_parkings", tags=["Favorite parkings"])
app.include_router(user_router, prefix="/api", tags=["Users"])
app.include_router(cv_router, prefix="/cv", tags=["CV"])
app.include_router(cameras_router, prefix="/cv", tags=["Cameras"])
