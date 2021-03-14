from datetime import datetime
import uuid
import networkx as nx

from fastapi import FastAPI, Response, Request, Depends, status  # , Form
from fastapi.templating import Jinja2Templates
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, HTMLResponse

from sqlalchemy.orm import Session
from typing import Optional, List

from checkin.graph_utils import build_tree, reshape_tree, fetch_event_types_graph
from checkin.models import Checkin, EventType, EtInterface
from checkin.sqldatabase import engine, SessionLocal
from checkin.sqlmodels import SqaCheckin, SqaEventType, SqaEtInterface, Base
from checkin.sqldbapi import create_checkin, create_eventtype, \
                     get_root_event_type, \
                     get_all_checkins, get_most_recent_checkins, \
                     update_event_type, get_etinterfaces, \
                     create_etinterface, update_event_type_interface, \
                     get_checkins_df, \
                     get_most_recent_checkins_propagated_to_ancestors, \
                     get_most_recent_interaction


Base.metadata.create_all(bind=engine)
app = FastAPI()
templates = Jinja2Templates(directory="templates")

from fastapi.middleware.wsgi import WSGIMiddleware
from checkin.dash_app import app_dash

app.mount("/dash", WSGIMiddleware(app_dash.server))

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

###########################################
    
# API

@app.post("/checkin/")
async def post_checkin(checkin: Checkin, db: Session = Depends(get_db)):
    print("checkin pre:", checkin)
    if not checkin.timestamp:
        checkin.timestamp = datetime.now()
    create_checkin(db, checkin)
    return True

@app.post("/checkinmany/")
async def checkin_many(request: Request, checkins: List[Checkin], db: Session = Depends(get_db)):
    for c in checkins:
        print("Checking in")
        print(c)
        create_checkin(db, c)
    return True
    
@app.get("/checkin/")
async def get_checkins(request: Request, db: Session = Depends(get_db)):
    return get_most_recent_checkins(db)

def register_event_type(event_type: EventType, db: Session):
    new_id = uuid.uuid4()
    event_type.id = new_id
    if event_type.parent_id is None:
        root = get_root_event_type(db)
        event_type.parent_id = root.id
    create_eventtype(db, event_type)
    return new_id

@app.post("/eventtype/")
async def register_event_types(event_types: List[EventType], 
                              db: Session = Depends(get_db)):
    print("Registering multiple")
    print(event_types)
    return [register_event_type(e, db) for e in event_types] # this feels like cheating...

@app.post("/eventtype/interface/")
async def register_event_type_interfaces(event_type_interfaces: List[EtInterface], 
                                         db: Session = Depends(get_db)):
    return [create_etinterface(db, e) for e in event_type_interfaces]
    
@app.put("/eventtype/interface/")
async def update_event_type_interfaces(event_type_interfaces: List[EtInterface], 
                                         db: Session = Depends(get_db)):
    return [update_event_type_interface(db, e) for e in event_type_interfaces]

@app.get("/eventtype/")
async def get_event_types(db: Session = Depends(get_db)):
    G = fetch_event_types_graph(db)
    root = get_root_event_type(db)
    return nx.json_graph.tree_data(G, root=root.id)
    
@app.put("/eventtype/")
async def put_event_type(event_type: EventType, db: Session = Depends(get_db)):
    result = update_event_type(db, event_type)
    # To do: response conditional on update success. 
    # Report to user if something went wrong.
    return result
    
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
    
@app.get("/mostrecent/")
async def get_most_recent(db: Session = Depends(get_db)):
    return get_most_recent_checkins_propagated_to_ancestors(db)

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
    

# holding on to this for now... maybe reuse this visual for emotions checkin?        
@app.get("/sunburst")
async def tree(request: Request, db: Session = Depends(get_db)):
    G = fetch_event_types_graph(db)
    root = get_root_event_type(db)
    return templates.TemplateResponse("sunburst-modal.html", {"request": request,
                                      "data_tree": [nx.json_graph.tree_data(G, root=root.id)],
                                      "plot_data": reshape_tree([nx.json_graph.tree_data(G, root=root.id)])
                                      }) 

@app.get("/")
async def listview(request: Request, db: Session = Depends(get_db)):
    G = fetch_event_types_graph(db)
    root = get_root_event_type(db)
    interface_dict = {e.event_type_id:e for e in get_etinterfaces(db)}
    
    depths = nx.shortest_path_length(G, root.id)
    nx.set_node_attributes(G, depths, 'depth')
    most_recent_interaction = get_most_recent_interaction(db)
    
    return templates.TemplateResponse("event_types_tree.html", {"request": request,
                                      "data_tree": [nx.json_graph.tree_data(G, root=root.id)],
                                      "plot_data": reshape_tree([nx.json_graph.tree_data(G, root=root.id)]),
                                      "et_interfaces": interface_dict,
                                      "most_recent_interaction": jsonable_encoder(most_recent_interaction)
                                      })
                                      
#@app.get("/table/", response_class=HTMLResponse)
@app.get("/table/")
async def checkins_table(request: Request, db: Session = Depends(get_db)):
    table = get_checkins_df(db).to_html(index=False)
    return templates.TemplateResponse("table.html", 
        {'request': request, 'table':table})
        
