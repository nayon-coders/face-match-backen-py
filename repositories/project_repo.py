from sqlalchemy.orm import Session
from typing import Any, Dict, Union
from .base import BaseRepository
from pm_models import Project, ProjectService, Service
from pm_schemas import ProjectCreate, ProjectUpdate
import uuid
import re

class ProjectRepository(BaseRepository[Project, ProjectCreate, ProjectUpdate]):
    def create_with_code(self, db: Session, obj_in: ProjectCreate) -> Project:
        obj_data = obj_in.dict(exclude={"service_ids"})
        service_ids = obj_in.service_ids
        
        # Auto generate code
        obj_data["project_code"] = f"PRJ-{str(uuid.uuid4())[:8].upper()}"
        
        # Auto generate slug
        base_slug = re.sub(r'[^a-zA-Z0-9]+', '-', obj_data["project_title"].lower()).strip('-')
        obj_data["slug"] = f"{base_slug}-{str(uuid.uuid4())[:4]}"
        
        # Calculate services budget
        services_budget = 0.0
        services_to_link = []
        if service_ids:
            services = db.query(Service).filter(Service.id.in_(service_ids)).all()
            for svc in services:
                services_budget += svc.default_price
                services_to_link.append(ProjectService(
                    service_id=svc.id,
                    unit_price=svc.default_price,
                    total=svc.default_price,
                    quantity=1.0
                ))
        
        # Calculate final budget = base budget + services budget
        base_budget = obj_data.get("budget", 0.0)
        obj_data["final_budget"] = base_budget + services_budget
        
        db_obj = self.model(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        # Link services to project
        for p_svc in services_to_link:
            p_svc.project_id = db_obj.id
            db.add(p_svc)
        
        if services_to_link:
            db.commit()
            db.refresh(db_obj)
            
        return db_obj

    def update(
        self, db: Session, db_obj: Project, obj_in: Union[ProjectUpdate, Dict[str, Any]]
    ) -> Project:
        obj_data = obj_in if isinstance(obj_in, dict) else obj_in.dict(exclude_unset=True)
        
        service_ids = obj_data.pop("service_ids", None)
        
        if service_ids is not None:
            # Delete old services
            db.query(ProjectService).filter(ProjectService.project_id == db_obj.id).delete()
            
            # Add new services
            services_budget = 0.0
            if service_ids:
                services = db.query(Service).filter(Service.id.in_(service_ids)).all()
                for svc in services:
                    services_budget += svc.default_price
                    db.add(ProjectService(
                        project_id=db_obj.id,
                        service_id=svc.id,
                        unit_price=svc.default_price,
                        total=svc.default_price,
                        quantity=1.0
                    ))
            
            base_budget = obj_data.get("budget", db_obj.budget)
            obj_data["final_budget"] = base_budget + services_budget

        for field in obj_data:
            if hasattr(db_obj, field):
                setattr(db_obj, field, obj_data[field])

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

project_repo = ProjectRepository(Project)
