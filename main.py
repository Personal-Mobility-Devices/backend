from fastapi import FastAPI
from parkingsAPI import app as parking_app
from usersAPI import app as user_app
from cvAPI import app as cv_app

app = FastAPI()

@app.get("/")
def home():
    return {"status": "System is running"}



app.include_router(parking_app.router, prefix="/api", tags=["Parkings"])
app.include_router(user_app.router, prefix="/api", tags=["Users"])
app.include_router(cv_app.router, prefix="/cv", tags=["CV"])