from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.router import router
from backend.db.database import engine, SessionLocal
from backend.db.models import Base
from backend.data_ingestion import load_data_from_json, ingest_faculty_data
import os
from contextlib import asynccontextmanager

# ensure tables exist
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    from backend.data_ingestion import BASE_DIR
    json_path = os.path.join(BASE_DIR, "faculty_data_complete.json")

    data = load_data_from_json(json_path)
    if data:
        db = SessionLocal()
        ingest_faculty_data(db, data)
        db.close()

    yield  # This is where FastAPI runs the app

    # Optional: add shutdown logic here if needed

app = FastAPI(
    title="Purdue ECE Faculty Finder API",
    description="RESTful API for searching ECE faculty by name and research interests.",
    version="v1",
    lifespan=lifespan
)

# 2. CORS Middleware (Essential for connecting Frontend/Next.js)
origins = [
    "http://localhost:3000", 
    "https://purdue-faculty-finder.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Include the Router
app.include_router(router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Faculty Finder API. Go to /docs for endpoints."}