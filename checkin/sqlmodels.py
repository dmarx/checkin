from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy_utils import UUIDType

from sqldatabase import Base

   
class SqaCheckin(Base):
    __tablename__ = "checkins"
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime)
    event_type = Column(UUIDType(binary=False), ForeignKey("eventtypes.id"))
    value = Column(Integer)
    comments = Column(String)
    
    # should change `event_type` above to `event_type_id`
    eventtype = relationship("SqaEventType", back_populates="checkins")


class SqaEventType(Base):
    __tablename__ = "eventtypes"
    
    id = Column(UUIDType(binary=False), primary_key=True)
    name = Column(String)
    is_checkinable = Column(Boolean, default=True)
    parent_id = Column(UUIDType(binary=False), ForeignKey("eventtypes.id"))
    
    checkins = relationship("SqaCheckin", back_populates="eventtype")


class SqaEtInterface(Base):
    __tablename__ = "etinterfaces"
    event_type_id = Column(UUIDType(binary=False), ForeignKey("eventtypes.id"), primary_key=True)
    value_type = Column(String)
    input_type = Column(String)
    minval = Column(Integer)
    maxval = Column(Integer)
