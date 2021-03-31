from datetime import datetime
import uuid
import time # for debugging

from loguru import logger
import networkx as nx
from sqlalchemy.orm import Session
from typing import Optional, List

from fastapi import FastAPI, Response, Request, Depends, status  # , Form
from fastapi.templating import Jinja2Templates
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, HTMLResponse

from checkin.graph_utils import reshape_tree, fetch_event_types_graph
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
                     get_most_recent_interaction, \
                     get_all_event_types
                     
from checkin.random_cute_image import random_cute_image_url


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

@app.post("/checkinmany/")
async def checkin_many(request: Request, checkins: List[Checkin], db: Session = Depends(get_db)):
    for c in checkins:
        logger.debug("Checking in")
        logger.debug(c)
        create_checkin(db, c)
    return True

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
    logger.debug("Registering multiple")
    logger.debug(event_types)
    return [register_event_type(e, db) for e in event_types] # this feels like cheating...
    
@app.put("/eventtype/interface/")
async def update_event_type_interfaces(event_type_interfaces: List[EtInterface], 
                                         db: Session = Depends(get_db)):
    return [update_event_type_interface(db, e) for e in event_type_interfaces]
    
@app.put("/eventtype/")
async def put_event_type(event_type: EventType, db: Session = Depends(get_db)):
    result = update_event_type(db, event_type)
    # To do: response conditional on update success. 
    # Report to user if something went wrong.
    return result
        
@app.get("/mostrecent/")
async def get_most_recent(db: Session = Depends(get_db)):
    return get_most_recent_checkins_propagated_to_ancestors(db)

### This gets used by sunburst-modal.html
@app.get("/plot_data/")
async def get_plot_data(db: Session = Depends(get_db)):
    G = fetch_event_types_graph(db)
    root = get_root_event_type(db)
    return reshape_tree([nx.json_graph.tree_data(G, root=root.id)])[0]
    
### This gets used by sunburst-modal.html
@app.post("/checkin/")
async def post_checkin(checkin: Checkin, db: Session = Depends(get_db)):
    logger.debug("checkin pre:", checkin)
    if not checkin.timestamp:
        checkin.timestamp = datetime.now()
    create_checkin(db, checkin)
    return True

# Doesn't look like this gets used anywhere, but I feel like it's a nice endpoint to have for debugging.
@app.get("/data/")
async def get_data(db: Session = Depends(get_db)):
    return get_all_checkins(db)

############################################

#@app.get("/cute")
#def cute(request: Request):
#    st = time.time()
#    url = random_cute_image_url()
#    et = time.time()
#    logger.debug(f"elapsed: {et-st}")
#    logger.debug(url)
#    return templates.TemplateResponse("nfc_success.html", {
#                                            "request": request, 
#                                            'image_url': url})
                               
#@app.get("/cute/{sub}")
@app.get("/cute")
async def cute4sub(request: Request
                  #,sub: str = None
                  ):
    sub = 'dogswearinghats'
    logger.debug(sub)
    logger.debug(type(sub))
    # WEIRD...
    if sub == 'None':
        sub = None
        logger.debug(type(sub))
    st = time.time()
    url = await random_cute_image_url(sub)
    et = time.time()
    logger.debug(f"elapsed: {et-st}")
    logger.debug(url)
    return templates.TemplateResponse("nfc_success.html", {
                                            "request": request, 
                                            'image_url': url})

@app.get("/nfc-api/")
async def nfc_submit(et_id: str, 
                     request: Request,
                     db: Session = Depends(get_db)
                     ):
    # et_id just needs to match first few characters
    logger.debug(f"[et_id] {et_id}")
    et = None
    for candidate in get_all_event_types(db):
        #logger.debug(f"[candidate] {candidate}")
        idstr = str(candidate.id)
        if idstr.startswith(et_id):
            et = candidate
            break
    if not et:
        return None
    checkin = Checkin(
        timestamp = datetime.now(),
        event_type = et.id,
        value = True
    )
    logger.debug(f"[checkin] {checkin}")
    create_checkin(db, checkin)
    #return checkin
    url = await random_cute_image_url()
    return templates.TemplateResponse("nfc_success.html", {"request": request, 'image_url': url})

############################################

# Exceptions

#@logger.catch
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.debug(exc.errors())
    logger.debug(exc.body)
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
        
