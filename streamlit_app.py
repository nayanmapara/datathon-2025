import streamlit as st
from src.load_data import load_all_data
from src.feature_engineering import preprocess_all
from src.risk_model import build_risk_models
from src.risk_fusion import compute_unified_risk
from src.graph_builder import build_graph
from src.route_finder import get_safe_route
from src.map_generator import create_route_map

st.title("SafeRoute AI – Toronto 🛡️")
st.subheader("Find the safest walking route in the city")

start = st.text_input("Start (lat, lon)")
end = st.text_input("End (lat, lon)")

if st.button("Find Safe Route"):
    df_cyc, df_crime, df_coll = load_all_data()
    df_cyc, df_crime, df_coll = preprocess_all(df_cyc, df_crime, df_coll)

    km, lr = build_risk_models(df_crime)
    risk_df = compute_unified_risk(df_cyc, df_crime, df_coll, km, lr)

    G = build_graph(risk_df)

    path, score = get_safe_route(G, start, end)

    st.write(f"### Safety Score: {score}/100")

    route_map = create_route_map(path, risk_df)
    st.components.v1.html(route_map, height=500)
