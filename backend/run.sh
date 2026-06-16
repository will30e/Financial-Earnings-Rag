#!/bin/bash
# Start the backend API server.
# Creates the venv on first run if it doesn't exist.

set -e
cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
  echo "Creating virtualenv..."
  python3 -m venv .venv
  .venv/bin/pip install --upgrade pip -q
  .venv/bin/pip install -r requirements.txt -q
fi

[ -f .env ] || cp .env.example .env

.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
