# 🚲 SafeRoute AI – Toronto Interactive Routing

Find the best walking route in Toronto using real city maps, Geoapify Routing API, and a friendly UI. Pick route points by name, manual latitude/longitude, or click straight onto the map!

Check it out: [https://datathon-2025.streamlit.app/](https://datathon-2025.streamlit.app/)

***

## ✨ Features

A Streamlit app that recommends the safest walking route in Toronto using:
- Traffic collisions
- Crime data
- Cyclist injuries

Uses ML (KMeans + Logistic Regression), risk scoring, and NetworkX route optimization.

- **Input Modes:**
    - Popular Toronto location dropdown
    - Manual latitude/longitude entry
    - Select start/end points directly via map click
- **Live routing** via [Geoapify Routing API](https://apidocs.geoapify.com/docs/)
- Persistent interactive map (no more disappearing routes)
- Fully modern, mobile-friendly UI
- Labeled routes and real Toronto basemap (folium + streamlit-folium)

***

## 🚀 Quick Start

1. **Clone this repo**

```sh
git clone <your-repo-url>
cd <your-project-directory>
```

2. **Install required packages**

```sh
pip install streamlit requests folium streamlit-folium python-dotenv
```

3. **Get your free Geoapify API key**
    - Register at [Geoapify MyProjects](https://myprojects.geoapify.com/)
    - Put your key in `.env`:

```
API_KEY=your_actual_geoapify_api_key
```

4. **Run the app**

```sh
streamlit run streamlit_app.py
```


***

## 🕹️ Usage

1. Choose your input mode (dropdown, coordinates, map click)
2. If "Pick on Map", click anywhere, then use "Set as Start" or "Set as End" for the selected point
3. Press **Find Safe Route 🚦**
4. See your route instantly on a live, interactive map!
5. Map and route stay visible—use **Clear Map 🧹** to reset

***

## 🗂️ Structure

```
├── streamlit_app.py       # Main Streamlit app file
├── .env                   # (Not committed) Holds your API key
├── requirements.txt       # App dependencies
└── README.md              # This file
```


***

## 📦 Dependencies

- streamlit
- requests
- folium
- streamlit-folium
- python-dotenv

***

## 🔔 Notes

- Pre-loaded with Toronto’s most popular destinations for instant routing
- Easily extend for other cities, add more points, or change routing modes (`mode=drive|bike|walk`)
- Map state and routes persist until cleared; robust against reruns and UI changes

***

## 🏆 Credits

- Powered by [Geoapify Location Platform](https://apidocs.geoapify.com/docs/)
- Built with [Streamlit](https://streamlit.io)
- Toronto location data compiled by project contributors

***

## 📝 License

MIT – Open for personal, hackathon, and educational use

***

**Ready to route? Pick a location or click the map – get your Toronto path instantly!**

---
