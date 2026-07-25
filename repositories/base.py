from typing import TypeVar, Generic, Type, Any
from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")

class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, db: Session, id: Any) -> ModelType:
        return db.query(self.model).filter(self.model.id == id, self.model.deleted_at == None).first()

    def get_all(self, db: Session, skip: int = 0, limit: int = 100):
        return db.query(self.model).filter(self.model.deleted_at == None).order_by(self.model.id.desc()).offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in: CreateSchemaType) -> ModelType:
        obj_data = obj_in.dict()
        db_obj = self.model(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj: ModelType, obj_in: UpdateSchemaType) -> ModelType:
        obj_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            setattr(db_obj, field, obj_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def soft_delete(self, db: Session, id: int):
        from datetime import datetime
        db_obj = db.query(self.model).get(id)
        if db_obj:
            db_obj.deleted_at = datetime.utcnow()
            db.add(db_obj)
            db.commit()
        return db_obj
