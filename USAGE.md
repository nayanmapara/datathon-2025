# SafeRoute AI - Usage Guide

## Quick Start

### 1. Installation

First, install the required dependencies:

```bash
pip install -r requirements.txt
```

### 2. Running the Application

#### Option A: Interactive Streamlit App (Recommended)

Launch the web interface:

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

#### Option B: Command-Line Demo

Run the demo script to see the core functionality:

```bash
python3 demo.py
```

This will:
- Generate sample data
- Calculate risk scores
- Build a route network
- Find optimal routes
- Generate an HTML map at `/tmp/saferoute_demo_map.html`

## Using the Streamlit Interface

### Configuration Panel (Sidebar)

**Time of Day**
- Use the slider to select the current hour (0-23)
- Risk assessment adjusts based on time
- Example: Crime patterns differ between 2 AM and 2 PM

**Number of Locations**
- Controls the density of the route network
- Range: 20-150 locations
- More locations = more route options but slower processing

**Max Connection Distance**
- Maximum distance (in meters) between connected locations
- Range: 200-800 meters
- Higher values create more connected networks

### Selecting Routes

1. **Start Location**: Choose from the dropdown menu
   - Shows location ID and coordinates
   - Displays lighting score and risk level

2. **End Location**: Choose from available destinations
   - Excludes the start location
   - Shows safety information

3. **Find Route**: Click the "Find Safest Route" button

### Understanding Results

#### Route Comparison Metrics

- **Distance**: Total path length in meters
- **Risk Score**: Average safety score (0=safe, 1=dangerous)
- **Segments**: Number of path segments

#### Interactive Map

**Route Colors**:
- 🟢 **Green Line**: Safest route (recommended)
- 🔴 **Red Line**: Shortest route (may be less safe)

**Location Markers**:
- 🟢 **Green Dots**: Low-risk areas
- 🟠 **Orange Dots**: Medium-risk areas
- 🔴 **Red Dots**: High-risk areas

**Controls**:
- Click and drag to pan
- Scroll to zoom
- Click on routes/markers for details

#### Safety Recommendations

The app provides contextual safety advice based on the route's average risk score:

- **✅ Low Risk (<0.33)**: Safe to proceed
- **⚠️ Medium Risk (0.33-0.67)**: Stay alert, consider walking with others
- **🚨 High Risk (>0.67)**: Consider alternative transportation or timing

## Programming with SafeRoute AI

You can use SafeRoute AI's modules in your own Python scripts:

### Basic Example

```python
from data_loader import load_data, prepare_location_features
from risk_scorer import RiskScorer
from graph_builder import build_graph
from route_finder import RouteFinder

# Load data
locations_df, incidents_df = load_data()

# Prepare features for current time
features_df = prepare_location_features(locations_df, incidents_df, current_hour=14)

# Calculate risk scores
scorer = RiskScorer(n_clusters=3)
scorer.fit(features_df)
risk_scores = scorer.predict_risk_scores(features_df)

# Build network graph
graph = build_graph(locations_df, risk_scores, max_connection_distance=400)

# Find safest route
finder = RouteFinder(graph)
path = finder.find_safest_route(start_node=0, end_node=50)
route_info = finder.get_route_info(path)

print(f"Route distance: {route_info['total_distance']:.0f}m")
print(f"Average risk: {route_info['avg_risk_score']:.2f}")
```

### Creating Custom Maps

```python
from map_generator import create_route_comparison_map

# Get route coordinates
safest_coords = finder.get_route_coordinates(safest_path)
shortest_coords = finder.get_route_coordinates(shortest_path)

# Create map
route_map = create_route_comparison_map(
    safest_coords,
    shortest_coords,
    safest_info,
    shortest_info,
    locations_df,
    risk_scores
)

# Save to file
route_map.save('my_route_map.html')
```

## Data Model

### Location Data Structure

Each location has:
- `location_id`: Unique identifier
- `latitude`, `longitude`: Geographic coordinates
- `lighting_score`: Quality of lighting (0-1)

### Incident Data Structure

Each crime incident has:
- `incident_id`: Unique identifier
- `location_id`: Where it occurred
- `hour`: Time of day (0-23)
- `crime_severity`: 'low', 'medium', or 'high'

### Feature Engineering

The system automatically creates these features:
- `total_incidents`: All crimes at location
- `high_severity_count`: Number of serious crimes
- `recent_incidents`: Crimes within time window

## Algorithm Details

### Risk Scoring

1. **KMeans Clustering**: Groups locations into risk categories
2. **Logistic Regression**: Predicts high-risk probability
3. **Combined Score**: Weighted average (60% cluster, 40% probability)
4. **Lighting Adjustment**: Poor lighting increases risk score

### Route Finding

1. **Graph Construction**: Locations are nodes, paths are edges
2. **Edge Weights**: `distance × (1 + risk_factor)`
3. **Pathfinding**: Dijkstra's algorithm minimizes total weight
4. **Comparison**: Also calculates shortest distance-only route

## Tips and Best Practices

### For Best Results

1. **Adjust Time**: Set the hour to match when you'll be walking
2. **Increase Density**: More locations provide better route options
3. **Connection Distance**: If routes aren't found, increase max distance
4. **Compare Routes**: Always review the trade-off between distance and safety

### Understanding Trade-offs

- A safer route may be slightly longer
- The app shows the extra distance and risk reduction
- Consider your comfort level and time constraints
- In unfamiliar areas, prioritize safety over distance

### Limitations

⚠️ **This is demonstration software**:
- Uses simulated data
- Real-world applications need actual crime databases
- Cannot predict all risks
- Should be one of multiple safety considerations

## Troubleshooting

### "No route found between selected locations"

**Cause**: Locations are in disconnected network components

**Solutions**:
- Increase "Max connection distance" in settings
- Reduce "Number of locations" for denser networks
- Try different start/end locations
- The app will suggest connected alternatives

### Application runs slowly

**Cause**: Too many locations or connections

**Solutions**:
- Reduce number of locations to 50-80
- Decrease max connection distance
- Close other applications

### Import errors

**Cause**: Missing dependencies

**Solution**:
```bash
pip install -r requirements.txt --upgrade
```

## Advanced Usage

### Custom Data Sources

To use your own data, modify `data_loader.py`:

```python
def load_data():
    # Replace with your data loading logic
    locations_df = pd.read_csv('your_locations.csv')
    incidents_df = pd.read_csv('your_incidents.csv')
    return locations_df, incidents_df
```

Required columns:
- Locations: `location_id`, `latitude`, `longitude`, `lighting_score`
- Incidents: `location_id`, `hour`, `crime_severity`

### Tuning the Risk Model

Adjust the risk scorer in `risk_scorer.py`:

```python
# Change number of risk categories
scorer = RiskScorer(n_clusters=5)  # More granular risk levels

# Adjust weight balance in predict_risk_scores()
final_scores = 0.7 * cluster_risks + 0.3 * risk_probs  # Prefer clusters
```

### Custom Edge Weights

Modify the graph builder to emphasize different factors:

```python
# In graph_builder.py, build_graph()
risk_multiplier = 1 + (avg_risk * 3.0)  # Stronger risk penalty
edge_weight = distance * risk_multiplier
```

## API Reference

See individual module files for detailed API documentation:

- `data_loader.py`: Data loading and preparation
- `risk_scorer.py`: ML-based risk assessment
- `graph_builder.py`: Network graph construction
- `route_finder.py`: Pathfinding algorithms
- `map_generator.py`: Visualization functions

Each function includes docstrings with parameter descriptions and return types.

## Support

For issues, questions, or contributions:
- GitHub Issues: [Report a problem](https://github.com/nayanmapara/datathon-2025/issues)
- Pull Requests: Contributions welcome!

## License

Educational and demonstration purposes. See repository for details.
