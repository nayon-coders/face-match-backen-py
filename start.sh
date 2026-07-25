#!/bin/bash
# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
echo "Installing/Updating requirements..."
pip install fastapi uvicorn sqlalchemy pymysql python-multipart deepface tf-keras opencv-python-headless pydantic python-dotenv

echo "Starting FastAPI Server..."
uvicorn main:app --host 0.0.0.0 --port 8000
