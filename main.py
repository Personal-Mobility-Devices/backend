from fastapi import FastAPI
from parkingsAPI import router as parking_router
from usersAPI import router as user_router
from cvAPI import router as cv_router

app = FastAPI()

@app.get("/")
def home():
    return {"status": "System is running"}



app.include_router(parking_router, prefix="/api", tags=["Parkings"])
app.include_router(user_router, prefix="/api", tags=["Users"])
app.include_router(cv_router, prefix="/cv", tags=["CV"])