import networkx as nx

def build_graph(risk_df):
    G = nx.Graph()

    for i, row in risk_df.iterrows():
        node_id = str(i)
        G.add_node(node_id, lat=row["lat"], lon=row["lon"], risk=row["risk_score"])

        if i > 0:
            G.add_edge(str(i-1), node_id, weight=row["risk_score"])

    return G
