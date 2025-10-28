# init_db.py
from backend.db.database import engine, SessionLocal
from backend.db import models
from backend.db.models import Faculty

def init():
    print("Creating tables...")
    models.Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")

    print("Adding initial users...")
    session = SessionLocal()
    existing_faculty = session.query(Faculty).all()
    if not existing_faculty:
        pass
    else:
        print("Faculty records already exist. Skipping initial data add.")

if __name__ == "__main__":
    init()
