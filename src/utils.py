def parse_point(text):
    lat, lon = text.split(",")
    return float(lat), float(lon)
