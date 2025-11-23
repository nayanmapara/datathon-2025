import pandas as pd

def load_all_data():
    cyclists = pd.read_csv("data/cyclists_toronto.csv")
    crime = pd.read_csv("data/major_crime_indicators.csv")
    collisions = pd.read_csv("data/traffic_collisions.csv")
    return cyclists, crime, collisions
