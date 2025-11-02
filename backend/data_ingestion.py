import json
import os
from datetime import datetime
from sqlalchemy.orm import Session
from backend.db.database import SessionLocal, engine
from backend.db.models import Faculty, Base
from backend.scraper import log_message, LOG_FILE

# --- Configuration ---
BASE_DIR = os.path.dirname(__file__)
DATA_FILE_PATH = os.path.join(BASE_DIR, "faculty_data_complete.json")
# --- End Configuration ---

def load_data_from_json(file_path: str) -> list:
    """Reads and parses the faculty data from the JSON file."""

    if not os.path.exists(file_path):
        print(f"Error: Data file not found at {file_path}")
        return []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def ingest_faculty_data(db: Session, faculty_data: list):
    """Inserts faculty data into the database, checking for duplicates."""
    
    log_message(f"--- Starting data ingestion into database ---", "a")

    total_added = 0
    
    for item in faculty_data:
        log_message(f"Processing: {item['name']}", "a")
        existing_faculty = db.query(Faculty).filter(Faculty.name == item["name"]).first()

        # EDIT LATER FOR UPDATING
        if existing_faculty:
            print(f"Skipping: {item['name']} already exists.")
            continue
            
        # Create a new Faculty object
        new_faculty = Faculty(
            name=item["name"],
            webpage_url=item.get("personal_webpage"), 
            research_interests=item.get("research_interests"),
            created_at=datetime.now()
        )
        
        # Add the new object to the session
        db.add(new_faculty)
        total_added += 1

    # Commit all changes to the database
    db.commit()
    log_message(f"--- Data ingestion complete: {total_added} new records added ---", "a")

    print(f"\nSuccessfully added {total_added} new faculty records.")

if __name__ == "__main__":
    # Ensure tables exist before trying to insert data (safe to call again)
    print("Ensuring tables are initialized...")
    Base.metadata.create_all(bind=engine) 
    
    # 1. Load the data from the JSON file
    data_to_ingest = load_data_from_json(DATA_FILE_PATH)
    
    if data_to_ingest:
        # 2. Get a database session
        db_session = SessionLocal()
        
        # 3. Ingest the data
        print(f"Starting ingestion of {len(data_to_ingest)} records...")
        ingest_faculty_data(db_session, data_to_ingest)
        
        # 4. Close the session
        db_session.close()
    
    print("Data ingestion complete.")