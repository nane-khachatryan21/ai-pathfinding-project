from collections import deque
import heapq
import math

class State:
    def get_applicable_actions(self):
        pass

    def get_action_result(self, action):
        pass

    def __eq__(self, other):
        pass

    def __hash__(self):
        pass


class Action:
    def cost(self):
        pass


class GoalTest:
    def is_goal(self, state):
        pass


class Node:
    def __init__(self, parent, action, state):
        self.value = 0
        self.parent = parent
        self.action = action
        self.state = state
        self.depth = parent.depth + 1 if parent else 0
        self.path_cost = parent.path_cost + action.cost() if parent else 0

    def __lt__(self, other):
        return self.value < other.value


class Frontier:
    def add_node(self, node):
        pass

    def clear(self):
        pass

    def __bool__(self):
        pass

    def remove_node(self):
        pass

    def get_maximum_number_of_nodes_on_frontier(self):
        pass


class NodeFunction:
    def eval(self, node):
        pass


class AStarFunction(NodeFunction):
    def __init__(self, heuristic):
        """
        heuristic: either a callable(state) -> float or a mapping state -> float
        """
        self.heuristic = heuristic

    def eval(self, node):
        if callable(self.heuristic):
            h_val = self.heuristic(node.state)
        else:
            h_val = self.heuristic[node.state]
        return node.path_cost + h_val


class UCSFunction(NodeFunction):
    def eval(self, node):
        return node.path_cost


class BestFirstFrontier(Frontier):
    def __init__(self, node_function):
        self._queue = []
        self.node_function = node_function
        self._maximum_number_of_nodes_on_frontier = 0

    def add_node(self, node):
        node.value = self.node_function.eval(node)
        heapq.heappush(self._queue, node)
        if len(self._queue) > self._maximum_number_of_nodes_on_frontier:
            self._maximum_number_of_nodes_on_frontier = len(self._queue)

    def clear(self):
        self._queue.clear()

    def __bool__(self):
        return bool(self._queue)

    def get_maximum_number_of_nodes_on_frontier(self):
        return self._maximum_number_of_nodes_on_frontier

    def remove_node(self):
        return heapq.heappop(self._queue)
    
    def top(self):
        return self._queue[0] if self._queue else None


class AbstractQueueFrontier(Frontier):
    def __init__(self):
        self._queue = deque()
        self._maximum_number_of_nodes_on_frontier = 0

    def add_node(self, node):
        self._queue.append(node)
        if len(self._queue) > self._maximum_number_of_nodes_on_frontier:
            self._maximum_number_of_nodes_on_frontier = len(self._queue)

    def clear(self):
        self._queue.clear()

    def __bool__(self):
        return bool(self._queue)

    def get_maximum_number_of_nodes_on_frontier(self):
        return self._maximum_number_of_nodes_on_frontier


class DepthFirstFrontier(AbstractQueueFrontier):
    def remove_node(self):
        return self._queue.pop()


class BreadthFirstFrontier(AbstractQueueFrontier):
    def remove_node(self):
        return self._queue.popleft()


class Search:
    def find_solution(self, initial_state, goal_test):
        pass

    def get_number_of_nodes_in_last_search(self):
        pass


class TreeSearch(Search):
    def __init__(self, frontier):
        self._frontier = frontier

    def find_solution(self, initial_state, goal_test, callback=None):
        self._number_of_nodes = 1
        self._frontier.clear()
        self._frontier.add_node(Node(None, None, initial_state))
        while self._frontier:
            node = self._frontier.remove_node()
            
            # Callback for node expansion
            if callback:
                frontier_nodes = [n.state.node_id for n in list(self._frontier._queue) if hasattr(n.state, 'node_id')]
                callback(event='node_expanded', node=node, frontier=frontier_nodes, expanded=set())
            
            if goal_test.is_goal(node.state):
                if callback:
                    from graph_search import extract_node_id_path
                    callback(event='goal_found', node=node, frontier=[], expanded=set(), solution_path=extract_node_id_path(node))
                return node
            else:
                for action in node.state.get_applicable_actions():
                    new_state = node.state.get_action_result(action)
                    self._frontier.add_node(Node(node, action, new_state))
                    self._number_of_nodes += 1
        return None

    def get_number_of_nodes_in_last_search(self):
        return self._number_of_nodes


class GraphSearch(Search):
    def __init__(self, frontier):
        self._frontier = frontier

    def find_solution(self, initial_state, goal_test, callback=None):
        self._number_of_nodes = 1
        self._frontier.clear()
        self._frontier.add_node(Node(None, None, initial_state))
        expanded_states = set()
        while self._frontier:
            node = self._frontier.remove_node()
            if node.state in expanded_states:
                continue
            
            # Callback for node expansion
            if callback:
                frontier_nodes = [n.state.node_id for n in list(self._frontier._queue) if hasattr(n.state, 'node_id')]
                callback(event='node_expanded', node=node, frontier=frontier_nodes, expanded=expanded_states)
            
            if goal_test.is_goal(node.state):
                if callback:
                    from graph_search import extract_node_id_path
                    callback(event='goal_found', node=node, frontier=[], expanded=expanded_states, solution_path=extract_node_id_path(node))
                return node
            else:
                expanded_states.add(node.state)
                for action in node.state.get_applicable_actions():
                    new_state = node.state.get_action_result(action)
                    if new_state not in expanded_states:
                        self._frontier.add_node(Node(node, action, new_state))
                        self._number_of_nodes += 1
        return None

    def get_number_of_nodes_in_last_search(self):
        return self._number_of_nodes


class BreadthFirstTreeSearch(Search):
    def __init__(self):
        self._frontier = BreadthFirstFrontier()

    def find_solution(self, initial_state, goal_test, callback=None):
        node = Node(None, None, initial_state)
        self._number_of_nodes = 1
        if goal_test.is_goal(node.state):
            if callback:
                from graph_search import extract_node_id_path
                callback(event='goal_found', node=node, frontier=[], expanded=set(), solution_path=extract_node_id_path(node))
            return node
        self._frontier.clear()
        self._frontier.add_node(node)
        expanded_count = 0
        while self._frontier:
            node = self._frontier.remove_node()
            expanded_count += 1
            
            # Callback for node expansion
            if callback:
                frontier_nodes = [n.state.node_id for n in list(self._frontier._queue) if hasattr(n.state, 'node_id')]
                callback(event='node_expanded', node=node, frontier=frontier_nodes, expanded=set())
            
            for action in node.state.get_applicable_actions():
                new_state = node.state.get_action_result(action)
                child = Node(node, action, new_state)
                if goal_test.is_goal(new_state):
                    if callback:
                        from graph_search import extract_node_id_path
                        callback(event='goal_found', node=child, frontier=[], expanded=set(), solution_path=extract_node_id_path(child))
                    return child
                self._frontier.add_node(child)
                self._number_of_nodes += 1
        return None

    def get_number_of_nodes_in_last_search(self):
        return self._number_of_nodes

    def get_frontier(self):
        return self._frontier


class BreadthFirstGraphSearch(Search):
    def __init__(self):
        self._frontier = BreadthFirstFrontier()

    def find_solution(self, initial_state, goal_test, callback=None):
        node = Node(None, None, initial_state)
        self._number_of_nodes = 1
        if goal_test.is_goal(node.state):
            if callback:
                from graph_search import extract_node_id_path
                callback(event='goal_found', node=node, frontier=[], expanded=set([initial_state]), solution_path=extract_node_id_path(node))
            return node
        self._frontier.clear()
        self._frontier.add_node(node)
        reached_states = set()
        reached_states.add(initial_state)
        while self._frontier:
            node = self._frontier.remove_node()
            
            # Callback for node expansion
            if callback:
                frontier_nodes = [n.state.node_id for n in list(self._frontier._queue) if hasattr(n.state, 'node_id')]
                callback(event='node_expanded', node=node, frontier=frontier_nodes, expanded=reached_states)
            
            for action in node.state.get_applicable_actions():
                new_state = node.state.get_action_result(action)
                child = Node(node, action, new_state)
                if goal_test.is_goal(new_state):
                    if callback:
                        from graph_search import extract_node_id_path
                        callback(event='goal_found', node=child, frontier=[], expanded=reached_states, solution_path=extract_node_id_path(child))
                    return child
                if new_state not in reached_states:
                    reached_states.add(new_state)
                    self._frontier.add_node(child)
                    self._number_of_nodes += 1
        return None

    def get_number_of_nodes_in_last_search(self):
        return self._number_of_nodes

    def get_frontier(self):
        return self._frontier
