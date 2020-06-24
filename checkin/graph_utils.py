import networkx as nx
from sqlalchemy.orm import Session
from sqldbapi import get_all_event_types

def build_tree(nodes):
    G = nx.DiGraph()
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