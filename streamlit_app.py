import streamlit as st
import networkx as nx
import os

from src.data_loader import load_cyclist_data, load_crime_data, load_collision_data
from src.feature_engineering import preprocess_all
from src.risk_model import build_risk_model
from src.graph_builder import build_graph, get_nearest_node

st.title("SafeRoute AI – MVP (All Datasets Included)")

# --------------------------
# Upload files (with defaults)
# --------------------------

DATA_DIR = "data"
DEFAULT_CYCLIST = os.path.join(DATA_DIR, "cyclist.csv")
DEFAULT_CRIME   = os.path.join(DATA_DIR, "crime.csv")
DEFAULT_COLL    = os.path.join(DATA_DIR, "collision.csv")

cycle_file = st.file_uploader("Cyclists Dataset", type="csv")
crime_file = st.file_uploader("Crime Dataset", type="csv")
coll_file = st.file_uploader("Collisions Dataset", type="csv")

# Use files from 'data' folder if not uploaded
if cycle_file is None:
    cycle_file = DEFAULT_CYCLIST
if crime_file is None:
    crime_file = DEFAULT_CRIME
if coll_file is None:
    coll_file = DEFAULT_COLL

if cycle_file and crime_file and coll_file:
    st.success("All datasets loaded!")

    df_cyc = load_cyclist_data(cycle_file)
    df_crime = load_crime_data(crime_file)
    df_coll = load_collision_data(coll_file)
    df_all = preprocess_all(df_cyc, df_crime, df_coll)
    st.write("### Preview of combined dataset:")
    st.dataframe(df_all.head())

    # Build risk model
    model = build_risk_model(df_all)
    st.success("Risk model trained.")

    # Input fields
    col1, col2 = st.columns(2)
    start_lat = col1.number_input("Start Latitude")
    start_lon = col1.number_input("Start Longitude")
    end_lat = col2.number_input("End Latitude")
    end_lon = col2.number_input("End Longitude")

    if st.button("Find Safe Route"):
        G = build_graph(df_all, model)
        start = get_nearest_node(G, float(start_lat), float(start_lon))
        end = get_nearest_node(G, float(end_lat), float(end_lon))

        try:
            path = nx.shortest_path(G, start, end, weight="weight")
            st.success("Route generated!")
            st.write(path[:10], "...")
        except nx.NetworkXNoPath:
            st.error("No path could be found between your selected points. Try adjusting your inputs.")
