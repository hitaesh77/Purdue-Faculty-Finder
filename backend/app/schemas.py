from pydantic import BaseModel
from typing import Optional

class FacultyOut(BaseModel):
    id: int
    name: str
    webpage_url: Optional[str]
    research_interests: Optional[str]

    # future fields for returning by research interest search

    class Config:
        # allows ORM objects to be returned directly
        from_attributes = True

class FacultyNameOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True