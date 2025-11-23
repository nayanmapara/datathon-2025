import networkx as nx

def get_safe_route(G, start, end):
    try:
        path = nx.shortest_path(G, start, end, weight="weight")
        score = round(100 - sum(G.edges[path[i], path[i+1]]["weight"] for i in range(len(path)-1)), 2)
        return path, score
    except:
        return [], 0
