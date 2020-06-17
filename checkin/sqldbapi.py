from sqlalchemy.orm import Session

#from . import models

#from .. import models as schemas

#from .models import SqaCheckin, SqaEventType
#from ..schemas import Checkin, EventType

import sqlmodels as models
import models as schemas
#from models import Checkin, EventType

"""
def get_user(db: Session, user_id: int):
    return db.query(models.SqaUser).filter(models.SqaUser.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.SqaUser).filter(models.SqaUser.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = models.SqaUser(email=user.email, hashed_password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
"""

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