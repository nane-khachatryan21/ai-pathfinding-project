from search import (
    State,
    Action,
    GoalTest,
    Search,
    Node,
    BestFirstFrontier,
    UCSFunction,
)


class GraphState(State):
    def __init__(self, graph, node_id):
        self.graph = graph
        self.node_id = node_id

    def get_applicable_actions(self):
        actions = []
        for neighbor in self.graph.neighbors(self.node_id):
            # Pick one representative edge (or use first edge key)
            edge_data = self.graph.get_edge_data(self.node_id, neighbor)
            for key in edge_data:
                actions.append(GraphAction(neighbor, edge_data[key]["length"])) #edge_data[key]["cost"]
        return actions

    def get_action_result(self, action):
        # Next state is simply the neighbor node
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
        # Use BestFirstFrontier with UCSFunction (f = g)
        self._frontier = BestFirstFrontier(UCSFunction())

    def find_solution(self, initial_state, goal_test):
        self._number_of_nodes = 1
        self._frontier.clear()
        start_node = Node(None, None, initial_state)
        self._frontier.add_node(start_node)
        reached_states = {initial_state: 0}  # state → best known cost

        while self._frontier:
            node = self._frontier.remove_node()

            # Skip if this path is worse than already found
            if node.path_cost > reached_states.get(node.state, float("inf")):
                continue

            if goal_test.is_goal(node.state):
                return node

            # Expand neighbors
            for action in node.state.get_applicable_actions():
                new_state = node.state.get_action_result(action)
                new_cost = node.path_cost + action.cost()

                # Add or improve state
                if new_state not in reached_states or new_cost < reached_states[new_state]:
                    reached_states[new_state] = new_cost
                    child = Node(node, action, new_state)
                    self._frontier.add_node(child)
                    self._number_of_nodes += 1
        return None

    def get_number_of_nodes_in_last_search(self):
        return self._number_of_nodes

    def get_frontier(self):
        return self._frontier
