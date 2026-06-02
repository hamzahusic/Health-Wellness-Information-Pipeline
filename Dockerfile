# Dockerfile
# ─────────────────────────────────────────────────────────────
# Single-stage build — python:3.12-slim (Debian, minimal footprint).
# ─────────────────────────────────────────────────────────────

FROM python:3.12-slim

LABEL maintainer="student@ibu.edu.ba"
LABEL description="Health & Wellness Information Pipeline — Dash Dashboard"

WORKDIR /app

# ── Layer 1: dependencies ─────────────────────────────────────
# Copy requirements first so Docker can cache this layer.
# pip install is skipped on subsequent builds unless
# requirements.txt changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Layer 2: application code ─────────────────────────────────
COPY . .

# Port the Dash server listens on (documentation only — the
# actual binding is done by Gunicorn via CMD).
EXPOSE 8050

# ── Runtime ───────────────────────────────────────────────────
# Gunicorn replaces the Flask dev server in production:
#   --workers 2     two processes (safe for low-memory hosts)
#   --timeout 120   allow slow first-load queries to complete
#   app:server      the `server` variable exposed in app.py
CMD ["gunicorn", \
     "--bind", "0.0.0.0:8050", \
     "--workers", "2", \
     "--timeout", "120", \
     "app:server"]