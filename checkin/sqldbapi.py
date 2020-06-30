import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import func

import models as schemas
import sqlmodels as models

def _attach_et_interface_mapped_attrs(et_interface: schemas.EtInterface):
    vimap = {'range':'radios', 'number':'number', 'boolean':'checkbox', 'text':'text'}
    if et_interface.input_type is None:
        et_interface.input_type = vimap[et_interface.value_type]
    return et_interface

def _create_sqa(db: Session, schema_model, sqa_model):
    db_obj = sqa_model(**schema_model.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def create_checkin(db: Session, checkin: schemas.Checkin):
    return _create_sqa(db, checkin, models.SqaCheckin)
    
def create_etinterface(db: Session, etinterface: schemas.EtInterface):
    _attach_et_interface_mapped_attrs(et_interface)
    return _create_sqa(db, etinterface, models.SqaEtInterface)

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
    
def get_most_recent_checkins(db: Session):
    results = db.query(models.SqaCheckin, 
         func.max(models.SqaCheckin.timestamp)
        ).group_by(models.SqaCheckin.event_type)
    checkins = [schemas.Checkin.from_orm(r) for r, _ts in results]
    return {str(c.event_type): c for c in checkins }
    
def get_etinterfaces(db: Session):
    results = db.query(models.SqaEtInterface)
    #return [schemas.EtInterface.from_orm(r) for r in results]
    return [schemas.EtInterface(
                event_type_id = r.event_type_id,
                value_type = r.value_type,
                input_type = r.input_type,
                minval = r.minval,
                maxval = r.maxval)
            for r in results]
    
def _merge_sqa(db: Session, schema_model, sqa_model, key='id'):
    #db_obj = sqa_model(**schema_model.dict())
    #db.merge(db_obj)
    #db_obj = db.query(sqa_model).filter(sqa_model.id == schema_model.id).first()
    db_obj = db.query(sqa_model)\
               .filter(
                 getattr(sqa_model, key) == 
                 getattr(schema_model, key))\
               .first()
    if db_obj is None:
        print("[merge_sqa] db_obj does not exist. Creating...")
        return _create_sqa(db=db, schema_model=schema_model, sqa_model=sqa_model)

    print('[merge_sqa] db_obj:', db_obj)
    for k, v in schema_model.dict().items():
        setattr(db_obj, k, v)
    db.commit()
    db.refresh(db_obj)
    return db_obj
    
def update_event_type(db: Session, event_type: schemas.EventType):
    #return create_eventtype(db, event_type) # Returns an integrity error
    return _merge_sqa(db, event_type, models.SqaEventType)
    
def update_event_type_interface(db: Session, et_interface: schemas.EtInterface):
    _attach_et_interface_mapped_attrs(et_interface)
    return _merge_sqa(db, 
                      et_interface, 
                      models.SqaEtInterface, 
                      key='event_type_id')

def get_checkins_df(db: Session):
    columns=['timestamp','value','comments', 'event_type']
    checkins = db.query(models.SqaCheckin)
    records = []
    for c in checkins:
        rec = {col:getattr(c, col) for col in columns}
        rec['event_type'] = c.eventtype.name
        rec['parent'] = c.eventtype.parent.name
        records.append(rec)
    return pd.DataFrame(records)
        