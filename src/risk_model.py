from sklearn.cluster import KMeans
import numpy as np

def build_risk_model(df):
    km = KMeans(n_clusters=5, random_state=42)
    km.fit(df[["lat", "lon"]])
    return km


def predict_point_risk(model, lat, lon):
    return int(model.predict([[lat, lon]])[0])
