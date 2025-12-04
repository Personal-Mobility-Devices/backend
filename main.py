from fastapi import FastAPI
from parkingsAPI import app as parking_app

app = FastAPI()

@app.get("/")
def home():
    return {"status": "ok"}

app.mount("/api", parking_app)