#!/bin/bash
echo "Starting FastAPI Backend Server..."
echo ""
cd "$(dirname "$0")"
python -m uvicorn app:app --reload

