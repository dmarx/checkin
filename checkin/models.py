from datetime import datetime
from pydantic import BaseModel
from typing import Optional
import uuid


class Checkin(BaseModel):
    timestamp: datetime
    event_type: uuid.UUID
    value: Optional[int]
    comments: Optional[str]
    
    class Config:
        orm_mode = True

    
class EventType(BaseModel):
    id: Optional[uuid.UUID]
    name: str
    is_checkinable: bool = True
    parent_id: Optional[uuid.UUID] = None #'0'
    
    class Config:
        orm_mode = True


class EtInterface (BaseModel):
	event_type_id: uuid.UUID
	value_type: str # [range, number, boolean, text]
	input_type: str # [radios, text, checkbox, number] # redundant w/ value_type
	minval: Optional[int]
	maxval: Optional[int]
    
    #class Config:
    #    orm_mode = True
