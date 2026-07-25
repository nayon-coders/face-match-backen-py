from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from pm_schemas import ClientCreate, ClientUpdate, ClientResponse
from repositories.client_repo import client_repo

router = APIRouter(prefix="/clients", tags=["Clients"])

@router.get("", response_model=List[ClientResponse])
def get_clients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return client_repo.get_all(db, skip=skip, limit=limit)

@router.get("/{client_id}", response_model=ClientResponse)
def get_client(client_id: int, db: Session = Depends(get_db)):
    client = client_repo.get(db, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client

@router.post("", response_model=ClientResponse)
def create_client(client_in: ClientCreate, db: Session = Depends(get_db)):
    # Check email duplicate
    existing = db.query(client_repo.model).filter(client_repo.model.email == client_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    return client_repo.create_with_code(db, client_in)

@router.put("/{client_id}", response_model=ClientResponse)
def update_client(client_id: int, client_in: ClientUpdate, db: Session = Depends(get_db)):
    client = client_repo.get(db, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    if client_in.email != client.email:
        existing = db.query(client_repo.model).filter(client_repo.model.email == client_in.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
            
    return client_repo.update(db, client, client_in)

@router.delete("/{client_id}")
def delete_client(client_id: int, db: Session = Depends(get_db)):
    client = client_repo.get(db, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    client_repo.soft_delete(db, client_id)
    return {"detail": "Client deleted successfully"}
