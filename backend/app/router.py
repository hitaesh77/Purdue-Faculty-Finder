from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from typing import List
from .schemas import FacultyOut, FacultyNameOut
from backend.db.database import get_db
from backend.db import models
from backend.data_ingestion import ingest_faculty_data
from backend.scraper import scrape_faculty_directory, enrich_faculty_data
from backend.app.auth import verify_admin


router = APIRouter(
    prefix="/api/v1", # base path
    tags=["faculty"]
)

# API ENDPOINTS
    
# Search faculty by ID and return full details
@router.get("/faculty/{faculty_id}", response_model=FacultyOut)
def get_faculty_by_id(
    faculty_id: int,
    db: Session = Depends(get_db)
):
    try:
        faculty = db.query(models.Faculty).filter(models.Faculty.id == faculty_id).first()
        if not faculty:
            raise HTTPException(status_code=404, detail="Faculty not found")
        
        return FacultyOut(
            id=faculty.id,
            name=faculty.name,
            webpage_url=faculty.webpage_url,
            research_interests=faculty.research_interests
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
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

# search faculty by research interest and return a list
@router.get("/search/research", response_model=List[FacultyNameOut])
def search_faculty_by_research_interest(
    q: str = Query(..., min_length=1),
    db: Session = Depends(get_db)
):
    try:
        # Case-insensitive substring match in research interests
        faculty_list = db.query(models.Faculty).filter(models.Faculty.research_interests.ilike(f"%{q}%")).all()

        # Convert to response format
        results = [FacultyNameOut(id=f.id, name=f.name) for f in faculty_list]

        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
# get all facult data and return a list
@router.get("/search/all", response_model=List[FacultyNameOut])
def get_all_faculty(
    db: Session = Depends(get_db)
):
    try:
        faculty_list = db.query(models.Faculty).all()

        # Convert to response format
        results = [FacultyNameOut(id=f.id, name=f.name) for f in faculty_list]

        return results
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    
# update faculty data (admin only)
@router.post("/update")
def update_faculty(db: Session = Depends(get_db), _: bool = Depends(verify_admin)):
    try:
        raw_list = scrape_faculty_directory()
        if not raw_list:
            raise HTTPException(status_code=500, detail="Scrape failed")
        enriched = enrich_faculty_data(raw_list)
        ingest_faculty_data(db, enriched)
        return {"status": "ok", "record_count": len(enriched)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))