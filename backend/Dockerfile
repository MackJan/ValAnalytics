FROM python:3.9-slim

WORKDIR /app

# Install backend dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
# Copy migrations (Alembic)
COPY alembic/ ./alembic/
COPY alembic.ini ./

# Default command: run FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
