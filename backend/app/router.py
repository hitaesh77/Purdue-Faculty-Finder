from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from typing import List
from .schemas import FacultyNameOut
from backend.db.database import get_db
from backend.db import models


router = APIRouter(
    prefix="/api/v1/faculty", # base path
    tags=["faculty"]
)

# API ENDPOINTS

# Search faculty by name and return a list
@router.get("/search/name", response_model=List[FacultyNameOut])
def search_faculty_by_name(
    q: str = Query(..., min_length=1),
    db: Session = Depends(get_db)
):
    try:
        # Case-insensitive substring match
        faculty_list = db.query(models.Faculty).filter(models.Faculty.name.ilike(f"%{q}%")).all()

        # Convert to response format
        results = [FacultyNameOut(id=f.id, name=f.name) for f in faculty_list]

        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
