from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class Faculty(Base):
    __tablename__ = "faculty"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    webpage_url = Column(String)
    research_interests = Column(String)
    created_at = Column(DateTime, default=datetime.now())
