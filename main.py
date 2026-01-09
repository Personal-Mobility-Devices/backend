from fastapi import FastAPI
from api.parkingsAPI import router as parking_router
from api.usersAPI import router as user_router
from api.cvAPI import router as cv_router
from api.parkingSpaceAPI import router as parking_space_router
from api.favoriteParkingsAPI import router as favorite_parkings_router
from api.camerasAPI import router as cameras_router
from api.authAPI import router as auth_router

app = FastAPI()

@app.get("/")
def home():
    return {"status": "System is running"}



app.include_router(parking_router, prefix="/api", tags=["Parkings"])
app.include_router(parking_space_router, prefix="/parking_spaces", tags=["Parking spaces"])
app.include_router(favorite_parkings_router, prefix="/favorite_parkings", tags=["Favorite parkings"])
app.include_router(user_router, prefix="/api", tags=["Users"])
app.include_router(auth_router, prefix="/api", tags=["Auth"])
app.include_router(cv_router, prefix="/cv", tags=["CV"])
app.include_router(cameras_router, prefix="/cv", tags=["Cameras"])
