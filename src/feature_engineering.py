import pandas as pd

def preprocess_cyclists(df):
    df = df.rename(columns={"LAT": "lat", "LONG": "lon"})
    df["hour"] = df["ACC TIME.hour"]
    df["severity"] = df["INJURY"].apply(lambda x: 1 if x != "None" else 0)
    return df[["lat", "lon", "hour", "severity"]]

def preprocess_crime(df):
    df = df.rename(columns={"LAT_WGS84": "lat", "LONG_WGS84": "lon"})
    df["hour"] = df["OCC_HOUR"]
    df["severity"] = df["MCI_CATEGORY"].apply(lambda x: 1 if x in ["Assault", "Robbery"] else 0)
    return df[["lat", "lon", "hour", "severity"]]

def preprocess_collisions(df):
    df = df.rename(columns={"Latitude": "lat", "Longitude": "lon"})
    df["hour"] = df["Hour"]
    df["severity"] = df["Injury_Collisions"] + df["Fatalities"]
    return df[["lat", "lon", "hour", "severity"]]

def preprocess_all(cyc, crime, coll):
    return preprocess_cyclists(cyc), preprocess_crime(crime), preprocess_collisions(coll)
