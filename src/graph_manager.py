"""
Manager for loading and serving multiple graph options.
Handles caching and simplification of graphs for efficient transfer.
"""

import pickle
import os
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass
import json
import networkx as nx


@dataclass
class GraphMetadata:
    """Metadata about a graph."""
    graph_id: str
    name: str
    description: str
    node_count: int
    edge_count: int
    bbox: Dict[str, float]  # {min_lat, max_lat, min_lon, max_lon}


class GraphManager:
    """Manages multiple graph options for pathfinding visualization."""
    
    def __init__(self, graphs_dir: str = None):
        """
        Initialize graph manager.
        
        Args:
            graphs_dir: Directory containing graph pickle files
        """
        if graphs_dir is None:
            graphs_dir = os.path.join(os.path.dirname(__file__), 'graphs')
        self.graphs_dir = graphs_dir
        self._graphs: Dict[str, Any] = {}
        self._metadata: Dict[str, GraphMetadata] = {}
        
    def register_graph(self, graph_id: str, name: str, description: str, graph_file: str):
        """Register a graph option."""
        graph_path = os.path.join(self.graphs_dir, graph_file)
        if not os.path.exists(graph_path):
            print(f"Warning: Graph file {graph_path} not found")
            return
        
        # Load graph
        with open(graph_path, 'rb') as f:
            graph = pickle.load(f)
        
        # Calculate metadata
        node_count = graph.number_of_nodes()
        edge_count = graph.number_of_edges()
        
        # Calculate bounding box
        lats = [data['y'] for _, data in graph.nodes(data=True)]
        lons = [data['x'] for _, data in graph.nodes(data=True)]
        bbox = {
            'min_lat': min(lats),
            'max_lat': max(lats),
            'min_lon': min(lons),
            'max_lon': max(lons)
        }
        
        # Store graph and metadata
        self._graphs[graph_id] = graph
        self._metadata[graph_id] = GraphMetadata(
            graph_id=graph_id,
            name=name,
            description=description,
            node_count=node_count,
            edge_count=edge_count,
            bbox=bbox
        )
        
        print(f"Registered graph: {name} ({node_count} nodes, {edge_count} edges)")
    
    def get_graph(self, graph_id: str) -> Optional[Any]:
        """Get a graph by ID."""
        return self._graphs.get(graph_id)
    
    def get_metadata(self, graph_id: str) -> Optional[GraphMetadata]:
        """Get metadata for a graph."""
        return self._metadata.get(graph_id)
    
    def list_graphs(self) -> List[Dict[str, Any]]:
        """List all available graphs with their metadata."""
        return [
            {
                'graph_id': meta.graph_id,
                'name': meta.name,
                'description': meta.description,
                'node_count': meta.node_count,
                'edge_count': meta.edge_count,
                'bbox': meta.bbox
            }
            for meta in self._metadata.values()
        ]
    
    def serialize_graph(self, graph_id: str, simplify: bool = True) -> Optional[Dict[str, Any]]:
        """
        Serialize a graph to JSON-friendly format.
        
        Args:
            graph_id: ID of the graph to serialize
            simplify: If True, simplify node/edge data for smaller payload
        
        Returns:
            Dictionary with 'nodes' and 'edges' lists
        """
        graph = self.get_graph(graph_id)
        metadata = self.get_metadata(graph_id)
        
        if graph is None or metadata is None:
            return None
        
        # Serialize nodes
        nodes = []
        for node_id, data in graph.nodes(data=True):
            node_data = {
                'id': str(node_id),  # Convert to string for JSON compatibility
                'lat': data['y'],
                'lon': data['x']
            }
            nodes.append(node_data)
        
        # Serialize edges
        edges = []
        seen_edges = set()  # To handle MultiGraph duplicate edges
        for u, v, key, data in graph.edges(keys=True, data=True):
            edge_key = (min(u, v), max(u, v))  # Normalize edge direction
            if edge_key not in seen_edges:
                seen_edges.add(edge_key)
                edge_data = {
                    'source': str(u),
                    'target': str(v),
                    'length': data.get('length_m', data.get('length', 0))
                }
                edges.append(edge_data)
        
        return {
            'graph_id': graph_id,
            'metadata': {
                'name': metadata.name,
                'description': metadata.description,
                'node_count': metadata.node_count,
                'edge_count': metadata.edge_count,
                'bbox': metadata.bbox
            },
            'nodes': nodes,
            'edges': edges
        }
    
    def find_node(self, graph_id: str, node_str: str) -> Optional[Any]:
        """
        Find a node in the graph, handling type conversions.
        
        Args:
            graph_id: ID of the graph
            node_str: Node ID as string
            
        Returns:
            The actual node ID in the graph, or None if not found
        """
        graph = self.get_graph(graph_id)
        if graph is None:
            return None
        
        graph_nodes = list(graph.nodes())
        
        # Try direct match first (already correct type)
        if node_str in graph_nodes:
            return node_str
        
        # Try converting to int (common for OSMnx graphs)
        try:
            node_int = int(node_str)
            if node_int in graph_nodes:
                return node_int
        except (ValueError, TypeError):
            pass
        
        # For city-level graphs, try case-insensitive string match
        node_str_lower = str(node_str).lower()
        for node in graph_nodes:
            if str(node).lower() == node_str_lower:
                return node
        
        return None
    
    def validate_node(self, graph_id: str, node_id: str) -> Optional[Dict[str, Any]]:
        """
        Validate if a node exists in the graph and return its details.
        
        Args:
            graph_id: ID of the graph
            node_id: Node ID to validate
            
        Returns:
            Dictionary with node details if valid, None otherwise
        """
        graph = self.get_graph(graph_id)
        if graph is None:
            return None
        
        actual_node = self.find_node(graph_id, node_id)
        if actual_node is None:
            return None
        
        # Get node data
        node_data = graph.nodes[actual_node]
        
        return {
            'valid': True,
            'node_id': str(actual_node),
            'lat': node_data.get('y'),
            'lon': node_data.get('x'),
            'label': str(actual_node)
        }
    
    def check_reachability(self, graph_id: str, start_node: str, goal_node: str) -> Dict[str, Any]:
        """
        Check if two nodes are reachable from each other.
        
        Args:
            graph_id: ID of the graph
            start_node: Start node ID
            goal_node: Goal node ID
            
        Returns:
            Dictionary with reachability information
        """
        graph = self.get_graph(graph_id)
        if graph is None:
            return {'reachable': False, 'error': 'Graph not found'}
        
        # Find actual nodes
        actual_start = self.find_node(graph_id, start_node)
        actual_goal = self.find_node(graph_id, goal_node)
        
        if actual_start is None:
            return {'reachable': False, 'error': f'Start node "{start_node}" not found in graph'}
        
        if actual_goal is None:
            return {'reachable': False, 'error': f'Goal node "{goal_node}" not found in graph'}
        
        # Check if nodes are in the same connected component
        try:
            # For directed graphs, check weak connectivity
            if graph.is_directed():
                # Convert to undirected for connectivity check
                undirected = graph.to_undirected()
                reachable = nx.has_path(undirected, actual_start, actual_goal)
            else:
                reachable = nx.has_path(graph, actual_start, actual_goal)
            
            if reachable:
                return {
                    'reachable': True,
                    'start_node': str(actual_start),
                    'goal_node': str(actual_goal)
                }
            else:
                return {
                    'reachable': False,
                    'error': 'Nodes are not connected in the graph',
                    'start_node': str(actual_start),
                    'goal_node': str(actual_goal)
                }
        except Exception as e:
            return {
                'reachable': False,
                'error': f'Error checking reachability: {str(e)}'
            }
    
    def get_node_ids_set(self, graph_id: str) -> Optional[Set]:
        """
        Get a set of all node IDs in the graph for quick lookup.
        
        Args:
            graph_id: ID of the graph
            
        Returns:
            Set of node IDs or None if graph not found
        """
        graph = self.get_graph(graph_id)
        if graph is None:
            return None
        
        return set(graph.nodes())


# Global graph manager instance
graph_manager = GraphManager()


def initialize_graphs():
    """Initialize and register all available graphs."""
    # Check if graphs directory exists
    graphs_dir = graph_manager.graphs_dir
    if not os.path.exists(graphs_dir):
        os.makedirs(graphs_dir)
        print(f"Created graphs directory: {graphs_dir}")
        print("Please run prepare_graphs.py to generate graph files.")
        return
    
    # Register available graphs
    graph_files = {
        'armenia_cities': 'armenia_cities.pkl',
        'armenia_full': 'armenia_cities_villages.pkl',
        'yerevan': 'yerevan.pkl'
    }
    
    for graph_id, filename in graph_files.items():
        filepath = os.path.join(graphs_dir, filename)
        if os.path.exists(filepath):
            if graph_id == 'armenia_cities':
                graph_manager.register_graph(
                    graph_id='armenia_cities',
                    name='Armenia Cities',
                    description='Road network connecting major cities in Armenia',
                    graph_file=filename
                )
            elif graph_id == 'armenia_full':
                graph_manager.register_graph(
                    graph_id='armenia_full',
                    name='Armenia Cities & Villages',
                    description='Extended road network including cities and villages',
                    graph_file=filename
                )
            elif graph_id == 'yerevan':
                graph_manager.register_graph(
                    graph_id='yerevan',
                    name='Yerevan',
                    description='Complete road network of Yerevan city',
                    graph_file=filename
                )
        else:
            print(f"Graph file not found: {filepath}")


# Initialize graphs on module import
initialize_graphs()

