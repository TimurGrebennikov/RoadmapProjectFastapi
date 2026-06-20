##!/bin/bash
#set -e
#
#echo "Waiting for PostgreSQL to be ready..."
#sleep 5
#
#echo "Running database migrations..."
#/app/alembic upgrade head
#
#echo "Starting FastAPI application..."
#exec /app/.venv/bin/uvicorn src.main:app --host 0.0.0.0 --port 8000