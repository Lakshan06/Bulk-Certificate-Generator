from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os
from app.database import engine, Base
from app import models

from app.routers import jobs, certificates

# Create all tables in the database
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Bulk Certificate Generator", version="1.0.0")

app.include_router(jobs.router, prefix="/api/v1")
app.include_router(certificates.router, prefix="/api/v1")

os.makedirs("app/static", exist_ok=True)
app.mount("/ui", StaticFiles(directory="app/static", html=True), name="ui")

@app.get("/")
def read_root():
    return {"message": "Welcome to Bulk Certificate Generator API"}
