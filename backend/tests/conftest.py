import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.db.models import Base
from backend.db.database import get_db
from backend.app.main import app

"""
Fixtures for testing the FastAPI application with a temporary in-memory database.
Goals:
  - Provide a test database session
  - Provide a test client for API requests
"""

# fixture for creating an in-memory SQLite database
@pytest.fixture(scope="session")
def test_engine():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    return engine

# fixture for creating a new session for each test
@pytest.fixture(scope="session")
def TestSessionLocal(test_engine):
    return sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# fixture for providing a database session to tests
@pytest.fixture
def db(TestSessionLocal):
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()

# fixture for providing a test client for API requests
@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)
