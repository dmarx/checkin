from collections import defaultdict
from datetime import datetime
import uuid
import shelve
import networkx as nx

from fastapi import FastAPI, Response, Request, Form
from fastapi.templating import Jinja2Templates
from typing import Optional

from models import Checkin, EventType

from fastapi.staticfiles import StaticFiles

db_path = "checkin_data.shelf"

app = FastAPI()

# Jesus.... this piece here is a mess for some reason. Screw url_for(),
# it's uglier, but I'll just put the json directly in the template. Yeesh.
##app.mount("/static", StaticFiles(directory="static", check_dir=True), name="static")

templates = Jinja2Templates(directory="templates")

###########################################

    
###########################################

# temporary, hyper-simple datamodel
DATA = []

G = nx.DiGraph()
G.add_node('0')

with shelve.open(db_path) as db:
    if 'DATA' in db:
        DATA = db['DATA']
    if 'G' in db:
        G = db['G']
        
###########################################
    
# API

@app.post("/checkin/")
async def post_checkin(checkin: Checkin):
    if not checkin.timestamp:
        checkin.timestamp = datetime.now()
    with shelve.open(db_path, writeback=True) as db:
        db['DATA'].append(checkin)
        global DATA
        DATA = db['DATA']
    return True
    
@app.post("/eventtype/")
async def register_event_type(event_type: EventType):
    new_id = uuid.uuid4()
    event_type.id = new_id
    with shelve.open(db_path, writeback=True) as db:
        global G
        G = db['G']
        G.add_node(new_id, obj=event_type)
        G.add_edge(event_type.parent_id, new_id)
    return new_id

@app.get("/eventtype/")
async def get_event_types():
    return nx.json_graph.tree_data(G, root='0')
    
@app.get("/eventtype/{eventtype_id}", response_model=EventType)
async def get_event_type(eventtype_id: uuid.UUID):
    return G.nodes(data=True)[eventtype_id]['obj']
    
@app.get("/data/")
async def get_data():
    return DATA
    
############################################

# pages
    
@app.get("/")
async def homepage(request: Request):
    return templates.TemplateResponse("register_event_type.html", {"request": request})
    
@app.get("/test")
async def test(request: Request):
    return templates.TemplateResponse("register_event_type3.html", {"request": request, 
                                      "vars_dict":{"name":"str", "parent_id":"str"}})
        
@app.get("/tree")
async def tree(request: Request):
    #return templates.TemplateResponse("event_types_tree.html", {"request": request,
    #return templates.TemplateResponse("sunburst.html", {"request": request,
    return templates.TemplateResponse("sunburst-modal.html", {"request": request,
                                      "data_tree": [nx.json_graph.tree_data(G, root='0')]}) 
                                      # can I call get_event_types here?

@app.get("/checkin/{name}/{event_type_id}")
async def checkin(request: Request, event_type_id:uuid.UUID ):
    # In the URL pattern, {name} can be literally anything. Just using this
    # pattern for user readability. Not necessary at all. Just need the event_type_id
    tree = [nx.json_graph.tree_data(G, root=event_type_id)]
    event_type = tree[0]['obj']
    return templates.TemplateResponse("checkin.html", {"request": request, 
                                      "tree": tree, "event_type": event_type})
                                      