import os
import osmnx as ox
import networkx as nx
from graph_search import *
import networkx as nx

# ----- Build toy MultiGraph -----
PLACE = "Kentron, Yerevan, Armenia"   # small; fast for smoke tests
NETWORK = "drive"

# ---------- download (simplify=True by default here) ----------
G = ox.graph.graph_from_place(PLACE, network_type=NETWORK, simplify=True)

# keep only the largest connected component (weak is fine for roads)
G = ox.truncate.largest_component(G, strongly=False)

start_node_id = list(G.nodes)[0]
goal_node_id = list(G.nodes)[564]
dlit = DStarSearch(G, start_node_id, goal_node_id)
path = dlit.main()
print(list(path[0]))