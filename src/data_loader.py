import pandas as pd


def load_cyclist_data(path):
    df = pd.read_csv(path)

    # Rename based on actual cyclist dataset columns
    df = df.rename(columns={
        "LAT": "lat",
        "LONG": "lon",
    })

    # Debug print to verify columns
    print("Cyclist columns:", df.columns.tolist())

    # Keep only records with valid coordinates
    df = df[["lat", "lon"]].dropna()

    # Assign risk weight for cyclists
    df["risk"] = 1.0

    return df


def load_crime_data(path):
    df = pd.read_csv(path)

    # Rename based on crime dataset columns
    df = df.rename(columns={
        "LAT_WGS84": "lat",
        "LONG_WGS84": "lon",
    })

    print("Crime columns:", df.columns.tolist())

    df = df[["lat", "lon"]].dropna()
    df["risk"] = 2.0

    return df


def load_collision_data(path):
    df = pd.read_csv(path)

    # Rename based on collision dataset columns
    df = df.rename(columns={
        "Latitude": "lat",
        "Longitude": "lon",
        "Injury_Collisions": "inj",
        "Fatalities": "fat",
    })

    print("Collision columns:", df.columns.tolist())

    # Drop rows with missing lat/lon but keep injury/fatality nulls for imputation
    df = df[["lat", "lon", "inj", "fat"]].dropna(subset=["lat", "lon"])

    # Convert injury and fatalities to numeric, fill missing with 0
    df["inj"] = pd.to_numeric(df["inj"], errors="coerce").fillna(0)
    df["fat"] = pd.to_numeric(df["fat"], errors="coerce").fillna(0)

    # Risk is sum of injuries plus fatalities
    df["risk"] = df["inj"] + df["fat"]

    df = df[["lat", "lon", "risk"]]

    return df
