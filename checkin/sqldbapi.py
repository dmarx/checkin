from sqlalchemy.orm import Session

import models as schemas
import sqlmodels as models

def _create_sqa(db: Session, schema_model, sqa_model):
    db_obj = sqa_model(**schema_model.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def create_checkin(db: Session, checkin: schemas.Checkin):
    return _create_sqa(db, checkin, models.SqaCheckin)

def create_eventtype(db: Session, event_type: schemas.EventType):
    return _create_sqa(db, event_type, models.SqaEventType)
    
def get_root_event_type(db: Session):
    """
    Event types form a tree beneath a common root node. This node is 
    assigned a random unique id, but is identifiable by ~~the absence of a parent_id.~~
    ....node.parent_id = node.id and node.name == '~ROOT~'
    """
    return db.query(models.SqaEventType).filter(models.SqaEventType.id == models.SqaEventType.parent_id).first()

def get_all_event_types(db: Session):
    results = db.query(models.SqaEventType)
    return [schemas.EventType.from_orm(r) for r in results]
    
def get_all_checkins(db: Session):
    results = db.query(models.SqaCheckin)
    return [schemas.Checkin.from_orm(r) for r in results]