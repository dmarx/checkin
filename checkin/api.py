from collections import defaultdict
from datetime import datetime
import uuid
import shelve
import networkx as nx

from fastapi import FastAPI, Response, Request, Depends, status  # , Form
from fastapi.templating import Jinja2Templates
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
#from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import Optional

from models import Checkin, EventType
from sqldatabase import engine, SessionLocal
from sqlmodels import SqaCheckin, SqaEventType, Base
from sqldbapi import create_checkin, create_eventtype, \
                     get_root_event_type, get_all_event_types, \
                     get_all_checkins

Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_path = "checkin_data.shelf"

app = FastAPI()

templates = Jinja2Templates(directory="templates")

###########################################

def build_tree(nodes):
    G = nx.DiGraph()
    #G.add_node('0')
    edges = []
    for n in nodes:
        G.add_node(n.id, obj=n)
        if not n.parent_id == n.id:
            edges.append((n.parent_id, n.id))
    G.add_edges_from(edges)
    return G

def reshape_tree(tree):
    outv = []
    for node in tree:
        has_children = False
        item = {'id': node['id'],
                'is_checkinable': False}
        if 'children' in node:
            item['children'] = reshape_tree(node['children'])
            has_children = True
        if 'obj' in node:
            item['parent_id'] = node['obj'].parent_id
            item['name'] = node['obj'].name
            item['is_checkinable'] = node['obj'].is_checkinable
        item['value'] = 1*(not has_children)
        outv.append(item)
    return outv
    
def fetch_event_types_graph(db: Session):
    event_types = get_all_event_types(db)
    return  build_tree(event_types)
    
###########################################
    
# API

@app.post("/checkin/")
async def post_checkin(checkin: Checkin, db_sqa: Session = Depends(get_db)):
    print("checkin pre:", checkin)
    if not checkin.timestamp:
        checkin.timestamp = datetime.now()
    create_checkin(db_sqa, checkin)
    return True
    
@app.post("/eventtype/")
async def register_event_type(event_type: EventType, 
                              db: Session = Depends(get_db)):
    new_id = uuid.uuid4()
    event_type.id = new_id
    if event_type.parent_id is None:
        root = get_root_event_type(db)
        event_type.parent_id = root.id
    create_eventtype(db, event_type)
    return new_id

@app.get("/eventtype/")
async def get_event_types(db: Session = Depends(get_db)):
    G = fetch_event_types_graph(db)
    root = get_root_event_type(db)
    return nx.json_graph.tree_data(G, root=root.id)
    
@app.get("/eventtype/{eventtype_id}", response_model=EventType)
async def get_event_type(eventtype_id: uuid.UUID):
    G = fetch_event_types_graph(db)
    return G.nodes(data=True)[eventtype_id]['obj']
    
@app.get("/data/")
async def get_data(db: Session = Depends(get_db)):
    return get_all_checkins(db)
    
@app.get("/plot_data/")
async def get_plot_data(db: Session = Depends(get_db)):
    G = fetch_event_types_graph(db)
    root = get_root_event_type(db)
    return reshape_tree([nx.json_graph.tree_data(G, root=root.id)])[0]
    
############################################

# Exceptions

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print(exc.errors())
    print(exc.body)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )
    
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
async def tree(request: Request, db: Session = Depends(get_db)):
    #return templates.TemplateResponse("event_types_tree.html", {"request": request,
    G = fetch_event_types_graph(db)
    root = get_root_event_type(db)
    return templates.TemplateResponse("sunburst-modal.html", {"request": request,
                                      "data_tree": [nx.json_graph.tree_data(G, root=root.id)],
                                      "plot_data": reshape_tree([nx.json_graph.tree_data(G, root=root.id)])
                                      }) 
                                      # can I call get_event_types here?

@app.get("/checkin/{name}/{event_type_id}")
async def checkin(request: Request, event_type_id:uuid.UUID ):
    # In the URL pattern, {name} can be literally anything. Just using this
    # pattern for user readability. Not necessary at all. Just need the event_type_id
    G = fetch_event_types_graph(db)
    tree = [nx.json_graph.tree_data(G, root=event_type_id)]
    event_type = tree[0]['obj']
    return templates.TemplateResponse("checkin.html", {"request": request, 
                                      "tree": tree, "event_type": event_type})
                                      