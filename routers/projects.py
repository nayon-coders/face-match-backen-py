from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
import shutil
import os
import time
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from pm_schemas import ProjectCreate, ProjectUpdate, ProjectResponse
from repositories.project_repo import project_repo

router = APIRouter(prefix="/projects", tags=["Projects"])

@router.get("", response_model=List[ProjectResponse])
def get_projects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return project_repo.get_all(db, skip=skip, limit=limit)

@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = project_repo.get(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.post("", response_model=ProjectResponse)
def create_project(project_in: ProjectCreate, db: Session = Depends(get_db)):
    return project_repo.create_with_code(db, project_in)

@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(project_id: int, project_in: ProjectUpdate, db: Session = Depends(get_db)):
    project = project_repo.get(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project_repo.update(db, project, project_in)

@router.delete("/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    project = project_repo.get(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project_repo.soft_delete(db, project_id)
    return {"detail": "Project deleted successfully"}

@router.post("/{project_id}/upload-document")
def upload_project_document(project_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    project = project_repo.get(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
    os.makedirs("uploads/projects", exist_ok=True)
    
    file_extension = os.path.splitext(file.filename)[1]
    safe_filename = f"project_{project_id}_{int(time.time())}{file_extension}"
    file_path = f"uploads/projects/{safe_filename}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Update project
    project.document_path = f"/uploads/projects/{safe_filename}"
    db.commit()
    db.refresh(project)
    
    return {"detail": "Document uploaded successfully", "document_path": project.document_path}
