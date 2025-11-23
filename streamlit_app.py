import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
from dotenv import load_dotenv
import os

# --- Load API key
load_dotenv()
API_KEY = os.getenv("API_KEY")

# --- Toronto Hotspots
POPULAR_LOCATIONS = {
    "Union Station": (43.645233, -79.380219),
    "CN Tower": (43.642566, -79.387057),
    "Toronto Eaton Centre": (43.654438, -79.380691),
    "Royal Ontario Museum": (43.667710, -79.394777),
    "University of Toronto": (43.662892, -79.395656),
    "Rogers Centre": (43.641921, -79.389201),
    "St. Lawrence Market": (43.648605, -79.371351),
    "Yonge-Dundas Square": (43.656066, -79.380151),
    "High Park": (43.646547, -79.463738),
    "Scarborough Town Centre": (43.775737, -79.257765),
    "Ontario Science Centre": (43.716122, -79.340664),
    "Casa Loma": (43.678019, -79.409445)
}

# --- Session state defaults
for key, value in {
    "start_lat": 43.645233, "start_lon": -79.380219,
    "end_lat": 43.642566, "end_lon": -79.387057,
    "route_geojson": None,
    "route_midpoint": None,
    "route_exists": False
}.items():
    if key not in st.session_state:
        st.session_state[key] = value

# --- UI setup
st.set_page_config(page_title="SafeRoute AI", page_icon="🚲", layout="wide")
st.markdown("### How do you want to choose route points?")
mode = st.radio(
    "Select input mode:",
    options=["By Name (dropdown)", "Manual Entry", "Pick on Map"]
)

# --- Dynamic Input
popular_names = list(POPULAR_LOCATIONS.keys())

if mode == "By Name (dropdown)":
    col1, col2 = st.columns([1, 1])
    start_name = col1.selectbox("Start location", popular_names, index=0)
    end_name = col2.selectbox("End location", popular_names, index=1)
    start_lat, start_lon = POPULAR_LOCATIONS[start_name]
    end_lat, end_lon = POPULAR_LOCATIONS[end_name]
elif mode == "Manual Entry":
    col1, col2 = st.columns([1, 1])
    start_lat = col1.number_input("Start Latitude", value=st.session_state["start_lat"], format="%.6f")
    start_lon = col1.number_input("Start Longitude", value=st.session_state["start_lon"], format="%.6f")
    end_lat = col2.number_input("End Latitude", value=st.session_state["end_lat"], format="%.6f")
    end_lon = col2.number_input("End Longitude", value=st.session_state["end_lon"], format="%.6f")
else:  # Pick on Map
    st.write("Click anywhere on map then set as Start or End below.")
    midpoint = [(st.session_state["start_lat"] + st.session_state["end_lat"]) / 2,
                (st.session_state["start_lon"] + st.session_state["end_lon"]) / 2]
    m = folium.Map(location=midpoint, zoom_start=13)
    folium.Marker([st.session_state["start_lat"], st.session_state["start_lon"]],
                  popup="Start", icon=folium.Icon(color="green")).add_to(m)
    folium.Marker([st.session_state["end_lat"], st.session_state["end_lon"]],
                  popup="End", icon=folium.Icon(color="blue")).add_to(m)
    folium.TileLayer(
        tiles=f"https://maps.geoapify.com/v1/tile/osm-carto/{{z}}/{{x}}/{{y}}.png?apiKey={API_KEY}",
        attr="Geoapify",
        overlay=False,
        control=True,
        max_zoom=20
    ).add_to(m)
    map_data = st_folium(m, width=850, height=400)
    clicked_lat = None
    clicked_lon = None
    if isinstance(map_data, dict) and "last_clicked" in map_data and map_data["last_clicked"] is not None:
        clicked_lat = map_data["last_clicked"]["lat"]
        clicked_lon = map_data["last_clicked"]["lng"]

    if clicked_lat is not None and clicked_lon is not None:
        st.write(f"Clicked: {clicked_lat:.6f}, {clicked_lon:.6f}")
        if st.button("Set as Start Point"):
            st.session_state["start_lat"] = clicked_lat
            st.session_state["start_lon"] = clicked_lon
        if st.button("Set as End Point"):
            st.session_state["end_lat"] = clicked_lat
            st.session_state["end_lon"] = clicked_lon
    start_lat = st.session_state["start_lat"]
    start_lon = st.session_state["start_lon"]
    end_lat = st.session_state["end_lat"]
    end_lon = st.session_state["end_lon"]

st.write("---")
submitted = st.button("Find Safe Route 🚦")

# --- Routing (store results in session_state)
if submitted:
    route_url = (
        f"https://api.geoapify.com/v1/routing?"
        f"waypoints={start_lat},{start_lon}|{end_lat},{end_lon}"
        f"&mode=walk&apiKey={API_KEY}"
    )
    response = requests.get(route_url)
    route_json = response.json()
    if "features" in route_json and len(route_json["features"]) > 0:
        geojson = route_json["features"][0]["geometry"]
        midpoint = [(start_lat + end_lat) / 2, (start_lon + end_lon) / 2]
        st.session_state["route_geojson"] = geojson
        st.session_state["route_midpoint"] = midpoint
        st.session_state["route_exists"] = True
    else:
        st.session_state["route_geojson"] = None
        st.session_state["route_exists"] = False

# --- Map output persists until cleared
if st.session_state["route_exists"]:
    m = folium.Map(location=st.session_state["route_midpoint"], zoom_start=13)
    folium.GeoJson(
        st.session_state["route_geojson"], name="Route",
        style_function=lambda x: {"color": "#D7263D", "weight": 7}
    ).add_to(m)
    folium.Marker([start_lat, start_lon], popup="Start", icon=folium.Icon(color="green")).add_to(m)
    folium.Marker([end_lat, end_lon], popup="End", icon=folium.Icon(color="blue")).add_to(m)
    folium.TileLayer(
        tiles=f"https://maps.geoapify.com/v1/tile/osm-carto/{{z}}/{{x}}/{{y}}.png?apiKey={API_KEY}",
        attr="Geoapify",
        overlay=False,
        control=True,
        max_zoom=20
    ).add_to(m)
    st_folium(m, width=850, height=500)
    st.success("Route visualized on map!")

if st.button("Clear Map 🧹"):
    st.session_state["route_geojson"] = None
    st.session_state["route_exists"] = False
    st.session_state["route_midpoint"] = None
    st.experimental_rerun()

# st.write("Choose by name, coordinates, or clicking on the map for instant Toronto routing. Powered by Geoapify + Streamlit.")
