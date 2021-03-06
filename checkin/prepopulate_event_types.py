from models import EventType
import uuid
import shelve
import networkx as nx

from sqldatabase import engine, SessionLocal
from sqlmodels import SqaCheckin, SqaEventType, Base
from sqldbapi import create_checkin, create_eventtype

Base.metadata.create_all(bind=engine)

sqadb = SessionLocal()

spec = {'Activities of Daily Living': {
    'Chores': ['Vacuuming', 'Dishes', 'Laundry', 'Trash', 'Cooked'],
    'Hygiene': ['Brushed Teeth', 'Showered', 'Changed Clothes', 'Medications',
                'Toenails', 'Beard', 'Pubic Hair'],
    'Meals': ['Breakfast', 'Lunch', 'Dinner', 'Snacking']},
 'Skills': {'Mindfulness Skills': ['Observe/Describe', 'One Mindfully'],
            'Emotion Regulation Skills': ['Accumulate Positive Emotions',
                                          'Build Mastery', 'Opposite Action',
                                          'Check The Facts'],
            'Distress Tolerance Skills': ['Radical Acceptance',
                                          'IMPROVE (Distract)', 'STOP', 
                                          'Paired Muscle Relaxation', 'TIPP'],
            'Interpersonal Effectiveness Skills': ['DEAR MAN', 'GIVE', 'FAST',
                                          'Clarified Goals',
                                          'Build/Attend Relationships'],
            'ACT Skills': ['Defusions', 'Expansion', 
                           'Contact With Present Moment', 'Self as Context']},
 'Emotions': ['Sadness', 'Depression', 'Guilt', 'Shame', 'Anger',
                 'Frustration', 'Fear', 'Anxiety', 'Joy',
                 'Accomplishment'],
 'Sensuality': ['PIV', 'Cuddling awake', 'Cuddling to sleep', 'I initiate'],
 'Frame of Mind': ['Fixed Mind', 'Fatalistic Mind', 'Flexible Mind'],
 'Target Behaviors':['Rumination', 'Perfectionism', 'Avoidance/Procrastination',
                    'Negative Self Talk', 'Substance Use', 'Isolation',
                    'Suicidal Ideation']}

# create a root node id
ROOT_ID = uuid.uuid4()
event_type = EventType(name="~ROOT~")
event_type.id = ROOT_ID
event_type.parent_id = ROOT_ID # it's either this or null. for validation, would prefer it be a non-nullable attribute
create_eventtype(sqadb, event_type)

G = nx.DiGraph()
#G.add_node('0')
G.add_node(ROOT_ID)

# This is definitely not the most efficient way to do this. Don't care.
# build graph from spec
name2id = {}

for ename in spec.keys():
    event_type = EventType(name=ename)
    new_id = uuid.uuid4()
    event_type.id = new_id
    #event_type.parent_id = '0' # type error, sqlalchemy wants a CHAR(16) (i.e. a UUID)
    event_type.parent_id = ROOT_ID
    create_eventtype(sqadb, event_type)
    G.add_node(new_id, obj=event_type)
    G.add_edge(event_type.parent_id, new_id)
    name2id[ename] = new_id
    
for k, v in spec.items():
    parent_id = name2id[k]
    is_checkinable = True
    if isinstance(v, dict):
        is_checkinable = False
    for child_name in v:
        new_id = uuid.uuid4()
        event_type = EventType(name=child_name,
                               parent_id=parent_id,
                               is_checkinable=is_checkinable,
                               id = new_id)
        create_eventtype(sqadb, event_type)
        G.add_node(new_id, obj=event_type)
        G.add_edge(event_type.parent_id, event_type.id)
        name2id[event_type.name] = event_type.id
        
        if not is_checkinable:
            w = v[child_name]
            is_checkinable2 = True
            if isinstance(w, dict):
                print("NOT DONE YET")
                is_checkinable2 = False
                print(w)
            for child_name2 in w:
                new_id2 = uuid.uuid4()
                event_type2 = EventType(name=child_name2,
                                       parent_id=event_type.id,
                                       is_checkinable=is_checkinable2,
                                       id = new_id2)
                create_eventtype(sqadb, event_type2)
                G.add_node(new_id2, obj=event_type2)
                G.add_edge(event_type2.parent_id, event_type2.id)
                name2id[event_type2.name] = event_type2.id
        
#nx.json_graph.tree_data(G, root='0')

db_path = "checkin_data.shelf"
with shelve.open(db_path) as db:
    db['G'] = G