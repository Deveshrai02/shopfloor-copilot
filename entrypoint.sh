#!/bin/sh
# entrypoint.sh — starts both services inside the single Spaces container.
#
# uvicorn runs in the background (port 8000, loopback only).
# Streamlit runs in the foreground on port 7860 so Docker tracks its PID.
# If Streamlit exits, the container exits and Spaces will restart it.

set -e

echo "[entrypoint] Starting Mock MES API on port 8000..."
uvicorn app.mock_mes_api:app --host 127.0.0.1 --port 8000 &

# Give the API a moment to bind before Streamlit makes its first tool call
sleep 2

echo "[entrypoint] Starting Streamlit on port 7860..."
exec streamlit run app/streamlit_app.py \
  --server.address 0.0.0.0 \
  --server.port 7860 \
  --server.headless true \
  --server.fileWatcherType none
