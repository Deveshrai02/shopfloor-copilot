# ── Stage: runtime ────────────────────────────────────────────────────────────
# python:3.11-slim keeps the image small (~130 MB compressed) while providing
# a glibc runtime compatible with faiss-cpu's pre-built wheels. Alpine is
# avoided because faiss-cpu has no musl wheel and building from source is slow.
FROM python:3.11-slim

# Prevents .pyc files and enables unbuffered stdout so logs appear immediately
# in `docker logs` / `docker-compose logs`.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# ── Dependency layer (cached unless requirements.txt changes) ─────────────────
# Copying requirements.txt alone before the rest of the source means Docker
# reuses this layer on every rebuild where only application code changed.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Application code ──────────────────────────────────────────────────────────
COPY app/       ./app/
COPY data/sops/ ./data/sops/

# data/index/ is intentionally excluded — the index is built at startup so it
# always reflects the SOP files present in the image.
