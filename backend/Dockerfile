# ============================================================
#  Backend Dockerfile  (Phase 2 baseline)
# ============================================================
FROM python:3.11-slim

# system deps for psycopg2, audio (ffmpeg added in later phase)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# install python deps first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# copy source last
COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
