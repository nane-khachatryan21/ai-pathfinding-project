#!/usr/bin/env python3
"""
Script to prepare and save graph data files for the pathfinding visualization.

This script creates three graph variants:
1. Armenia Cities - Road network connecting major cities
2. Armenia Cities & Villages - Extended network including villages  
3. Yerevan - Complete Yerevan city road network

Usage:
    python prepare_graphs.py
"""

import os
import pickle
import osmnx as ox
import networkx as nx
from shapely.geometry import Point
import geopandas as gpd

# Configure osmnx
ox.settings.use_cache = True
ox.settings.log_console = True

# Output directory for graphs
GRAPHS_DIR = os.path.join(os.path.dirname(__file__), 'graphs')


def ensure_graphs_dir():
    """Ensure the graphs directory exists."""
    if not os.path.exists(GRAPHS_DIR):
        os.makedirs(GRAPHS_DIR)
        print(f"Created directory: {GRAPHS_DIR}")


def prepare_armenia_cities():
    """
    Prepare Armenia cities graph - intercity road network.
    Based on the ground.ipynb code.
    """
    print("\n=== Preparing Armenia Cities Graph ===")
    
    PLACE = "Armenia"
    HIGHWAYS = "motorway|trunk|primary|secondary|tertiary"
    CUSTOM_FILTER = f'["highway"~"{HIGHWAYS}"]'
    
    try:
        # Get boundary polygon for Armenia
        armenia = ox.geocode_to_gdf(PLACE).to_crs(4326)
        poly = armenia.geometry.iloc[0]
        
        # Build intercity road network
        print("Downloading road network...")
        G = ox.graph.graph_from_polygon(
            poly, network_type="drive", simplify=True, custom_filter=CUSTOM_FILTER
        )
        G = ox.truncate.largest_component(G, strongly=False)
        
        # Get settlements (cities + towns)
        print("Getting cities and towns...")
        sett = ox.features.features_from_polygon(poly, tags={"place": ["city", "town"]})
        sett = sett[~sett.geometry.is_empty].copy()
        
        def to_point(geom):
            return geom if geom.geom_type == "Point" else geom.centroid
        
        sett["rep_point"] = sett.geometry.apply(to_point)
        name_col = "name:en" if "name:en" in sett.columns else "name"
        sett["label"] = sett[name_col].astype(str)
        
        sett = sett.loc[:, ["label", "rep_point"]].drop_duplicates("label")
        sett = gpd.GeoDataFrame(sett, geometry="rep_point", crs="EPSG:4326")
        
        # Map settlements to nearest road nodes
        print("Mapping settlements to road network...")
        xs = sett["rep_point"].x.values
        ys = sett["rep_point"].y.values
        nearest_nodes = ox.distance.nearest_nodes(G, X=xs, Y=ys)
        sett["graph_node"] = nearest_nodes
        
        # Build city-level graph
        print("Building city-level graph...")
        def gc_km(a: Point, b: Point):
            return ox.distance.great_circle(a.y, a.x, b.y, b.x) / 1000.0
        
        coords = sett.set_index("label")["rep_point"].to_dict()
        nodes = sett.set_index("label")["graph_node"].to_dict()
        labels = list(coords.keys())
        
        k = 3  # connect to k nearest neighbors
        radius_km = 90  # within this radius
        
        H = nx.MultiGraph()
        for lbl in labels:
            H.add_node(lbl, x=coords[lbl].x, y=coords[lbl].y, graph_node=nodes[lbl])
        
        for u in labels:
            neigh = sorted(
                ((v, gc_km(coords[u], coords[v])) for v in labels if v != u),
                key=lambda x: x[1]
            )[:k]
            
            for v, crow in neigh:
                if crow > radius_km:
                    continue
                u_node, v_node = nodes[u], nodes[v]
                try:
                    length_m = nx.shortest_path_length(G, u_node, v_node, weight="length")
                    path = nx.shortest_path(G, u_node, v_node, weight="length")
                    H.add_edge(u, v,
                              length_m=length_m,
                              length_km=length_m/1000.0,
                              length=length_m,  # for compatibility
                              crow_km=crow,
                              road_path=path)
                except nx.NetworkXNoPath:
                    continue
        
        print(f"Cities graph: {H.number_of_nodes()} nodes, {H.number_of_edges()} edges")
        
        # Save graph
        output_path = os.path.join(GRAPHS_DIR, 'armenia_cities.pkl')
        with open(output_path, 'wb') as f:
            pickle.dump(H, f, protocol=pickle.HIGHEST_PROTOCOL)
        print(f"Saved to: {output_path}")
        
        return H
        
    except Exception as e:
        print(f"Error preparing Armenia cities graph: {e}")
        return None


def prepare_armenia_cities_villages():
    """
    Prepare Armenia cities + villages graph - extended network.
    """
    print("\n=== Preparing Armenia Cities & Villages Graph ===")
    
    PLACE = "Armenia"
    HIGHWAYS = "motorway|trunk|primary|secondary|tertiary"
    CUSTOM_FILTER = f'["highway"~"{HIGHWAYS}"]'
    
    try:
        # Get boundary polygon for Armenia
        armenia = ox.geocode_to_gdf(PLACE).to_crs(4326)
        poly = armenia.geometry.iloc[0]
        
        # Build intercity road network (reuse if available)
        print("Downloading road network...")
        G = ox.graph.graph_from_polygon(
            poly, network_type="drive", simplify=True, custom_filter=CUSTOM_FILTER
        )
        G = ox.truncate.largest_component(G, strongly=False)
        
        # Get settlements (cities + towns + villages)
        print("Getting cities, towns, and villages...")
        sett = ox.features.features_from_polygon(
            poly, tags={"place": ["city", "town", "village"]}
        )
        sett = sett[~sett.geometry.is_empty].copy()
        
        def to_point(geom):
            return geom if geom.geom_type == "Point" else geom.centroid
        
        sett["rep_point"] = sett.geometry.apply(to_point)
        name_col = "name:en" if "name:en" in sett.columns else "name"
        sett["label"] = sett[name_col].astype(str)
        
        sett = sett.loc[:, ["label", "rep_point"]].drop_duplicates("label")
        sett = gpd.GeoDataFrame(sett, geometry="rep_point", crs="EPSG:4326")
        
        # Map settlements to nearest road nodes
        print("Mapping settlements to road network...")
        xs = sett["rep_point"].x.values
        ys = sett["rep_point"].y.values
        nearest_nodes = ox.distance.nearest_nodes(G, X=xs, Y=ys)
        sett["graph_node"] = nearest_nodes
        
        # Build settlement-level graph
        print("Building cities+villages graph...")
        def gc_km(a: Point, b: Point):
            return ox.distance.great_circle(a.y, a.x, b.y, b.x) / 1000.0
        
        coords = sett.set_index("label")["rep_point"].to_dict()
        nodes = sett.set_index("label")["graph_node"].to_dict()
        labels = list(coords.keys())
        
        k = 4  # connect to k nearest neighbors (more for denser network)
        radius_km = 60  # within this radius (smaller for villages)
        
        H = nx.MultiGraph()
        for lbl in labels:
            H.add_node(lbl, x=coords[lbl].x, y=coords[lbl].y, graph_node=nodes[lbl])
        
        for u in labels:
            neigh = sorted(
                ((v, gc_km(coords[u], coords[v])) for v in labels if v != u),
                key=lambda x: x[1]
            )[:k]
            
            for v, crow in neigh:
                if crow > radius_km:
                    continue
                u_node, v_node = nodes[u], nodes[v]
                try:
                    length_m = nx.shortest_path_length(G, u_node, v_node, weight="length")
                    path = nx.shortest_path(G, u_node, v_node, weight="length")
                    H.add_edge(u, v,
                              length_m=length_m,
                              length_km=length_m/1000.0,
                              length=length_m,
                              crow_km=crow,
                              road_path=path)
                except nx.NetworkXNoPath:
                    continue
        
        print(f"Cities+Villages graph: {H.number_of_nodes()} nodes, {H.number_of_edges()} edges")
        
        # Save graph
        output_path = os.path.join(GRAPHS_DIR, 'armenia_cities_villages.pkl')
        with open(output_path, 'wb') as f:
            pickle.dump(H, f, protocol=pickle.HIGHEST_PROTOCOL)
        print(f"Saved to: {output_path}")
        
        return H
        
    except Exception as e:
        print(f"Error preparing Armenia cities+villages graph: {e}")
        return None


def prepare_yerevan():
    """
    Prepare Yerevan city graph - detailed street network.
    """
    print("\n=== Preparing Yerevan Graph ===")
    
    PLACE = "Yerevan, Armenia"
    
    try:
        # Download Yerevan street network
        print("Downloading Yerevan street network...")
        G = ox.graph.graph_from_place(PLACE, network_type="drive", simplify=True)
        G = ox.truncate.largest_component(G, strongly=False)
        
        # Clean node attributes - keep only essential data
        for _, data in G.nodes(data=True):
            # Keep only x, y coordinates
            keys_to_remove = [k for k in data.keys() if k not in ['x', 'y']]
            for k in keys_to_remove:
                data.pop(k, None)
        
        # Clean edge attributes
        for u, v, k, data in G.edges(keys=True, data=True):
            # Keep only length
            keys_to_keep = ['length']
            keys_to_remove = [key for key in data.keys() if key not in keys_to_keep]
            for key in keys_to_remove:
                data.pop(key, None)
        
        print(f"Yerevan graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
        
        # Save graph
        output_path = os.path.join(GRAPHS_DIR, 'yerevan.pkl')
        with open(output_path, 'wb') as f:
            pickle.dump(G, f, protocol=pickle.HIGHEST_PROTOCOL)
        print(f"Saved to: {output_path}")
        
        return G
        
    except Exception as e:
        print(f"Error preparing Yerevan graph: {e}")
        return None


def main():
    """Main function to prepare all graphs."""
    print("=" * 60)
    print("Graph Preparation Script")
    print("=" * 60)
    
    ensure_graphs_dir()
    
    # Prepare all three graphs
    print("\nThis may take several minutes depending on your internet connection...")
    
    # 1. Armenia Cities
    armenia_cities = prepare_armenia_cities()
    
    # 2. Armenia Cities & Villages (this will take longer)
    armenia_full = prepare_armenia_cities_villages()
    
    # 3. Yerevan
    yerevan = prepare_yerevan()
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary:")
    print("=" * 60)
    if armenia_cities:
        print(f"✓ Armenia Cities: {armenia_cities.number_of_nodes()} nodes")
    else:
        print("✗ Armenia Cities: Failed")
    
    if armenia_full:
        print(f"✓ Armenia Cities & Villages: {armenia_full.number_of_nodes()} nodes")
    else:
        print("✗ Armenia Cities & Villages: Failed")
    
    if yerevan:
        print(f"✓ Yerevan: {yerevan.number_of_nodes()} nodes")
    else:
        print("✗ Yerevan: Failed")
    
    print("\nAll graph files saved to:", GRAPHS_DIR)
    print("You can now start the Flask server.")


if __name__ == "__main__":
    main()

