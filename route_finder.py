"""
Route finder module for SafeRoute AI.
Implements pathfinding algorithms to find the safest route.
"""

import networkx as nx
from typing import List, Tuple, Optional, Dict


class RouteFinder:
    """
    Finds optimal routes in a weighted graph.
    """
    
    def __init__(self, graph: nx.Graph):
        """
        Initialize the route finder with a graph.
        
        Args:
            graph: NetworkX graph with weighted edges
        """
        self.graph = graph
    
    def find_safest_route(self, start_node: int, end_node: int) -> Optional[List[int]]:
        """
        Find the safest route between two nodes using Dijkstra's algorithm.
        The 'weight' attribute on edges should reflect safety (lower = safer).
        
        Args:
            start_node: Starting node ID
            end_node: Ending node ID
            
        Returns:
            List of node IDs representing the path, or None if no path exists
        """
        if start_node not in self.graph.nodes:
            raise ValueError(f"Start node {start_node} not found in graph")
        if end_node not in self.graph.nodes:
            raise ValueError(f"End node {end_node} not found in graph")
        
        try:
            # Use Dijkstra's algorithm with 'weight' attribute
            path = nx.shortest_path(
                self.graph, 
                source=start_node, 
                target=end_node, 
                weight='weight'
            )
            return path
        except nx.NetworkXNoPath:
            return None
    
    def find_shortest_route(self, start_node: int, end_node: int) -> Optional[List[int]]:
        """
        Find the shortest route by distance (ignoring safety).
        
        Args:
            start_node: Starting node ID
            end_node: Ending node ID
            
        Returns:
            List of node IDs representing the path, or None if no path exists
        """
        if start_node not in self.graph.nodes:
            raise ValueError(f"Start node {start_node} not found in graph")
        if end_node not in self.graph.nodes:
            raise ValueError(f"End node {end_node} not found in graph")
        
        try:
            # Use distance instead of weighted score
            path = nx.shortest_path(
                self.graph,
                source=start_node,
                target=end_node,
                weight='distance'
            )
            return path
        except nx.NetworkXNoPath:
            return None
    
    def get_route_info(self, path: List[int]) -> Dict:
        """
        Get detailed information about a route.
        
        Args:
            path: List of node IDs representing the route
            
        Returns:
            Dictionary with route statistics
        """
        if not path or len(path) < 2:
            return {
                'total_distance': 0.0,
                'total_risk_score': 0.0,
                'avg_risk_score': 0.0,
                'num_segments': 0
            }
        
        total_distance = 0.0
        total_risk = 0.0
        num_segments = len(path) - 1
        
        for i in range(num_segments):
            node1, node2 = path[i], path[i + 1]
            
            # Get edge data
            if self.graph.has_edge(node1, node2):
                edge_data = self.graph[node1][node2]
                total_distance += edge_data.get('distance', 0)
                total_risk += edge_data.get('risk', 0)
        
        avg_risk = total_risk / num_segments if num_segments > 0 else 0.0
        
        return {
            'total_distance': total_distance,
            'total_risk_score': total_risk,
            'avg_risk_score': avg_risk,
            'num_segments': num_segments
        }
    
    def compare_routes(self, path1: List[int], path2: List[int]) -> Dict:
        """
        Compare two routes and return statistics for both.
        
        Args:
            path1: First route (e.g., safest route)
            path2: Second route (e.g., shortest route)
            
        Returns:
            Dictionary with comparison statistics
        """
        info1 = self.get_route_info(path1)
        info2 = self.get_route_info(path2)
        
        return {
            'route1': info1,
            'route2': info2,
            'distance_difference': info1['total_distance'] - info2['total_distance'],
            'risk_difference': info1['avg_risk_score'] - info2['avg_risk_score']
        }
    
    def get_route_coordinates(self, path: List[int]) -> List[Tuple[float, float]]:
        """
        Get the coordinates of all nodes in a route.
        
        Args:
            path: List of node IDs representing the route
            
        Returns:
            List of (latitude, longitude) tuples
        """
        coordinates = []
        for node_id in path:
            node_data = self.graph.nodes[node_id]
            coordinates.append((node_data['latitude'], node_data['longitude']))
        
        return coordinates
