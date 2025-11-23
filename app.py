"""
SafeRoute AI - Streamlit Application
Finds the safest walking route using crime, lighting, and time data.
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# Import custom modules
from data_loader import prepare_location_features
from risk_scorer import RiskScorer
from graph_builder import build_graph, get_graph_stats
from route_finder import RouteFinder
from map_generator import create_route_comparison_map


def main():
    """Main application function."""
    
    # Page configuration
    st.set_page_config(
        page_title="SafeRoute AI",
        page_icon="🛡️",
        layout="wide"
    )
    
    # Title and description
    st.title("🛡️ SafeRoute AI")
    st.markdown("""
    **Find the safest walking route based on crime data, lighting conditions, and time of day.**
    
    SafeRoute AI uses machine learning (KMeans clustering + Logistic Regression) to assess 
    location risk and NetworkX for intelligent pathfinding.
    """)
    
    # Sidebar for configuration
    st.sidebar.header("⚙️ Configuration")
    
    # Time selection
    current_hour = st.sidebar.slider(
        "Select time of day (hour)",
        min_value=0,
        max_value=23,
        value=datetime.now().hour,
        help="Risk assessment varies by time of day"
    )
    
    # Number of locations
    num_locations = st.sidebar.slider(
        "Number of locations",
        min_value=20,
        max_value=150,
        value=80,
        step=10,
        help="More locations = more detailed network but slower processing"
    )
    
    # Max connection distance
    max_distance = st.sidebar.slider(
        "Max connection distance (meters)",
        min_value=200,
        max_value=800,
        value=400,
        step=50,
        help="Maximum distance to connect nearby locations"
    )
    
    # Load and process data
    with st.spinner("Loading data and building safety network..."):
        try:
            # Load data
            from data_loader import generate_sample_data
            locations_df, incidents_df = generate_sample_data(num_locations)
            
            # Prepare features
            features_df = prepare_location_features(locations_df, incidents_df, current_hour)
            
            # Calculate risk scores
            risk_scorer = RiskScorer(n_clusters=3)
            risk_scorer.fit(features_df)
            risk_scores = risk_scorer.predict_risk_scores(features_df)
            
            # Build graph
            graph = build_graph(locations_df, risk_scores, max_distance)
            graph_stats = get_graph_stats(graph)
            
            # Store in session state
            st.session_state['locations_df'] = locations_df
            st.session_state['risk_scores'] = risk_scores
            st.session_state['graph'] = graph
            st.session_state['graph_stats'] = graph_stats
            
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
            return
    
    # Display network statistics
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Network Statistics")
    st.sidebar.write(f"**Nodes:** {graph_stats['num_nodes']}")
    st.sidebar.write(f"**Edges:** {graph_stats['num_edges']}")
    st.sidebar.write(f"**Connected:** {'✅' if graph_stats['is_connected'] else '❌'}")
    st.sidebar.write(f"**Avg Connections:** {graph_stats['avg_degree']:.1f}")
    
    # Main content area
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📍 Select Start Location")
        
        # Get random locations for selection
        sample_locations = locations_df.sample(min(10, len(locations_df)))
        
        start_options = {
            f"Location {row['location_id']} ({row['latitude']:.4f}, {row['longitude']:.4f})": row['location_id']
            for _, row in sample_locations.iterrows()
        }
        
        selected_start = st.selectbox(
            "Start point",
            options=list(start_options.keys()),
            key="start_select"
        )
        start_node = start_options[selected_start]
        
        # Display start location info
        start_info = locations_df[locations_df['location_id'] == start_node].iloc[0]
        st.info(f"""
        **Lighting Score:** {start_info['lighting_score']:.2f}  
        **Risk Score:** {risk_scores[start_node]:.2f} ({risk_scorer.get_risk_category(risk_scores[start_node])})
        """)
    
    with col2:
        st.subheader("🎯 Select End Location")
        
        # Filter out start location
        end_sample = sample_locations[sample_locations['location_id'] != start_node]
        
        end_options = {
            f"Location {row['location_id']} ({row['latitude']:.4f}, {row['longitude']:.4f})": row['location_id']
            for _, row in end_sample.iterrows()
        }
        
        selected_end = st.selectbox(
            "End point",
            options=list(end_options.keys()),
            key="end_select"
        )
        end_node = end_options[selected_end]
        
        # Display end location info
        end_info = locations_df[locations_df['location_id'] == end_node].iloc[0]
        st.info(f"""
        **Lighting Score:** {end_info['lighting_score']:.2f}  
        **Risk Score:** {risk_scores[end_node]:.2f} ({risk_scorer.get_risk_category(risk_scores[end_node])})
        """)
    
    # Find routes button
    if st.button("🔍 Find Safest Route", type="primary", use_container_width=True):
        with st.spinner("Calculating optimal routes..."):
            try:
                # Initialize route finder
                route_finder = RouteFinder(graph)
                
                # Find safest route
                safest_path = route_finder.find_safest_route(start_node, end_node)
                
                # Find shortest route for comparison
                shortest_path = route_finder.find_shortest_route(start_node, end_node)
                
                if safest_path is None:
                    st.error("❌ No route found between selected locations. Try different locations or increase max connection distance.")
                    return
                
                # Get route information
                safest_info = route_finder.get_route_info(safest_path)
                shortest_info = route_finder.get_route_info(shortest_path) if shortest_path else {}
                
                # Get coordinates
                safest_coords = route_finder.get_route_coordinates(safest_path)
                shortest_coords = route_finder.get_route_coordinates(shortest_path) if shortest_path else []
                
                # Display route comparison
                st.markdown("---")
                st.subheader("📊 Route Comparison")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "Safest Route Distance",
                        f"{safest_info['total_distance']:.0f}m",
                        delta=f"{safest_info['total_distance'] - shortest_info.get('total_distance', 0):.0f}m" if shortest_path else None,
                        delta_color="off"
                    )
                
                with col2:
                    st.metric(
                        "Safest Route Risk",
                        f"{safest_info['avg_risk_score']:.2f}",
                        delta=f"{safest_info['avg_risk_score'] - shortest_info.get('avg_risk_score', 0):.2f}" if shortest_path else None,
                        delta_color="inverse"
                    )
                
                with col3:
                    st.metric(
                        "Number of Segments",
                        f"{safest_info['num_segments']}",
                        delta=f"{safest_info['num_segments'] - shortest_info.get('num_segments', 0)}" if shortest_path else None,
                        delta_color="off"
                    )
                
                # Display route details
                with st.expander("📋 Detailed Route Information"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**🛡️ Safest Route**")
                        st.write(f"- Distance: {safest_info['total_distance']:.1f} meters")
                        st.write(f"- Average Risk: {safest_info['avg_risk_score']:.3f}")
                        st.write(f"- Segments: {safest_info['num_segments']}")
                        st.write(f"- Path: {' → '.join(map(str, safest_path))}")
                    
                    if shortest_path:
                        with col2:
                            st.write("**⚡ Shortest Route**")
                            st.write(f"- Distance: {shortest_info['total_distance']:.1f} meters")
                            st.write(f"- Average Risk: {shortest_info['avg_risk_score']:.3f}")
                            st.write(f"- Segments: {shortest_info['num_segments']}")
                            st.write(f"- Path: {' → '.join(map(str, shortest_path))}")
                
                # Generate and display map
                st.markdown("---")
                st.subheader("🗺️ Interactive Route Map")
                
                route_map = create_route_comparison_map(
                    safest_coords,
                    shortest_coords,
                    safest_info,
                    shortest_info,
                    locations_df,
                    risk_scores
                )
                
                # Display map
                st.components.v1.html(route_map._repr_html_(), height=600)
                
                # Safety recommendations
                st.markdown("---")
                st.subheader("💡 Safety Recommendations")
                
                avg_risk = safest_info['avg_risk_score']
                
                if avg_risk < 0.33:
                    st.success("✅ This route is relatively safe. Enjoy your walk!")
                elif avg_risk < 0.67:
                    st.warning("⚠️ This route has moderate risk. Stay alert and consider walking with others.")
                else:
                    st.error("⚠️ This route has elevated risk. Consider alternative transportation or wait for daylight hours.")
                
                # Additional tips
                with st.expander("🔒 General Safety Tips"):
                    st.markdown("""
                    - **Stay Aware**: Keep your phone charged and stay alert to your surroundings
                    - **Share Location**: Let someone know your route and expected arrival time
                    - **Lighting**: Stick to well-lit areas whenever possible
                    - **Trust Instincts**: If something feels wrong, find an alternative route
                    - **Emergency**: Keep emergency contacts readily accessible
                    """)
                
            except Exception as e:
                st.error(f"Error calculating route: {str(e)}")
                import traceback
                st.error(traceback.format_exc())
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray;'>
    <p>SafeRoute AI | Built with Streamlit, scikit-learn, NetworkX, and Folium</p>
    <p>⚠️ This is a demonstration app. Always prioritize your personal safety.</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
