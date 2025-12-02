# registry.py
"""
Dynamic registry system for search algorithms and heuristics.
This allows the frontend to discover available algorithms and heuristics without hardcoding.
"""

from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass
import inspect


@dataclass
class AlgorithmMetadata:
    """Metadata about a search algorithm."""
    name: str
    display_name: str
    description: str
    requires_heuristic: bool
    algorithm_class: type


@dataclass
class HeuristicMetadata:
    """Metadata about a heuristic function."""
    name: str
    display_name: str
    description: str
    builder_function: Callable


class AlgorithmRegistry:
    """Registry for search algorithms."""
    
    def __init__(self):
        self._algorithms: Dict[str, AlgorithmMetadata] = {}
    
    def register(self, name: str, display_name: str, description: str, 
                 requires_heuristic: bool, algorithm_class: type):
        """Register a search algorithm."""
        self._algorithms[name] = AlgorithmMetadata(
            name=name,
            display_name=display_name,
            description=description,
            requires_heuristic=requires_heuristic,
            algorithm_class=algorithm_class
        )
    
    def get(self, name: str) -> Optional[AlgorithmMetadata]:
        """Get algorithm metadata by name."""
        return self._algorithms.get(name)
    
    def list_all(self) -> List[AlgorithmMetadata]:
        """List all registered algorithms."""
        return list(self._algorithms.values())
    
    def list_names(self) -> List[str]:
        """List all registered algorithm names."""
        return list(self._algorithms.keys())
    
    def create_instance(self, name: str) -> Any:
        """Create an instance of the algorithm."""
        metadata = self.get(name)
        if metadata is None:
            raise ValueError(f"Algorithm '{name}' not found in registry")
        return metadata.algorithm_class()


class HeuristicRegistry:
    """Registry for heuristic functions."""
    
    def __init__(self):
        self._heuristics: Dict[str, HeuristicMetadata] = {}
    
    def register(self, name: str, display_name: str, description: str, 
                 builder_function: Callable):
        """Register a heuristic builder function."""
        self._heuristics[name] = HeuristicMetadata(
            name=name,
            display_name=display_name,
            description=description,
            builder_function=builder_function
        )
    
    def get(self, name: str) -> Optional[HeuristicMetadata]:
        """Get heuristic metadata by name."""
        return self._heuristics.get(name)
    
    def list_all(self) -> List[HeuristicMetadata]:
        """List all registered heuristics."""
        return list(self._heuristics.values())
    
    def list_names(self) -> List[str]:
        """List all registered heuristic names."""
        return list(self._heuristics.keys())
    
    def build_heuristic(self, name: str, graph: Any, goal_node_id: Any) -> Callable:
        """Build a heuristic function for the given graph and goal."""
        metadata = self.get(name)
        if metadata is None:
            raise ValueError(f"Heuristic '{name}' not found in registry")
        return metadata.builder_function(graph, goal_node_id)


# Global registries
algorithm_registry = AlgorithmRegistry()
heuristic_registry = HeuristicRegistry()


def initialize_registries():
    """Initialize registries with available algorithms and heuristics."""
    from graph_search import (
        UCSGraphSearch,
        AStarGraphSearch,
        BidirectionalGraphSearch,
        build_euclidean_heuristic
    )
    from search import (
        BreadthFirstGraphSearch,
        BreadthFirstTreeSearch,
        GraphSearch,
        TreeSearch,
        BreadthFirstFrontier,
        DepthFirstFrontier
    )
    
    # Register algorithms
    algorithm_registry.register(
        name="ucs",
        display_name="Uniform Cost Search (UCS)",
        description="Finds the optimal path by exploring nodes in order of path cost",
        requires_heuristic=False,
        algorithm_class=UCSGraphSearch
    )
    
    algorithm_registry.register(
        name="astar",
        display_name="A* Search",
        description="Informed search using path cost + heuristic estimate",
        requires_heuristic=True,
        algorithm_class=AStarGraphSearch
    )
    
    algorithm_registry.register(
        name="bidirectional",
        display_name="Bidirectional Search",
        description="Searches from both start and goal simultaneously",
        requires_heuristic=False,
        algorithm_class=BidirectionalGraphSearch
    )
    
    algorithm_registry.register(
        name="bfs_graph",
        display_name="Breadth-First Search (Graph)",
        description="Explores nodes level by level, avoids revisiting",
        requires_heuristic=False,
        algorithm_class=BreadthFirstGraphSearch
    )
    
    algorithm_registry.register(
        name="bfs_tree",
        display_name="Breadth-First Search (Tree)",
        description="Explores nodes level by level, may revisit",
        requires_heuristic=False,
        algorithm_class=BreadthFirstTreeSearch
    )
    
    # Create DFS Graph and Tree Search instances
    class DFSGraphSearch(GraphSearch):
        def __init__(self):
            super().__init__(DepthFirstFrontier())
    
    class DFSTreeSearch(TreeSearch):
        def __init__(self):
            super().__init__(DepthFirstFrontier())
    
    algorithm_registry.register(
        name="dfs_graph",
        display_name="Depth-First Search (Graph)",
        description="Explores as deep as possible before backtracking, avoids revisiting",
        requires_heuristic=False,
        algorithm_class=DFSGraphSearch
    )
    
    algorithm_registry.register(
        name="dfs_tree",
        display_name="Depth-First Search (Tree)",
        description="Explores as deep as possible before backtracking, may revisit",
        requires_heuristic=False,
        algorithm_class=DFSTreeSearch
    )
    
    # Register heuristics
    heuristic_registry.register(
        name="euclidean",
        display_name="Euclidean Distance (Haversine)",
        description="Straight-line distance on Earth's surface",
        builder_function=build_euclidean_heuristic
    )
    
    # You can add more heuristics here in the future
    # For example:
    # heuristic_registry.register(
    #     name="zero",
    #     display_name="Zero Heuristic",
    #     description="Always returns 0 (reduces A* to UCS)",
    #     builder_function=lambda graph, goal: lambda state: 0
    # )


# Initialize registries on module import
initialize_registries()

