from fastapi import APIRouter


router = APIRouter(
    prefix="/api/v1/faculty", # base path
    tags=["faculty"]
)

# API ENDPOINTS

# @router.get("/name)