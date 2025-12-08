# Pathfinding on Armenia’s Road Network

A comprehensive implementation of pathfinding algorithms applied to real-world road networks in Armenia, featuring both uninformed and informed search strategies.

## Features

- **7 Search Algorithms**: UCS, A\*, Bidirectional Search, D\* Lite, BFS (Graph/Tree), DFS (Graph/Tree)
- **Real-World Graphs**: Pre-built road networks for Armenia's cities, Armenia's cities & villages and Yerevan
- **Heuristic**: Haversine distance for accurate geospatial estimation
- **Performance Analysis**: Comparison tools and visualization notebooks

## Table of Contents

- [Project Structure](#project-structure)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Available Algorithms](#available-algorithms)
- [Graph Data](#graph-data)
- [Jupyter Notebooks](#jupyter-notebooks)
- [Algorithm Details](#algorithm-details)
- [Web Application](#web-application)

## Project Structure

```
ai-pathfinding-project/
├── src/
│   ├── search.py              # Base search framework (State, Node, Frontier, Search)
│   ├── graph_search.py        # Graph-specific algorithms (UCS, A*, Bidirectional, D* Lite)
│   ├── prepare_graphs.py      # Script to generate road network graphs
│   ├── graphs/                # Pre-generated graph files (*.pkl)
│   │   ├── armenia_cities.pkl
│   │   ├── armenia_cities_villages.pkl
│   │   └── yerevan.pkl
│   ├── usage.ipynb            # Basic usage examples
│   ├── comparison.ipynb       # Algorithm performance comparison
│   └── ground.ipynb           # Ground truth validation
├── README.md                  # This file
└── requirements.txt           # Python dependencies
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai-pathfinding-project
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
   or
   ```bash
   conda create --name <env_name>
   conda activate <env_name>
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Dependencies

```
networkx>=3.2.1      # Graph data structures and algorithms
osmnx>=1.9.2         # Download road networks from OpenStreetMap
geopandas>=0.14.3    # Geospatial data processing
shapely>=2.0.3       # Geometric operations
```

## Quick Start

### Running Jupyter Notebooks

The easiest way to get started is with the provided notebooks:

```bash
jupyter notebook src/usage.ipynb
```

## Available Algorithms

### Uninformed Search

| Algorithm | Class | Description | Optimal? | Complete? |
|-----------|-------|-------------|----------|-----------|
| **UCS** | `UCSGraphSearch` | Uniform Cost Search - expands nodes in order of path cost | Yes | Yes |
| **A\*** | `AStarGraphSearch` | Best-first search using f(n) = g(n) + h(n) | Yes* | Yes |
| **Bidirectional** | `BidirectionalGraphSearch` | Simultaneous search from start and goal | Yes | Yes |
| **D\* Lite** | `DStarSearch` | Incremental search for dynamic environments | Yes* | Yes |

\*Optimal when using admissible/consistent heuristic

### Heuristics

- **Haversine Distance**: Great-circle distance on Earth's surface
  - Admissible: Always underestimates actual driving distance
  - Consistent: Satisfies triangle inequality

## Graph Data

### Pre-built Graphs

Three road network graphs are included in `src/graphs/`, which were generated with `src/prepare_graphs.py`:

| Graph | File | Nodes | Edges | Description |
|-------|------|-------|-------|-------------|
| **Armenia Cities** | `armenia_cities.pkl` | 50 | 150 | Major cities connected by primary roads |
| **Armenia Cities & Villages** | `armenia_cities_villages.pkl` | 993 | 3,968 | Extended network including villages |
| **Yerevan** | `yerevan.pkl` | 5,815 | 13,814 | Complete Yerevan city road network |

This script uses OSMnx to download real road network data from OpenStreetMap and processes it for use with the search algorithms.

### Graph Structure

Graphs are NetworkX `MultiGraph` objects with the following node attributes:
- `x`: Longitude
- `y`: Latitude  
- `name`: City/location name (for cities only)
- `osmid`: OpenStreetMap node ID

Edge attributes:
- `length`: Distance in meters
- `osmid`: OpenStreetMap way ID
- `highway`: Road type (motorway, primary, etc.)

## Jupyter Notebooks

1. **`usage.ipynb`**: Basic usage examples and getting started guide
2. **`comparison.ipynb`**: Comprehensive algorithm performance comparison

## Algorithm Details

For detailed implementation notes and theoretical background, see:
- `src/search.py`: Base search framework
- `src/graph_search.py`: Graph-specific implementations

## Web Application

**Want to visualize these algorithms in action?** Check out the interactive web application on the `ui-app` branch:

```bash
git checkout ui-app
```

See the `ui-app` branch README for setup instructions.

## License

This project is part of an AI course final project.