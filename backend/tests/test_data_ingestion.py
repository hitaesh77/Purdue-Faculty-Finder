import json
from backend.data_ingestion import load_data_from_json, ingest_faculty_data
from backend.db.models import Faculty

"""
Unit tests for data ingestion functions.
Goals:
  - load_data_from_json correctly loads JSON data and returns list
  - ingest_faculty_data adds new faculty to the database
  - ingest_faculty_data skips duplicates based on name
"""

def test_load_data_from_json(tmp_path):
    fp = tmp_path / "data.json"
    data = [{"name": "A"}]
    fp.write_text(json.dumps(data))
    out = load_data_from_json(str(fp))
    assert out == data

def test_ingest_faculty_data_adds(db):
    data = [{"name": "John", "personal_webpage": "x", "research_interests": "y"}]
    ingest_faculty_data(db, data)
    q = db.query(Faculty).all()
    assert len(q) == 1
    assert q[0].name == "John"

def test_ingest_faculty_data_skips_duplicates(db):
    data = [{"name": "John"}]
    ingest_faculty_data(db, data)
    ingest_faculty_data(db, data)
    q = db.query(Faculty).all()
    assert len(q) == 1
