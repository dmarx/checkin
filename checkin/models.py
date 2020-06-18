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
    