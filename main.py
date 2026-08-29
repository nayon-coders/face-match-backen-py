from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import os

import database, face_service
from database import get_db

import pm_models
import models
database.Base.metadata.create_all(bind=database.engine)

from routers import clients

app = FastAPI(title="FaceAttend API SaaS")
os.makedirs("uploads", exist_ok=True)

# Setup CORS for the Admin Panel
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(clients.router, prefix="/api")

@app.on_event("startup")
def startup_event():
    print("DEBUG: Running startup event...")
    face_service.preload_models()

def verify_api_key(x_api_key: str = Header(...), db: Session = Depends(get_db)):
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API Key missing")
    client = db.query(pm_models.Client).filter(pm_models.Client.api_key == x_api_key).first()
    if not client:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    if client.status != "Active":
        raise HTTPException(status_code=403, detail="Client account is inactive")
    return client

from typing import Optional
from datetime import datetime
import requests

def fetch_image_from_url(url: str) -> bytes:
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.content
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch image from URL: {url}")

@app.post("/api/v1/face/match")
def match_faces(
    image1: Optional[UploadFile] = File(None),
    image2: Optional[UploadFile] = File(None),
    image1_url: Optional[str] = Form(None),
    image2_url: Optional[str] = Form(None),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    client: pm_models.Client = Depends(verify_api_key)
):
    print(f"DEBUG: match_faces called by client {client.client_code}")
    
    if not image1 and not image1_url:
        raise HTTPException(status_code=400, detail="Must provide either image1 (File) or image1_url (String)")
    if not image2 and not image2_url:
        raise HTTPException(status_code=400, detail="Must provide either image2 (File) or image2_url (String)")

    image1_bytes = image1.file.read() if image1 else fetch_image_from_url(image1_url)
    image2_bytes = image2.file.read() if image2 else fetch_image_from_url(image2_url)
    
    result = face_service.match_two_images(image1_bytes, image2_bytes)
    
    if result.get("error"):
        raise HTTPException(status_code=400, detail=result["error"])
        
    now = datetime.now()
    
    return {
        "match": result["match"],
        "distance": result["distance"],
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
        "latitude": latitude,
        "longitude": longitude
    }
