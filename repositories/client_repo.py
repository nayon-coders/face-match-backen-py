from sqlalchemy.orm import Session
from .base import BaseRepository
from pm_models import Client
from pm_schemas import ClientCreate, ClientUpdate
import uuid

class ClientRepository(BaseRepository[Client, ClientCreate, ClientUpdate]):
    def create_with_code(self, db: Session, obj_in: ClientCreate) -> Client:
        obj_data = obj_in.dict()
        # Auto generate client code
        obj_data["client_code"] = f"CLI-{str(uuid.uuid4())[:8].upper()}"
        
        db_obj = self.model(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

client_repo = ClientRepository(Client)
