from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship

#from .database import Base
from sqldatabase import Base
from sqlalchemy_utils import UUIDType
   
class SqaCheckin(Base):
    __tablename__ = "checkins"
    
    id = Column(Integer, primary_key=True)
    #timestamp = Column(Integer)
    timestamp = Column(DateTime)
    #event_type = Column(String, ForeignKey("eventtypes.id"))
    event_type = Column(UUIDType(binary=False), ForeignKey("eventtypes.id"))
    value = Column(Integer)
    comments = Column(String)


class SqaEventType(Base):
    __tablename__ = "eventtypes"
    
    #id = Column(String, primary_key=True)
    id = Column(UUIDType(binary=False), primary_key=True)
    name = Column(String)
    is_checkinable = Column(Boolean, default=True)
    #parent_id = Column(Integer, default='0')
    #parent_id = Column(String, ForeignKey("eventtypes.id"))
    parent_id = Column(UUIDType(binary=False), ForeignKey("eventtypes.id"))

"""
class SqaUser(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    #is_active = Column(Boolean, default=True)
    #items = relationship("Item", back_populates="owner")
    #checkins = relationship("Checkin", backpopulates="user")
"""