from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from collections import defaultdict
import uuid
import networkx as nx

app = FastAPI()

###########################################

# temporary, hyper-simple datamodel
DATA = []
#EVENT_TYPE_TAXONOMY = defaultdict(list)
#EVENT_TYPES = defaultdict(dict) # {eventtypeid:EventType}

G = nx.DiGraph()
G.add_node('0')

###########################################

class Checkin(BaseModel):
    timestamp: Optional[datetime]
    #event_type: str
    event_type: uuid.UUID
    value: Optional[int]
    comments: Optional[str]
      
    
class EventType(BaseModel):
    id: Optional[uuid.UUID]
    name: str
    is_checkinable: bool = True
    parent_id: Optional[uuid.UUID] = '0'
    

###########################################
    
#def unique_id():
#    return uuid.uuid4().hex

@app.post("/checkin/")
async def post_checkin(checkin: Checkin):
    if not checkin.timestamp:
        checkin.timestamp = datetime.now()
    DATA.append(checkin)
    return True
    
@app.post("/eventtype/")
async def register_event_type(event_type: EventType):
    new_id = uuid.uuid4()
    event_type.id = new_id
    #EVENT_TYPES[new_id] = event_type
    G.add_node(new_id, obj=event_type)
    #if event_type.parent_id is not None:
    #    G.add_edge(event_type.parent_id, new_id)
    #else:
    #    G.add_edge('0', new_id)
    G.add_edge(event_type.parent_id, new_id)
    return new_id

@app.get("/eventtype/")
async def get_event_types():
    #return EVENT_TYPES, EVENT_TYPE_TAXONOMY
    #eturn G
    return nx.json_graph.tree_data(G, root='0')
    
@app.get("/eventtype/{eventtype_id}", response_model=EventType)
async def get_event_type(eventtype_id: uuid.UUID):
    #return EVENT_TYPES[eventtype_id]
    return G.nodes(data=True)[eventtype_id]['obj']
    
@app.get("/data/")
async def get_data():
    return DATA