"""
Graph builder module for SafeRoute AI.
Creates a weighted graph network using networkx.
"""

import networkx as nx
import numpy as np
import pandas as pd
from typing import Dict, Tuple


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate Euclidean distance between two points (simplified).
    
    Args:
        lat1, lon1: Coordinates of first point
        lat2, lon2: Coordinates of second point
        
    Returns:
        Distance in approximate meters
    """
    # Simple Euclidean distance scaled to approximate meters
    # (rough approximation for small distances)
    lat_diff = (lat2 - lat1) * 111000  # 1 degree latitude ≈ 111km
    lon_diff = (lon2 - lon1) * 111000 * np.cos(np.radians(lat1))
    return np.sqrt(lat_diff**2 + lon_diff**2)


def build_graph(locations_df: pd.DataFrame, 
                risk_scores: np.ndarray,
                max_connection_distance: float = 500.0) -> nx.Graph:
    """
    Build a weighted graph where nodes are locations and edges are paths.
    
    Args:
        locations_df: DataFrame with location information
        risk_scores: Array of risk scores for each location
        max_connection_distance: Maximum distance (meters) to connect two nodes
        
    Returns:
        NetworkX graph with weighted edges
    """
    G = nx.Graph()
    
    # Add nodes with attributes
    for idx, row in locations_df.iterrows():
        G.add_node(
            row['location_id'],
            latitude=row['latitude'],
            longitude=row['longitude'],
            risk_score=risk_scores[idx]
        )
    
    # Add edges between nearby nodes
    num_locations = len(locations_df)
    
    for i in range(num_locations):
        loc1 = locations_df.iloc[i]
        for j in range(i + 1, num_locations):
            loc2 = locations_df.iloc[j]
            
            # Calculate distance
            distance = calculate_distance(
                loc1['latitude'], loc1['longitude'],
                loc2['latitude'], loc2['longitude']
            )
            
            # Only connect nearby locations
            if distance <= max_connection_distance:
                # Calculate edge weight based on distance and risk
                avg_risk = (risk_scores[i] + risk_scores[j]) / 2.0
                
                # Weight combines distance and risk
                # Higher risk = higher weight (less desirable)
                # Formula: distance * (1 + risk_factor)
                risk_multiplier = 1 + (avg_risk * 2.0)  # Risk can double the effective distance
                edge_weight = distance * risk_multiplier
                
                G.add_edge(
                    loc1['location_id'],
                    loc2['location_id'],
                    weight=edge_weight,
                    distance=distance,
                    risk=avg_risk
                )
    
    return G


def get_node_info(G: nx.Graph, node_id: int) -> Dict:
    """
    Get information about a specific node in the graph.
    
    Args:
        G: NetworkX graph
        node_id: Node identifier
        
    Returns:
        Dictionary with node attributes
    """
    if node_id not in G.nodes:
        raise ValueError(f"Node {node_id} not found in graph")
    
    return G.nodes[node_id]


def find_nearest_node(G: nx.Graph, lat: float, lon: float) -> int:
    """
    Find the nearest node in the graph to given coordinates.
    
    Args:
        G: NetworkX graph
        lat: Latitude
        lon: Longitude
        
    Returns:
        Node ID of nearest node
    """
    min_distance = float('inf')
    nearest_node = None
    
    for node_id in G.nodes:
        node_data = G.nodes[node_id]
        distance = calculate_distance(
            lat, lon,
            node_data['latitude'], node_data['longitude']
        )
        
        if distance < min_distance:
            min_distance = distance
            nearest_node = node_id
    
    return nearest_node


def get_graph_stats(G: nx.Graph) -> Dict:
    """
    Get statistics about the graph.
    
    Args:
        G: NetworkX graph
        
    Returns:
        Dictionary with graph statistics
    """
    return {
        'num_nodes': G.number_of_nodes(),
        'num_edges': G.number_of_edges(),
        'is_connected': nx.is_connected(G),
        'avg_degree': sum(dict(G.degree()).values()) / G.number_of_nodes() if G.number_of_nodes() > 0 else 0
    }
