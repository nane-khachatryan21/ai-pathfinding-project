#!/usr/bin/env python3
"""
Flask API server for pathfinding visualization.

Provides endpoints for:
- Listing and retrieving graph data
- Listing algorithms and heuristics
- Running search algorithms with step-by-step visualization
"""

import sys
import os
from flask import Flask, jsonify, request, Response
from flask_cors import CORS
import json
import uuid
import time
from threading import Thread, Lock
from typing import Dict, Any, List, Optional

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from graph_manager import graph_manager
from registry import algorithm_registry, heuristic_registry
from graph_search import GraphState, SimpleGoalTest


app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Store active search sessions
search_sessions: Dict[str, Dict[str, Any]] = {}
sessions_lock = Lock()


@app.route('/api/graphs', methods=['GET'])
def list_graphs():
    """List all available graphs with metadata."""
    try:
        graphs = graph_manager.list_graphs()
        return jsonify({
            'success': True,
            'graphs': graphs
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/graph/<graph_id>', methods=['GET'])
def get_graph(graph_id):
    """Get serialized graph data for visualization."""
    try:
        graph_data = graph_manager.serialize_graph(graph_id, simplify=True)
        
        if graph_data is None:
            return jsonify({
                'success': False,
                'error': f'Graph {graph_id} not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': graph_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/graph/<graph_id>/validate_node/<node_id>', methods=['GET'])
def validate_node(graph_id, node_id):
    """Validate if a node exists in the graph."""
    try:
        result = graph_manager.validate_node(graph_id, node_id)
        
        if result is None:
            return jsonify({
                'success': False,
                'valid': False,
                'error': f'Node "{node_id}" not found in graph'
            }), 404
        
        return jsonify({
            'success': True,
            **result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'valid': False,
            'error': str(e)
        }), 500


@app.route('/api/graph/<graph_id>/check_reachability', methods=['POST'])
def check_reachability(graph_id):
    """Check if two nodes are reachable from each other."""
    try:
        data = request.get_json()
        
        if 'start_node' not in data or 'goal_node' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing start_node or goal_node'
            }), 400
        
        result = graph_manager.check_reachability(
            graph_id, 
            data['start_node'], 
            data['goal_node']
        )
        
        if 'error' in result:
            return jsonify({
                'success': False,
                **result
            }), 400
        
        return jsonify({
            'success': True,
            **result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/algorithms', methods=['GET'])
def list_algorithms():
    """List all available search algorithms."""
    try:
        algorithms = []
        for meta in algorithm_registry.list_all():
            algorithms.append({
                'name': meta.name,
                'display_name': meta.display_name,
                'description': meta.description,
                'requires_heuristic': meta.requires_heuristic
            })
        
        return jsonify({
            'success': True,
            'algorithms': algorithms
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/heuristics', methods=['GET'])
def list_heuristics():
    """List all available heuristics."""
    try:
        heuristics = []
        for meta in heuristic_registry.list_all():
            heuristics.append({
                'name': meta.name,
                'display_name': meta.display_name,
                'description': meta.description
            })
        
        return jsonify({
            'success': True,
            'heuristics': heuristics
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/search', methods=['POST'])
def start_search():
    """
    Start a new search.
    
    Expected JSON body:
    {
        "graph_id": "armenia_cities",
        "algorithm": "astar",
        "heuristic": "euclidean",  # optional, required for informed search
        "start_node": "node_id",
        "goal_node": "node_id"
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['graph_id', 'algorithm', 'start_node', 'goal_node']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        graph_id = data['graph_id']
        algorithm_name = data['algorithm']
        heuristic_name = data.get('heuristic')
        start_node = data['start_node']
        goal_node = data['goal_node']
        
        # Get graph
        graph = graph_manager.get_graph(graph_id)
        if graph is None:
            return jsonify({
                'success': False,
                'error': f'Graph {graph_id} not found'
            }), 404
        
        # Use improved find_node from graph_manager
        start_node_id = graph_manager.find_node(graph_id, start_node)
        goal_node_id = graph_manager.find_node(graph_id, goal_node)
        
        if start_node_id is None:
            return jsonify({
                'success': False,
                'error': f'Start node {start_node} not found in graph'
            }), 404
        
        if goal_node_id is None:
            return jsonify({
                'success': False,
                'error': f'Goal node {goal_node} not found in graph'
            }), 404
        
        # Get algorithm
        algo_meta = algorithm_registry.get(algorithm_name)
        if algo_meta is None:
            return jsonify({
                'success': False,
                'error': f'Algorithm {algorithm_name} not found'
            }), 404
        
        # Check if heuristic is needed
        if algo_meta.requires_heuristic and not heuristic_name:
            return jsonify({
                'success': False,
                'error': f'Algorithm {algorithm_name} requires a heuristic'
            }), 400
        
        # Create session
        session_id = str(uuid.uuid4())
        
        # Initialize session data
        with sessions_lock:
            search_sessions[session_id] = {
                'status': 'running',
                'steps': [],
                'completed': False,
                'error': None,
                'start_time': time.time(),
                'graph_id': graph_id,
                'algorithm': algorithm_name,
                'start_node': str(start_node_id),
                'goal_node': str(goal_node_id)
            }
        
        # Start search in background thread
        thread = Thread(
            target=run_search,
            args=(session_id, graph, algo_meta, start_node_id, goal_node_id, 
                  heuristic_name, graph_id)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'session_id': session_id
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def run_search(session_id, graph, algo_meta, start_node_id, goal_node_id, 
               heuristic_name, graph_id):
    """Run search algorithm in background thread."""
    try:
        # Create initial state and goal test
        initial_state = GraphState(graph, start_node_id)
        goal_test = SimpleGoalTest(goal_node_id)
        
        # Create algorithm instance
        algorithm = algorithm_registry.create_instance(algo_meta.name)
        
        # Create callback to capture steps
        def callback(event, node, frontier, expanded, **kwargs):
            step_data = {
                'event': event,
                'current_node': str(node.state.node_id) if hasattr(node.state, 'node_id') else None,
                'frontier': [str(n) for n in frontier] if isinstance(frontier, list) else [],
                'expanded': [str(s.node_id) for s in expanded if hasattr(s, 'node_id')],
                'path_cost': node.path_cost,
                'depth': node.depth
            }
            
            if event == 'goal_found':
                step_data['solution_path'] = kwargs.get('solution_path', [])
                step_data['solution_path'] = [str(n) for n in step_data['solution_path']]
            
            with sessions_lock:
                if session_id in search_sessions:
                    search_sessions[session_id]['steps'].append(step_data)
        
        # Run search based on algorithm type
        if algo_meta.requires_heuristic:
            # Build heuristic
            heuristic = heuristic_registry.build_heuristic(
                heuristic_name, graph, goal_node_id
            )
            solution = algorithm.find_solution(initial_state, goal_test, heuristic, callback)
        else:
            solution = algorithm.find_solution(initial_state, goal_test, callback)
        
        # Update session with results
        with sessions_lock:
            if session_id in search_sessions:
                search_sessions[session_id]['status'] = 'completed'
                search_sessions[session_id]['completed'] = True
                search_sessions[session_id]['solution_found'] = solution is not None
                search_sessions[session_id]['end_time'] = time.time()
                
                if solution:
                    from graph_search import extract_node_id_path
                    path = extract_node_id_path(solution)
                    search_sessions[session_id]['solution_path'] = [str(n) for n in path]
                    search_sessions[session_id]['solution_cost'] = solution.path_cost
                
    except Exception as e:
        with sessions_lock:
            if session_id in search_sessions:
                search_sessions[session_id]['status'] = 'error'
                search_sessions[session_id]['error'] = str(e)
                search_sessions[session_id]['completed'] = True


@app.route('/api/search/<session_id>/steps', methods=['GET'])
def get_search_steps(session_id):
    """Get search steps for a session."""
    try:
        with sessions_lock:
            if session_id not in search_sessions:
                return jsonify({
                    'success': False,
                    'error': 'Session not found'
                }), 404
            
            session = search_sessions[session_id]
            
            # Get optional offset parameter to support incremental fetching
            offset = int(request.args.get('offset', 0))
            
            response = {
                'success': True,
                'status': session['status'],
                'completed': session['completed'],
                'steps': session['steps'][offset:],
                'total_steps': len(session['steps']),
                'offset': offset
            }
            
            if session['completed']:
                response['solution_found'] = session.get('solution_found', False)
                if 'solution_path' in session:
                    response['solution_path'] = session['solution_path']
                    response['solution_cost'] = session['solution_cost']
                if 'error' in session and session['error']:
                    response['error'] = session['error']
            
            return jsonify(response)
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/search/<session_id>/cancel', methods=['POST'])
def cancel_search(session_id):
    """Cancel a running search."""
    try:
        with sessions_lock:
            if session_id not in search_sessions:
                return jsonify({
                    'success': False,
                    'error': 'Session not found'
                }), 404
            
            search_sessions[session_id]['status'] = 'cancelled'
            search_sessions[session_id]['completed'] = True
        
        return jsonify({
            'success': True,
            'message': 'Search cancelled'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'success': True,
        'message': 'Server is running',
        'graphs_available': len(graph_manager.list_graphs()),
        'algorithms_available': len(algorithm_registry.list_names()),
        'heuristics_available': len(heuristic_registry.list_names())
    })


if __name__ == '__main__':
    print("=" * 60)
    print("Pathfinding Visualization API Server")
    print("=" * 60)
    print("\nAvailable graphs:")
    for graph in graph_manager.list_graphs():
        print(f"  - {graph['name']}: {graph['node_count']} nodes")
    
    print("\nAvailable algorithms:")
    for algo in algorithm_registry.list_all():
        heur = " (requires heuristic)" if algo.requires_heuristic else ""
        print(f"  - {algo.display_name}{heur}")
    
    print("\nStarting server on http://localhost:5004")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5004, debug=True, threaded=True)

