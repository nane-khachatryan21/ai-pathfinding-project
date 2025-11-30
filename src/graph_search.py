# graph_search.py
import math

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


class UCSGraphSearch(Search):
    def __init__(self):
        self._frontier = BestFirstFrontier(UCSFunction())

    def find_solution(self, initial_state, goal_test):
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
                return node

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

    def find_solution(self, initial_state, goal_test, heuristic):
        """
        heuristic: callable taking a state (GraphState) and returning a non-negative estimate
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
                return node

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