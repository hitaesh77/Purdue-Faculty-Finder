from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.router import router
from backend.db.database import engine
from backend.db.models import Base

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Purdue ECE Faculty Finder API",
    description="RESTful API for searching ECE faculty by name and research interests.",
    version="v1"
)

# 2. CORS Middleware (Essential for connecting Frontend/Next.js)
origins = [
    "http://localhost:3000", 
    # add deployed url later
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