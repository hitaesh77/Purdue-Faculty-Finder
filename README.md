# Purdue Faculty Finder

### [Link to Faculty Finder](https://purdue-faculty-finder.vercel.app/)

FastAPI backend and Next.js frontend for searching Purdue ECE faculty by name or research interests. The system scrapes official faculty pages, stores structured records in SQLite, and serves them through REST endpoints consumed by the Next.js UI.

## Features

- Full faculty search by name and research keywords  
- Individual faculty detail retrieval  
- Automated scraping of Purdue ECE faculty directory  
- Admin-protected update endpoint  
- Local SQLite persistence 
- Clean separation of backend and frontend

## Architecture

Backend services:

- `scraper.py`  
  Scrapes faculty directory and individual profile pages for names, profile URLs, personal websites, and research interests.

- `data_ingestion.py`  
  Loads scraped JSON data and inserts unique records into the database.

- `router.py`  
  Exposes REST endpoints for searching and retrieving faculty.

- `auth.py`  
  Provides admin verification using HTTP Basic authentication.

- `database.py` and `models.py`  
  SQLite database and SQLAlchemy ORM models.

Frontend:

- Next.js React application served separately.  
- Hosted at: https://purdue-faculty-finder.vercel.app

API:

- Hosted on Vercel or local development server.  
- Swagger documentation at `/docs` or `/redoc`.

## Tech Stack

- Python 3  
- FastAPI  
- SQLAlchemy  
- SQLite  
- BeautifulSoup4  
- Requests  
- Next.js  
- Vercel deployment for frontend
- GCP deployment for backend

## Folder Structure

* **`backend/`**
    * **`app/`** (Contains core FastAPI application components)
        * `router.py`
        * `auth.py`
        * `schemas.py`
        * `main.py` 
    * **`db/`** (Database-related files)
        * `models.py`
        * `database.py`
        * `init_db.py`
    * `scraper.py`
    * `data_ingestion.py`
* **`frontend/`** (Next.js separate directory)

## Setup

Clone the repository:

    git clone https://github.com/hitaesh77/Purdue-Faculty-Finder.git

    cd Purdue-Faculty-Finder/backend


Install dependencies:

    pip install -r requirements.txt

Initialize the database:

    python -m backend.db.init_db

## Local Development

Start FastAPI:

    uvicorn backend.main:app --reload

The API is available at:

    http://127.0.0.1:8000

Open API documentation:

    http://127.0.0.1:8000/docs

To populate the database from scraped data:

1. Run scraper:

       python -m backend.scraper

      This generates `faculty_data_complete.json`.

2. Ingest:

       python -m backend.data_ingestion

## API Endpoints

- `GET /api/v1/search/name?q=`  
  Case-insensitive faculty name search.

- `GET /api/v1/search/research?q=`  
  Search by research keywords.

- `GET /api/v1/faculty/{id}`  
  Returns full faculty record.

- `POST /api/v1/update`  
  Re-scrapes the directory and updates the database. Admin authentication required.

## Authentication

Admin credentials loaded from `.env`:

    ADMIN_USER=...
    ADMIN_PASS=...

Used for the `/api/v1/update` endpoint.

## Testing

Tests use pytest, FastAPI TestClient, and an SQLite in-memory database.

Coverage includes:

- Scraper HTML parsing  
- Data ingestion  
- Authentication logic

To run tests:

    python -m pytest 

## Deployment

Frontend deployed on Vercel.  
Backend deployed on GCP.

Environment variables required:

    ADMIN_USER
    ADMIN_PASS

## Contact

Author: Hitaesh Saravanarajan  
Repository: https://github.com/hitaesh77/Purdue-Faculty-Finder
