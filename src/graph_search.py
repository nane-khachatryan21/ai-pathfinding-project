# graph_search.py
import math
import heapq

from search import (
    State,
    Action,
    GoalTest,
    Search,
    Node,
    BestFirstFrontier,
    UCSFunction,
    AStarFunction,
)


# Helper to get full path from any goal Node
def extract_node_id_path(goal_node):
    path = []
    node = goal_node
    while node is not None:
        path.append(node.state.node_id)
        node = node.parent
    path.reverse()
    return path


class GraphState(State):
    def __init__(self, graph, node_id):
        self.graph = graph
        self.node_id = node_id

    def get_applicable_actions(self):
        actions = []
        for neighbor in self.graph.neighbors(self.node_id):
            edge_data = self.graph.get_edge_data(self.node_id, neighbor)
            for key in edge_data:
                # edge length is in meters in osmnx road networks
                actions.append(GraphAction(neighbor, edge_data[key]["length"]))
        return actions

    def get_action_result(self, action):
        return GraphState(self.graph, action.target_node)

    def __eq__(self, other):
        return isinstance(other, GraphState) and self.node_id == other.node_id

    def __hash__(self):
        return hash(self.node_id)

    def __repr__(self):
        return f"State({self.node_id})"


class GraphAction(Action):
    def __init__(self, target_node, cost_value):
        self.target_node = target_node
        self._cost = cost_value

    def cost(self):
        return self._cost

    def __repr__(self):
        return f"→{self.target_node} (cost={self._cost})"


class SimpleGoalTest(GoalTest):
    def __init__(self, goal_node):
        self.goal_node = goal_node

    def is_goal(self, state):
        return state.node_id == self.goal_node
    
    def get_goal_node(self):
        return self.goal_node


class UCSGraphSearch(Search):
    def __init__(self):
        self._frontier = BestFirstFrontier(UCSFunction())

    def find_solution(self, initial_state, goal_test, callback=None):
        self._number_of_nodes = 1
        self._frontier.clear()
        start_node = Node(None, None, initial_state)
        self._frontier.add_node(start_node)
        reached_states = {initial_state: 0}  # state → best known cost g

        while self._frontier:
            node = self._frontier.remove_node()

            # Skip if this path is worse than already found
            if node.path_cost > reached_states.get(node.state, float("inf")):
                continue

            if goal_test.is_goal(node.state):
                if callback:
                    callback(event='goal_found', node=node, frontier=list(self._frontier._queue), 
                            expanded=set(reached_states.keys()), solution_path=extract_node_id_path(node))
                return node

            # Invoke callback on node expansion
            if callback:
                frontier_nodes = [n.state.node_id for n in self._frontier._queue]
                callback(event='node_expanded', node=node, frontier=frontier_nodes, 
                        expanded=set(reached_states.keys()))

            for action in node.state.get_applicable_actions():
                new_state = node.state.get_action_result(action)
                new_cost = node.path_cost + action.cost()

                if new_cost < reached_states.get(new_state, float("inf")):
                    reached_states[new_state] = new_cost
                    child = Node(node, action, new_state)
                    self._frontier.add_node(child)
                    self._number_of_nodes += 1
        return None

    def get_number_of_nodes_in_last_search(self):
        return self._number_of_nodes

    def get_frontier(self):
        return self._frontier


class AStarGraphSearch(Search):
    def __init__(self):
        # frontier is created once we know the heuristic
        self._frontier = None
        self._expanded_node_count = 0

    def find_solution(self, initial_state, goal_test, heuristic, callback=None):
        """
        heuristic: callable taking a state (GraphState) and returning a non-negative estimate
        callback: optional function to call on each node expansion
        """
        self._expanded_node_count = 0

        # Create a BestFirstFrontier that uses f(n) = g(n) + h(n)
        self._frontier = BestFirstFrontier(AStarFunction(heuristic))
        self._frontier.clear()

        start_node = Node(None, None, initial_state)
        self._frontier.add_node(start_node)

        # Best known g-cost per state
        best_g = {initial_state: 0.0}

        while self._frontier:
            node = self._frontier.remove_node()

            # If this node has a worse g than what we already have, skip it
            if node.path_cost > best_g.get(node.state, float("inf")):
                continue

            self._expanded_node_count += 1

            if goal_test.is_goal(node.state):
                if callback:
                    callback(event='goal_found', node=node, frontier=list(self._frontier._queue),
                            expanded=set(best_g.keys()), solution_path=extract_node_id_path(node))
                return node

            # Invoke callback on node expansion
            if callback:
                frontier_nodes = [n.state.node_id for n in self._frontier._queue]
                callback(event='node_expanded', node=node, frontier=frontier_nodes,
                        expanded=set(best_g.keys()))

            for action in node.state.get_applicable_actions():
                new_state = node.state.get_action_result(action)
                new_g = node.path_cost + action.cost()  # g(child)

                # If this is a better path to new_state, record it and push child
                if new_g < best_g.get(new_state, float("inf")):
                    best_g[new_state] = new_g
                    child = Node(node, action, new_state)
                    self._frontier.add_node(child)

        return None

    def get_expanded_node_count(self):
        return self._expanded_node_count

    def get_frontier(self):
        return self._frontier





def haversine(lat1, lon1, lat2, lon2):
    R = 6371000.0
    # Convert degrees to radians
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = (math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2)
    c = 2*math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c
    

def build_euclidean_heuristic(graph, goal_node_id):
    """
    Returns a heuristic function h(state) that estimates
    straight-line distance (in meters) from `state` to the goal node.

    `graph` is an osmnx/NetworkX graph with 'x' (lon) and 'y' (lat) on nodes.
    `goal_node_id` is the node id of the goal.
    """
    goal_data = graph.nodes[goal_node_id]
    goal_lat = goal_data["y"]
    goal_lon = goal_data["x"]

    # Earth radius in meters
    R = 6371000.0
    def haversine(lat1, lon1, lat2, lon2):
        # Convert degrees to radians
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)

        a = (math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2)
        c = 2*math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    def h(state):
        node_data = graph.nodes[state.node_id]
        lat = node_data["y"]
        lon = node_data["x"]
        # Straight-line lower bound to goal
        return haversine(lat, lon, goal_lat, goal_lon)

    return h


class BidirectionalGraphSearch(Search):

    def __init__(self):
        self._forward_frontier = None
        self._backward_frontier = None
        self._expanded_node_count = 0

    def _reconstruct_bidirectional_path(self, fwd_meeting_node, bwd_meeting_node):
        fwd_path = []
        node = fwd_meeting_node
        while node:
            fwd_path.append(node.state.node_id)
            node = node.parent

        bwd_path = []
        node = bwd_meeting_node
        while node:
            bwd_path.append(node.state.node_id)
            node = node.parent

        return fwd_path[::-1] + bwd_path[1:]
    
    def _build_node_chain(self, graph, path_ids):
        """
        Given a list of node ids [n0, n1, ..., nk] on the forward graph, build a linked chain of Node objects and return the goal Node.
        """
        # Root node
        start_id = path_ids[0]
        start_state = GraphState(graph, start_id)
        current_node = Node(parent=None, action=None, state=start_state)

        # Walk along the path, create actions and nodes
        for i in range(1, len(path_ids)):
            prev_id = path_ids[i - 1]
            curr_id = path_ids[i]

            # Look up an edge from prev_id to curr_id in the forward graph
            edge_data = graph.get_edge_data(prev_id, curr_id)
            if edge_data is None:
                # Shouldn't happen if path is valid, but be defensive
                raise ValueError(f"No edge from {prev_id} to {curr_id} in graph")

            # Pick one edge key and use its length as cost
            first_key = next(iter(edge_data.keys()))
            cost_value = edge_data[first_key]["length"]

            next_state = GraphState(graph, curr_id)
            next_action = GraphAction(curr_id, cost_value)

            current_node = Node(parent=current_node, action=next_action, state=next_state)

        # current_node is the goal Node
        return current_node


    def find_solution(self, initial_state, goal_test, callback=None):
        self._expanded_node_count = 0
        goal_node_id = goal_test.get_goal_node()

        # Original graph and reversed graph
        G = initial_state.graph
        
        # For undirected graphs (MultiGraph), no need to reverse
        # For directed graphs, reverse it
        if G.is_directed():
            G_rev = G.reverse(copy=True)
        else:
            G_rev = G  # Use same graph for undirected

        # States at the roots of the two searches
        start_state = initial_state
        goal_state = GraphState(G_rev, goal_node_id)

        start_node = Node(None, None, start_state)
        goal_node = Node(None, None, goal_state)

        # Frontiers (UCS on both sides)
        self._forward_frontier = BestFirstFrontier(UCSFunction())
        self._backward_frontier = BestFirstFrontier(UCSFunction())
        self._forward_frontier.clear()
        self._backward_frontier.clear()
        self._forward_frontier.add_node(start_node)
        self._backward_frontier.add_node(goal_node)

        # Best known g-cost per state from each side
        fwd_reached = {start_state: 0}
        bwd_reached = {goal_state: 0}

        # Map states to the best node representing them (for reconstruction)
        fwd_nodes = {start_state: start_node}
        bwd_nodes = {goal_state: goal_node}

        # Best total cost found so far and meeting nodes
        C_best = math.inf
        fwd_meeting_node = None
        bwd_meeting_node = None

        # Main loop
        while self._forward_frontier or self._backward_frontier:

            # Get minimal g on each frontier
            g_min_fwd = math.inf
            if self._forward_frontier:
                top_fwd = self._forward_frontier.top()
                g_min_fwd = top_fwd.path_cost

            g_min_bwd = math.inf
            if self._backward_frontier:
                top_bwd = self._backward_frontier.top()
                g_min_bwd = top_bwd.path_cost

            # If no better path can be found, terminate
            if min(g_min_fwd, g_min_bwd) >= C_best:
                break

            # Choose direction to expand
            if g_min_fwd <= g_min_bwd and self._forward_frontier:
                current = self._forward_frontier.remove_node()
                direction = "forward"
                # Skip outdated node
                if current.path_cost > fwd_reached.get(current.state, math.inf):
                    continue
            else:
                current = self._backward_frontier.remove_node()
                direction = "backward"
                # Skip outdated node
                if current.path_cost > bwd_reached.get(current.state, math.inf):
                    continue

            self._expanded_node_count += 1
            
            # Invoke callback on node expansion
            if callback:
                if direction == "forward":
                    frontier_nodes = [n.state.node_id for n in self._forward_frontier._queue]
                    callback(event='node_expanded', node=current, frontier=frontier_nodes,
                            expanded=set(fwd_reached.keys()))
                else:
                    frontier_nodes = [n.state.node_id for n in self._backward_frontier._queue]
                    callback(event='node_expanded', node=current, frontier=frontier_nodes,
                            expanded=set(bwd_reached.keys()))

            if direction == "forward":
                for action in current.state.get_applicable_actions():
                    child_state = current.state.get_action_result(action)
                    new_g = current.path_cost + action.cost()

                    if new_g < fwd_reached.get(child_state, math.inf):
                        fwd_reached[child_state] = new_g
                        child_node = Node(current, action, child_state)
                        self._forward_frontier.add_node(child_node)
                        fwd_nodes[child_state] = child_node

                        # Check for meeting with backward search
                        if child_state in bwd_reached:
                            total_cost = new_g + bwd_reached[child_state]
                            if total_cost < C_best:
                                C_best = total_cost
                                fwd_meeting_node = child_node
                                bwd_meeting_node = bwd_nodes[child_state]

            else:  # direction == "backward"
                for action in current.state.get_applicable_actions():
                    child_state = current.state.get_action_result(action)
                    new_g = current.path_cost + action.cost()

                    if new_g < bwd_reached.get(child_state, math.inf):
                        bwd_reached[child_state] = new_g
                        child_node = Node(current, action, child_state)
                        self._backward_frontier.add_node(child_node)
                        bwd_nodes[child_state] = child_node

                        # Check for meeting with forward search
                        if child_state in fwd_reached:
                            total_cost = new_g + fwd_reached[child_state]
                            if total_cost < C_best:
                                C_best = total_cost
                                bwd_meeting_node = child_node
                                fwd_meeting_node = fwd_nodes[child_state]

        # No path found
        if C_best == math.inf or fwd_meeting_node is None or bwd_meeting_node is None:
            return None

        # Reconstruct path as a list of node_ids
        final_path_node_sequence = self._reconstruct_bidirectional_path(fwd_meeting_node, bwd_meeting_node)
        goal_node = self._build_node_chain(G, final_path_node_sequence)
        
        # Invoke callback for goal found
        if callback:
            callback(event='goal_found', node=goal_node, 
                    frontier=[], 
                    expanded=set(fwd_reached.keys()) | set(bwd_reached.keys()),
                    solution_path=final_path_node_sequence)
        
        return goal_node
    
    def get_expanded_node_count(self):
        return self._expanded_node_count
    
    
def haversine(lat1, lon1, lat2, lon2):
    R = 6371000.0
    # Convert degrees to radians
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = (math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2)
    c = 2*math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


import networkx as nx
from collections import deque

from collections import deque

class EdgeCostChanger:
    """
    Simple edge-cost changer for D* Lite.
    Currently needs manuall setup
    Further finalization needed
    """

    def __init__(self, G, node=None, time_to_block=1000, radius=2, factor=10.0, weight_key="length"):
        self.G = G
        self.node_to_block = node
        self.time_to_block = time_to_block
        self.radius = radius
        self.factor = factor
        self.weight_key = weight_key

        self._t = 0
        self._already_changed = False   # so we only change once, for now

    def change_state(self, mode="manual"):
        self._t += 1
        if self._t < self.time_to_block:
            return []

        changed_edges = self._inflate_edge_costs()
        self._already_changed = True
        return changed_edges

    def _inflate_edge_costs(self):
        G = self.G
        node = self.node_to_block
        radius = self.radius
        factor = self.factor
        weight_key = self.weight_key


        visited = {node}
        queue = deque([(node, 0)])

        while queue:
            node, dist = queue.popleft()
            if dist >= radius:
                continue
            for nbr in G.neighbors(node):
                if nbr not in visited:
                    visited.add(nbr)
                    queue.append((nbr, dist + 1))

        nodes_within_radius = visited


        changed_edges = set()
        for u, v, k, d in G.edges(keys=True, data=True):
            if u in nodes_within_radius or v in nodes_within_radius:
                if weight_key in d:
                    d[weight_key] *= factor
                    changed_edges.add((u, v))

        return list(changed_edges)



class DStarNode:
    def __init__(self, node_id):
        self.id = node_id
        self.g = float("inf")
        self.rhs = float("inf")
        self.key = (float("inf"), float("inf"))
        self.succ = set()
        self.pred = set()

    # def __lt__(self, other):
    #     return self.key < other.key


class DStarPriorityQueue:
    def __init__(self):
        self.heap = []
        self.entry_finder = {}  # node_id → key

    def insert(self, node):
        self.entry_finder[node.id] = node.key
        heapq.heappush(self.heap, (node.key, node.id, node))

    def pop(self):
        while self.heap:
            key, _, node = heapq.heappop(self.heap)
            if self.entry_finder.get(node.id) == key: #careful 
                del self.entry_finder[node.id]
                return node
        return None  # empty

    # def top_key(self):
    #     if not self.heap:
    #         return (float("inf"), float("inf"))
    #     return self.heap[0][0]

    def top_key(self):
        while self.heap:
            key, node_id, node = self.heap[0]
            if self.entry_finder.get(node_id) == key:
                return key
            heapq.heappop(self.heap)  # discard stale entry
        return (float("inf"), float("inf"))
    
    def remove(self, node):
        if node.id in self.entry_finder:
            del self.entry_finder[node.id]
    
    def contains(self, node):
        return node.id in self.entry_finder


class DStarLiteSearch(Search):
    """
    D* Lite implementation that can adapt to edge cost changes.
    This is a wrapper that makes it compatible with the standard Search interface.
    """
    def __init__(self):
        self._expanded_node_count = 0
    
    def find_solution(self, initial_state, goal_test, callback=None):
        """
        Adapter method to make D* Lite compatible with the standard search interface.
        For visualization purposes, we'll run D* Lite without dynamic edge changes.
        """
        graph = initial_state.graph
        start_id = initial_state.node_id
        goal_id = goal_test.get_goal_node()
        
        # Create a no-op edge cost changer (no changes during search)
        edge_changer = EdgeCostChanger(graph, node=None, time_to_block=float('inf'))
        
        # Create the actual D* Lite searcher
        dstar = _DStarLiteCore(graph, start_id, goal_id, edge_changer, callback=callback)
        
        try:
            # Run the search
            path, _ = dstar.main()
            self._expanded_node_count = dstar.expansion_count
            
            if not path or len(path) == 0:
                return None
            
            # Build a Node chain for compatibility
            return dstar.build_solution_node()
        except Exception as e:
            print(f"D* Lite search error: {e}")
            return None
    
    def get_expanded_node_count(self):
        return self._expanded_node_count


class _DStarLiteCore:
    """Internal D* Lite implementation."""
    def __init__(self, G, start_id, goal_id, edge_cost_changer: EdgeCostChanger, callback=None):
        
        self.graph = G
        self.callback = callback
        self.expansion_count = 0
        self.callback_throttle_count = 0
        self.callback_throttle_interval = 10  # Only emit callback every N expansions

        self.edge_scheduler = edge_cost_changer
        self.nodes = {}
        for node_id in self.graph.nodes:
            node = DStarNode(node_id)
            # For undirected graphs (MultiGraph), use neighbors for both successors and predecessors
            # For directed graphs, use successors() and predecessors()
            if self.graph.is_directed():
                node.succ = set(self.graph.successors(node_id))
                node.pred = set(self.graph.predecessors(node_id))
            else:
                # For undirected graphs, neighbors serve as both successors and predecessors
                neighbors = set(self.graph.neighbors(node_id))
                node.succ = neighbors
                node.pred = neighbors
            self.nodes[node_id] = node

        self.start:DStarNode = self.nodes[start_id]
        self.goal:DStarNode = self.nodes[goal_id]
        self.last = self.start
        self.initial_start_id = start_id

        self.heuristic = self._dstar_h
        # procedure Initialize
        self.U = DStarPriorityQueue()
        self.km = 0
        self.goal.rhs = 0
        self.goal.key = self.calculate_key(self.goal)
        self.U.insert(self.goal)
        self.path_cost = 0
        self.full_path = []
        self.expanded_nodes = set()  # Track for efficient callback

    
    def build_solution_node(self):
        """Build a Node chain from the found path for compatibility."""
        if not self.full_path:
            return None
        
        # Build linked Node structure
        current_node = Node(None, None, GraphState(self.graph, self.full_path[0]))
        
        for i in range(1, len(self.full_path)):
            prev_id = self.full_path[i-1]
            curr_id = self.full_path[i]
            
            edge_data = self.graph.get_edge_data(prev_id, curr_id)
            if edge_data:
                key = next(iter(edge_data.keys()))
                cost = edge_data[key]["length"]
            else:
                cost = 0
            
            next_state = GraphState(self.graph, curr_id)
            next_action = GraphAction(curr_id, cost)
            current_node = Node(current_node, next_action, next_state)
        
        return current_node
        
    def _cost(self, u: DStarNode, v_id):
        edge_data = self.graph.get_edge_data(u.id, v_id)
        if not edge_data:
            return float("inf")
        key = next(iter(edge_data.keys()))
        return edge_data[key]["length"]
    
    def _dstar_h(self, u: DStarNode, v: DStarNode):
        data_u = self.graph.nodes[u.id]
        data_v = self.graph.nodes[v.id]

        lat1, lon1 = data_u["y"], data_u["x"]
        lat2, lon2 = data_v["y"], data_v["x"]

        return haversine(lat1, lon1, lat2, lon2)

    def calculate_key(self, u: DStarNode):
        val = min(u.g, u.rhs)
        return (val + self.heuristic(u, self.start) + self.km, val)

    def update_vertex(self, u: DStarNode):
        if u.id != self.goal.id:
            min_val = float("inf")
            for succ in u.succ:
                value = self._cost(u, succ) + self.nodes[succ].g
                if value < min_val:
                    min_val = value
            u.rhs = min_val

        if self.U.contains(u):
            self.U.remove(u)    

        if u.g != u.rhs:
            u.key = self.calculate_key(u)
            self.U.insert(u)
        
    def compute_shortest_path(self):
        while self.U.top_key() < self.calculate_key(self.start) or self.start.rhs != self.start.g:

            u = self.U.pop()
            if not u:
                return
            
            self.expansion_count += 1
            self.expanded_nodes.add(u.id)
            
            # Throttled callback for visualization - only emit every N expansions
            if self.callback and self.expansion_count % self.callback_throttle_interval == 0:
                # Use pre-tracked set instead of computing it each time
                frontier_list = [node.id for _, _, node in self.U.heap[:100]]  # Limit to first 100 for performance
                
                dummy_node = Node(None, None, GraphState(self.graph, u.id))
                dummy_node.path_cost = u.g
                dummy_node.depth = len(self.full_path)
                
                self.callback(
                    event='node_expanded',
                    node=dummy_node,
                    frontier=frontier_list,
                    expanded=self.expanded_nodes
                )
            
            k_old = u.key
            k_new = self.calculate_key(u)
            if not u:
                return
            if k_old < k_new:
                u.key = k_new
                self.U.insert(u)

            elif u.g > u.rhs:
                u.g = u.rhs
                for pred in u.pred:
                    self.update_vertex(self.nodes[pred])
            else:
                u.g = float("inf")
                for pred in u.pred:
                    self.update_vertex(self.nodes[pred])
                self.update_vertex(u)
    

    def main(self):
        self.compute_shortest_path()
        path = [self.initial_start_id]  # Include start node in path

        while self.start.id != self.goal.id:
            if self.start.g == float("inf"):
                print('D* Lite: path does not exist')
                return [], []

            self._make_move()
            path.append(self.start.id)

            changed_edges = self.edge_scheduler.change_state()
            if changed_edges:
                self.km = self.km + self.heuristic(self.last, self.start)
                self.last = self.start

                for (u_id, v_id) in changed_edges:  
                    u = self.nodes[v_id]
                    self.update_vertex(u)
                self.compute_shortest_path()
        
        self.full_path = path
        print(f'D* Lite Path Cost: {self.path_cost:.2f}m')
        
        # Callback for goal found
        if self.callback and len(path) > 0:
            dummy_node = Node(None, None, GraphState(self.graph, self.goal.id))
            dummy_node.path_cost = self.path_cost
            dummy_node.depth = len(path) - 1
            
            # Use tracked expanded nodes instead of recomputing
            self.callback(
                event='goal_found',
                node=dummy_node,
                frontier=[],
                expanded=self.expanded_nodes,
                solution_path=path
            )
        
        return path, []

    def _make_move(self):
        best = None
        best_val = float("inf")
        for s_id in self.start.succ:
            cost_val = self._cost(self.start, s_id) + self.nodes[s_id].g
            if cost_val < best_val:
                best_val = cost_val
                best = self.nodes[s_id]
        
        if best is None:
            return
        
        self.path_cost += self._cost(self.start, best.id)
        self.start = best

        return 
        
        