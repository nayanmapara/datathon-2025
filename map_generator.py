"""
Map generator module for SafeRoute AI.
Creates interactive maps using Folium for route visualization.
"""

import folium
import pandas as pd
import networkx as nx
from typing import List, Tuple, Optional


def create_base_map(center_lat: float = 40.7128, 
                   center_lon: float = -74.0060,
                   zoom_start: int = 13) -> folium.Map:
    """
    Create a base Folium map.
    
    Args:
        center_lat: Latitude for map center
        center_lon: Longitude for map center
        zoom_start: Initial zoom level
        
    Returns:
        Folium map object
    """
    return folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom_start,
        tiles='OpenStreetMap'
    )


def add_route_to_map(folium_map: folium.Map, 
                     coordinates: List[Tuple[float, float]],
                     color: str = 'blue',
                     weight: int = 5,
                     opacity: float = 0.7,
                     popup_text: str = None) -> folium.Map:
    """
    Add a route line to the map.
    
    Args:
        folium_map: Folium map object
        coordinates: List of (latitude, longitude) tuples
        color: Line color
        weight: Line width
        opacity: Line opacity
        popup_text: Optional popup text for the route
        
    Returns:
        Updated Folium map object
    """
    if len(coordinates) < 2:
        return folium_map
    
    folium.PolyLine(
        locations=coordinates,
        color=color,
        weight=weight,
        opacity=opacity,
        popup=popup_text if popup_text else None
    ).add_to(folium_map)
    
    return folium_map


def add_markers_to_map(folium_map: folium.Map,
                       start_coords: Tuple[float, float],
                       end_coords: Tuple[float, float]) -> folium.Map:
    """
    Add start and end markers to the map.
    
    Args:
        folium_map: Folium map object
        start_coords: (latitude, longitude) of start point
        end_coords: (latitude, longitude) of end point
        
    Returns:
        Updated Folium map object
    """
    # Start marker (green)
    folium.Marker(
        location=start_coords,
        popup='Start',
        icon=folium.Icon(color='green', icon='play', prefix='fa')
    ).add_to(folium_map)
    
    # End marker (red)
    folium.Marker(
        location=end_coords,
        popup='End',
        icon=folium.Icon(color='red', icon='stop', prefix='fa')
    ).add_to(folium_map)
    
    return folium_map


def add_risk_heatmap(folium_map: folium.Map,
                     locations_df: pd.DataFrame,
                     risk_scores: List[float]) -> folium.Map:
    """
    Add risk visualization to the map using colored circles.
    
    Args:
        folium_map: Folium map object
        locations_df: DataFrame with location data
        risk_scores: List of risk scores
        
    Returns:
        Updated Folium map object
    """
    for idx, row in locations_df.iterrows():
        risk_score = risk_scores[idx]
        
        # Determine color based on risk
        if risk_score < 0.33:
            color = 'green'
            risk_label = 'Low Risk'
        elif risk_score < 0.67:
            color = 'orange'
            risk_label = 'Medium Risk'
        else:
            color = 'red'
            risk_label = 'High Risk'
        
        # Add circle marker
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=3,
            color=color,
            fill=True,
            fillColor=color,
            fillOpacity=0.4,
            popup=f"Location {row['location_id']}<br>{risk_label}<br>Score: {risk_score:.2f}"
        ).add_to(folium_map)
    
    return folium_map


def create_route_comparison_map(
    safest_route_coords: List[Tuple[float, float]],
    shortest_route_coords: List[Tuple[float, float]],
    safest_info: dict,
    shortest_info: dict,
    locations_df: Optional[pd.DataFrame] = None,
    risk_scores: Optional[List[float]] = None
) -> folium.Map:
    """
    Create a map comparing the safest and shortest routes.
    
    Args:
        safest_route_coords: Coordinates for safest route
        shortest_route_coords: Coordinates for shortest route
        safest_info: Route information for safest route
        shortest_info: Route information for shortest route
        locations_df: Optional DataFrame with all locations
        risk_scores: Optional list of risk scores for visualization
        
    Returns:
        Folium map with both routes
    """
    # Calculate map center
    all_coords = safest_route_coords + shortest_route_coords
    center_lat = sum(c[0] for c in all_coords) / len(all_coords)
    center_lon = sum(c[1] for c in all_coords) / len(all_coords)
    
    # Create base map
    folium_map = create_base_map(center_lat, center_lon, zoom_start=14)
    
    # Add risk heatmap if available
    if locations_df is not None and risk_scores is not None:
        folium_map = add_risk_heatmap(folium_map, locations_df, risk_scores)
    
    # Add shortest route (in red, thinner)
    if shortest_route_coords:
        shortest_popup = (
            f"Shortest Route<br>"
            f"Distance: {shortest_info['total_distance']:.0f}m<br>"
            f"Avg Risk: {shortest_info['avg_risk_score']:.2f}"
        )
        folium_map = add_route_to_map(
            folium_map, 
            shortest_route_coords, 
            color='red',
            weight=4,
            opacity=0.5,
            popup_text=shortest_popup
        )
    
    # Add safest route (in green, thicker)
    if safest_route_coords:
        safest_popup = (
            f"Safest Route<br>"
            f"Distance: {safest_info['total_distance']:.0f}m<br>"
            f"Avg Risk: {safest_info['avg_risk_score']:.2f}"
        )
        folium_map = add_route_to_map(
            folium_map, 
            safest_route_coords, 
            color='green',
            weight=6,
            opacity=0.8,
            popup_text=safest_popup
        )
    
    # Add start and end markers
    if safest_route_coords:
        folium_map = add_markers_to_map(
            folium_map,
            safest_route_coords[0],
            safest_route_coords[-1]
        )
    
    # Add legend
    legend_html = '''
    <div style="position: fixed; 
                bottom: 50px; right: 50px; width: 200px; height: 140px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:14px; padding: 10px">
    <p><strong>Route Legend</strong></p>
    <p><span style="color:green; font-weight:bold;">━━━</span> Safest Route</p>
    <p><span style="color:red; font-weight:bold;">━━━</span> Shortest Route</p>
    <p><span style="color:green;">●</span> Low Risk</p>
    <p><span style="color:orange;">●</span> Medium Risk</p>
    <p><span style="color:red;">●</span> High Risk</p>
    </div>
    '''
    folium_map.get_root().html.add_child(folium.Element(legend_html))
    
    return folium_map
