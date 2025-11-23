import streamlit as st
import networkx as nx
import os
import pandas as pd
import pydeck as pdk

from src.data_loader import load_cyclist_data, load_crime_data, load_collision_data
from src.feature_engineering import preprocess_all
from src.risk_model import build_risk_model
from src.graph_builder import build_graph, get_nearest_node

st.title("SafeRoute AI – MVP (All Datasets Included)")

DATA_DIR = "data"
DEFAULT_CYCLIST = os.path.join(DATA_DIR, "cyclists_toronto.csv")
DEFAULT_CRIME   = os.path.join(DATA_DIR, "major_crime_indicators.csv")
DEFAULT_COLL    = os.path.join(DATA_DIR, "traffic_collisions.csv")

def debug(msg, obj):
    st.text(f"{msg}: {str(obj)}")

cycle_file = st.file_uploader("Cyclists Dataset", type="csv")
crime_file = st.file_uploader("Crime Dataset", type="csv")
coll_file = st.file_uploader("Collisions Dataset", type="csv")

if cycle_file is None:
    debug("Using default cyclist file", DEFAULT_CYCLIST)
    cycle_file = DEFAULT_CYCLIST
if crime_file is None:
    debug("Using default crime file", DEFAULT_CRIME)
    crime_file = DEFAULT_CRIME
if coll_file is None:
    debug("Using default collision file", DEFAULT_COLL)
    coll_file = DEFAULT_COLL

if cycle_file and crime_file and coll_file:
    st.success("All datasets loaded!")

    df_cyc = load_cyclist_data(cycle_file)
    df_crime = load_crime_data(crime_file)
    df_coll = load_collision_data(coll_file)
    df_all = preprocess_all(df_cyc, df_crime, df_coll)

    st.write("### Preview of combined dataset:")
    st.dataframe(df_all.head())

    # Filter to Toronto bounds (adjust if your area is different)
    df_all = df_all[(df_all["lat"] != 0) & (df_all["lon"] != 0)]
    df_all = df_all[(df_all["lat"] > 43.5) & (df_all["lat"] < 44.0) & 
                    (df_all["lon"] < -79.0) & (df_all["lon"] > -80.1)]
    debug("Filtered dataset bounds", {
        "lat_min": df_all["lat"].min(),
        "lat_max": df_all["lat"].max(),
        "lon_min": df_all["lon"].min(),
        "lon_max": df_all["lon"].max()
    })

    model = build_risk_model(df_all)
    st.success("Risk model trained.")

    col1, col2 = st.columns(2)
    start_lat = col1.number_input("Start Latitude", format="%.6f")
    start_lon = col1.number_input("Start Longitude", format="%.6f")
    end_lat = col2.number_input("End Latitude", format="%.6f")
    end_lon = col2.number_input("End Longitude", format="%.6f")

    st.info(f"Valid Lat: {df_all['lat'].min():.6f}-{df_all['lat'].max():.6f}, Lon: {df_all['lon'].min():.6f}-{df_all['lon'].max():.6f}")

    if st.button("Find Safe Route"):
        st.text("Building graph...")
        G = build_graph(df_all, model)
        debug("Number of graph nodes", len(G.nodes))
        debug("First 5 graph nodes", list(G.nodes)[:5])

        start_node = get_nearest_node(G, float(start_lat), float(start_lon))
        st.text(f"Start node used: {start_node}")
        end_node = get_nearest_node(G, float(end_lat), float(end_lon))
        st.text(f"End node used: {end_node}")

        try:
            st.text("Attempting path finding...")
            path = nx.shortest_path(G, start_node, end_node, weight="weight")
            st.success("Route generated!")
            st.text(f"First 10 nodes in path: {path[:10]}")

            # --- Visualization of Route ---
            st.text("Plotting route on map...")
            route_df = pd.DataFrame(path, columns=["lat", "lon"])
            route_df["lonlat"] = route_df.apply(lambda r: [r["lon"], r["lat"]], axis=1)
            st.pydeck_chart(
                pdk.Deck(
                    map_style="mapbox://styles/mapbox/light-v9",
                    initial_view_state=pdk.ViewState(
                        latitude=route_df["lat"].iloc[0],
                        longitude=route_df["lon"].iloc[0],
                        zoom=11
                    ),
                    layers=[
                        pdk.Layer(
                            "ScatterplotLayer",
                            data=route_df,
                            get_position="lonlat",
                            get_color=[0, 0, 255],
                            get_radius=100,
                        ),
                        pdk.Layer(
                            "PathLayer",
                            data=[{"path": route_df["lonlat"].tolist()}],
                            get_path="path",
                            get_color=[255, 0, 0],
                            width_scale=10,
                            width_min_pixels=3,
                        ),
                    ],
                )
            )
        except nx.NetworkXNoPath:
            st.error("No path could be found between your selected points.")
            st.text(f"Start node: {start_node}, End node: {end_node}")
            st.text(f"Grid bounds: Lat {df_all['lat'].min()} to {df_all['lat'].max()}, Lon {df_all['lon'].min()} to {df_all['lon'].max()}.")
            st.text("First 5 available nodes: " + str(list(G.nodes)[:5]))
            st.text("Pick coordinates close to these grid values.")
