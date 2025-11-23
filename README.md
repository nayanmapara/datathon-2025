# SafeRoute AI 🛡️

A Streamlit application that finds the safest walking route using crime data, lighting conditions, and time-of-day analysis. SafeRoute AI combines machine learning with graph-based pathfinding to help users navigate urban environments more safely.

## Features

- 🤖 **Machine Learning Risk Assessment**: Uses KMeans clustering and Logistic Regression to evaluate location safety
- 🗺️ **Intelligent Pathfinding**: Leverages NetworkX for weighted graph-based route optimization
- 📊 **Interactive Visualization**: Beautiful route maps with Folium
- ⏰ **Time-Aware Analysis**: Risk scores adjust based on time of day
- 💡 **Lighting Consideration**: Factors in street lighting quality
- 📈 **Route Comparison**: Compare safest route vs. shortest route

## Architecture

The application follows a modular design:

### Modules

1. **data_loader.py**: Data loading and feature preparation
   - Generates sample crime, lighting, and time data
   - Prepares location features for ML models

2. **risk_scorer.py**: Risk assessment using machine learning
   - KMeans clustering for risk categorization
   - Logistic Regression for risk probability
   - Combined scoring with lighting adjustment

3. **graph_builder.py**: Network graph construction
   - Builds weighted graph with NetworkX
   - Calculates distances between locations
   - Assigns edge weights based on distance and risk

4. **route_finder.py**: Pathfinding algorithms
   - Dijkstra's algorithm for safest route
   - Alternative shortest path calculation
   - Route statistics and comparison

5. **map_generator.py**: Interactive map visualization
   - Creates Folium maps with routes
   - Adds risk heatmap overlay
   - Displays route comparison

6. **app.py**: Main Streamlit application
   - User interface and interaction
   - Orchestrates all modules
   - Displays results and recommendations

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone https://github.com/nayanmapara/datathon-2025.git
cd datathon-2025
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the Streamlit application:

```bash
streamlit run app.py
```

The app will open in your default web browser at `http://localhost:8501`.

### Using the Application

1. **Configure Settings** (Sidebar):
   - Select time of day (0-23 hours)
   - Adjust number of locations (20-150)
   - Set max connection distance (200-800 meters)

2. **Select Locations**:
   - Choose a start location from the dropdown
   - Choose an end location from the dropdown

3. **Find Route**:
   - Click "Find Safest Route" button
   - View route comparison metrics
   - Explore interactive map
   - Review safety recommendations

### Understanding the Results

- **Green Route**: Safest path (minimizes risk exposure)
- **Red Route**: Shortest path (minimizes distance only)
- **Colored Dots**: Location risk levels
  - 🟢 Green: Low risk
  - 🟠 Orange: Medium risk
  - 🔴 Red: High risk

## Technical Details

### Machine Learning Models

**KMeans Clustering**:
- Groups locations into risk clusters (low, medium, high)
- Uses features: lighting score, total incidents, high severity count, recent incidents

**Logistic Regression**:
- Predicts probability of high-risk areas
- Provides continuous risk scores

**Combined Risk Scoring**:
- 60% cluster-based risk
- 40% probability-based risk
- Adjusted for lighting conditions

### Graph-Based Pathfinding

- **Nodes**: Geographic locations with risk scores
- **Edges**: Weighted connections between nearby locations
- **Edge Weight**: `distance × (1 + risk_factor)`
- **Algorithm**: Dijkstra's shortest path on weighted graph

### Data Model

**Location Features**:
- Geographic coordinates (latitude, longitude)
- Lighting score (0-1)
- Total crime incidents
- High severity incident count
- Recent incidents (time-filtered)

## Dependencies

- **streamlit**: Web application framework
- **pandas**: Data manipulation and analysis
- **scikit-learn**: Machine learning (KMeans, Logistic Regression)
- **networkx**: Graph-based pathfinding
- **folium**: Interactive map visualization
- **numpy**: Numerical computations

## Project Structure

```
datathon-2025/
├── app.py                 # Main Streamlit application
├── data_loader.py         # Data loading and preparation
├── risk_scorer.py         # ML-based risk assessment
├── graph_builder.py       # Network graph construction
├── route_finder.py        # Pathfinding algorithms
├── map_generator.py       # Map visualization
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Future Enhancements

- Integration with real crime databases
- Real-time lighting condition updates
- Historical trend analysis
- Mobile app version
- Multi-modal transportation options
- Community-reported incidents
- Weather condition integration

## Safety Disclaimer

⚠️ **Important**: This is a demonstration application using simulated data. While the algorithms and methodology are sound, always prioritize your personal safety and use multiple sources of information when planning routes in unfamiliar areas.

## License

This project is created for educational and demonstration purposes.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Author

Created for Datathon 2025