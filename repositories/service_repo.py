from sqlalchemy.orm import Session
from .base import BaseRepository
from pm_models import Service
from pm_schemas import ServiceCreate, ServiceUpdate
import uuid

class ServiceRepository(BaseRepository[Service, ServiceCreate, ServiceUpdate]):
    def create_with_code(self, db: Session, obj_in: ServiceCreate) -> Service:
        obj_data = obj_in.dict()
        obj_data["service_code"] = f"SRV-{str(uuid.uuid4())[:8].upper()}"
        
        db_obj = self.model(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

service_repo = ServiceRepository(Service)
