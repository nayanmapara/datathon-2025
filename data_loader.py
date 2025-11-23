"""
Data loading module for SafeRoute AI.
Handles loading and preparation of crime, lighting, and time data.
"""

import pandas as pd
import numpy as np
from typing import Tuple


def generate_sample_data(num_locations: int = 100) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Generate sample crime, lighting, and time data for demonstration.
    
    Args:
        num_locations: Number of locations to generate
        
    Returns:
        Tuple of (locations_df, incidents_df)
    """
    np.random.seed(42)
    
    # Generate location data (nodes in the network)
    locations = []
    for i in range(num_locations):
        lat = 40.7128 + np.random.uniform(-0.05, 0.05)  # NYC-centered coordinates
        lon = -74.0060 + np.random.uniform(-0.05, 0.05)
        lighting_score = np.random.uniform(0, 1)  # 0=dark, 1=well-lit
        
        locations.append({
            'location_id': i,
            'latitude': lat,
            'longitude': lon,
            'lighting_score': lighting_score
        })
    
    locations_df = pd.DataFrame(locations)
    
    # Generate crime incident data
    incidents = []
    num_incidents = num_locations * 3  # More incidents than locations
    
    for i in range(num_incidents):
        location_id = np.random.randint(0, num_locations)
        hour = np.random.randint(0, 24)
        crime_severity = np.random.choice(['low', 'medium', 'high'], 
                                         p=[0.5, 0.3, 0.2])
        
        incidents.append({
            'incident_id': i,
            'location_id': location_id,
            'hour': hour,
            'crime_severity': crime_severity
        })
    
    incidents_df = pd.DataFrame(incidents)
    
    return locations_df, incidents_df


def load_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load or generate data for the SafeRoute AI application.
    
    Returns:
        Tuple of (locations_df, incidents_df)
    """
    # For now, generate sample data
    # In production, this would load from actual data sources
    return generate_sample_data()


def prepare_location_features(locations_df: pd.DataFrame, 
                              incidents_df: pd.DataFrame,
                              current_hour: int = 12) -> pd.DataFrame:
    """
    Prepare features for each location by aggregating incident data.
    
    Args:
        locations_df: DataFrame with location information
        incidents_df: DataFrame with crime incidents
        current_hour: Current hour of day (0-23)
        
    Returns:
        DataFrame with location features
    """
    # Calculate crime statistics per location
    crime_stats = incidents_df.groupby('location_id').agg({
        'incident_id': 'count',
        'crime_severity': lambda x: (x == 'high').sum()
    }).rename(columns={
        'incident_id': 'total_incidents',
        'crime_severity': 'high_severity_count'
    })
    
    # Calculate time-specific incidents (within 3 hours of current time)
    time_window = 3
    time_filtered = incidents_df[
        (incidents_df['hour'] >= current_hour - time_window) & 
        (incidents_df['hour'] <= current_hour + time_window)
    ]
    
    time_stats = time_filtered.groupby('location_id').size().to_frame('recent_incidents')
    
    # Merge all features
    features_df = locations_df.copy()
    features_df = features_df.merge(crime_stats, on='location_id', how='left')
    features_df = features_df.merge(time_stats, on='location_id', how='left')
    
    # Fill NaN values
    features_df['total_incidents'] = features_df['total_incidents'].fillna(0)
    features_df['high_severity_count'] = features_df['high_severity_count'].fillna(0)
    features_df['recent_incidents'] = features_df['recent_incidents'].fillna(0)
    
    return features_df
