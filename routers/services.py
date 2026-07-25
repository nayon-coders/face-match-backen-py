from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from pm_schemas import ServiceCreate, ServiceUpdate, ServiceResponse
from repositories.service_repo import service_repo

router = APIRouter(prefix="/services", tags=["Services"])

@router.get("", response_model=List[ServiceResponse])
def get_services(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return service_repo.get_all(db, skip=skip, limit=limit)

@router.get("/{service_id}", response_model=ServiceResponse)
def get_service(service_id: int, db: Session = Depends(get_db)):
    service = service_repo.get(db, service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service

@router.post("", response_model=ServiceResponse)
def create_service(service_in: ServiceCreate, db: Session = Depends(get_db)):
    return service_repo.create_with_code(db, service_in)

@router.put("/{service_id}", response_model=ServiceResponse)
def update_service(service_id: int, service_in: ServiceUpdate, db: Session = Depends(get_db)):
    service = service_repo.get(db, service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service_repo.update(db, service, service_in)

@router.delete("/{service_id}")
def delete_service(service_id: int, db: Session = Depends(get_db)):
    service = service_repo.get(db, service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    service_repo.soft_delete(db, service_id)
    return {"detail": "Service deleted successfully"}
