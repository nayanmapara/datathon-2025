import folium

def create_route_map(path, risk_df):
    m = folium.Map(location=[43.6532, -79.3832], zoom_start=12)

    # Add risk points
    for _, row in risk_df.iterrows():
        folium.Circle(
            [row["lat"], row["lon"]],
            radius=20,
            color="red",
            weight=1,
            fill=True,
            fill_opacity=0.3
        ).add_to(m)

    # Add route polyline
    coords = [
        [risk_df.loc[int(node)]["lat"], risk_df.loc[int(node)]["lon"]]
        for node in path
    ]
    folium.PolyLine(coords, weight=5).add_to(m)

    return m._repr_html_()
