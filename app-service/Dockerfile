# app-service/Dockerfile

# ── Base image ────────────────────────────────────────────────
FROM python:3.11-slim

# ── Prevents .pyc files + enables stdout/stderr logging ───────
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# ── Working directory inside container ───────────────────────
WORKDIR /app

# ── Install dependencies first (layer caching) ───────────────
# Copied separately so Docker cache isn't busted on code changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Copy application code ─────────────────────────────────────
COPY . .

# ── Expose port ───────────────────────────────────────────────
EXPOSE 5001

# ── Run with Gunicorn in production ──────────────────────────
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--workers", "2", "run:app"]
