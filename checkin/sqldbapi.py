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