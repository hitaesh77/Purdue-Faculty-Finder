# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Copy backend folder
COPY backend/ ./backend

# Copy requirements.txt if you have one
COPY backend/requirements.txt ./backend/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r backend/requirements.txt

# Set environment variable for FastAPI to use the Cloud Run port
ENV PORT=8080

# Expose the port
EXPOSE 8080

# Create backend folder for DB/json if not exists
RUN mkdir -p /app/backend

# Run the FastAPI app
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8080"]
