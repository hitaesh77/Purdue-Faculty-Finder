from backend.db.database import engine
from backend.db.models import Base

def create_database():
    """Create SQLite database file and all tables (if not present)."""
    Base.metadata.create_all(bind=engine)
    print(f"Initialized database at: {engine.url}")

if __name__ == "__main__":
    create_database()