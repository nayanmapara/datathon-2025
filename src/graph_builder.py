import networkx as nx
import numpy as np
from math import sqrt
from src.risk_model import predict_point_risk

def build_graph(df_all, risk_model):

    G = nx.Graph()

    # Build grid covering city
    lats = np.linspace(df_all["lat"].min(), df_all["lat"].max(), 60)
    lons = np.linspace(df_all["lon"].min(), df_all["lon"].max(), 60)

    nodes = []
    for la in lats:
        for lo in lons:
            node = (float(la), float(lo))
            nodes.append(node)
            G.add_node(node)

    # Add weighted edges
    for a in nodes:
        for b in nodes:
            if abs(a[0] - b[0]) < 0.002 and abs(a[1] - b[1]) < 0.002:
                dist = sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)

                risk = predict_point_risk(risk_model, a[0], a[1])
                weight = dist * (1 + risk)

                G.add_edge(a, b, weight=weight)

    return G


def get_nearest_node(G, lat, lon):
    return min(G.nodes, key=lambda p: (p[0] - lat)**2 + (p[1] - lon)**2)
