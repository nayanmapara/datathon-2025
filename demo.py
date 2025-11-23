"""
Demo script to test the SafeRoute AI functionality without Streamlit UI.
This demonstrates the complete workflow of the application.
"""

import os
import tempfile
from data_loader import generate_sample_data, prepare_location_features
from risk_scorer import RiskScorer
from graph_builder import build_graph, get_graph_stats
from route_finder import RouteFinder
from map_generator import create_route_comparison_map


def main():
    """Main demo function."""
    
    print("🛡️ SafeRoute AI - Demo Script")
    print("=" * 60)
    
    # Step 1: Load data
    print("\n1️⃣ Loading data...")
    locations_df, incidents_df = generate_sample_data(num_locations=80)
    print(f"   ✓ Generated {len(locations_df)} locations")
    print(f"   ✓ Generated {len(incidents_df)} crime incidents")
    
    # Step 2: Prepare features
    print("\n2️⃣ Preparing location features...")
    current_hour = 20  # 8 PM
    features_df = prepare_location_features(locations_df, incidents_df, current_hour)
    print(f"   ✓ Features prepared for time: {current_hour}:00")
    print(f"   ✓ Feature columns: {list(features_df.columns)}")
    
    # Step 3: Calculate risk scores
    print("\n3️⃣ Calculating risk scores using ML...")
    risk_scorer = RiskScorer(n_clusters=3)
    risk_scorer.fit(features_df)
    risk_scores = risk_scorer.predict_risk_scores(features_df)
    print(f"   ✓ Risk scores calculated")
    print(f"   ✓ Min risk: {risk_scores.min():.3f}")
    print(f"   ✓ Max risk: {risk_scores.max():.3f}")
    print(f"   ✓ Average risk: {risk_scores.mean():.3f}")
    
    # Show risk distribution
    low_risk = (risk_scores < 0.33).sum()
    med_risk = ((risk_scores >= 0.33) & (risk_scores < 0.67)).sum()
    high_risk = (risk_scores >= 0.67).sum()
    print(f"   ✓ Risk distribution: Low={low_risk}, Medium={med_risk}, High={high_risk}")
    
    # Step 4: Build graph
    print("\n4️⃣ Building network graph...")
    graph = build_graph(locations_df, risk_scores, max_connection_distance=500.0)
    stats = get_graph_stats(graph)
    print(f"   ✓ Graph built with {stats['num_nodes']} nodes and {stats['num_edges']} edges")
    print(f"   ✓ Graph is connected: {stats['is_connected']}")
    print(f"   ✓ Average degree: {stats['avg_degree']:.2f}")
    
    # Step 5: Find routes
    print("\n5️⃣ Finding optimal routes...")
    route_finder = RouteFinder(graph)
    
    # Select start and end nodes
    start_node = 5
    end_node = 50
    
    print(f"   ✓ Start location: {start_node}")
    print(f"   ✓ End location: {end_node}")
    
    # Find safest route
    safest_path = route_finder.find_safest_route(start_node, end_node)
    
    if safest_path is None:
        print("   ❌ No route found (nodes not connected)")
        # Try to find connected nodes
        import networkx as nx
        components = list(nx.connected_components(graph))
        if len(components) > 0:
            largest_component = max(components, key=len)
            nodes = list(largest_component)
            if len(nodes) >= 2:
                start_node = nodes[0]
                end_node = nodes[min(10, len(nodes)-1)]
                print(f"   ℹ️ Retrying with connected nodes: {start_node} → {end_node}")
                safest_path = route_finder.find_safest_route(start_node, end_node)
    
    if safest_path:
        shortest_path = route_finder.find_shortest_route(start_node, end_node)
        
        safest_info = route_finder.get_route_info(safest_path)
        shortest_info = route_finder.get_route_info(shortest_path)
        
        print(f"\n   🛡️ SAFEST ROUTE:")
        print(f"      Distance: {safest_info['total_distance']:.1f} meters")
        print(f"      Average Risk: {safest_info['avg_risk_score']:.3f}")
        print(f"      Segments: {safest_info['num_segments']}")
        print(f"      Path: {' → '.join(map(str, safest_path))}")
        
        print(f"\n   ⚡ SHORTEST ROUTE:")
        print(f"      Distance: {shortest_info['total_distance']:.1f} meters")
        print(f"      Average Risk: {shortest_info['avg_risk_score']:.3f}")
        print(f"      Segments: {shortest_info['num_segments']}")
        print(f"      Path: {' → '.join(map(str, shortest_path))}")
        
        # Calculate trade-offs
        extra_distance = safest_info['total_distance'] - shortest_info['total_distance']
        risk_reduction = shortest_info['avg_risk_score'] - safest_info['avg_risk_score']
        
        print(f"\n   📊 TRADE-OFF ANALYSIS:")
        print(f"      Extra distance for safer route: {extra_distance:.1f} meters", end="")
        if shortest_info['total_distance'] > 0:
            print(f" ({extra_distance/shortest_info['total_distance']*100:.1f}%)")
        else:
            print()
        print(f"      Risk reduction: {risk_reduction:.3f}", end="")
        if shortest_info['avg_risk_score'] > 0:
            print(f" ({risk_reduction/shortest_info['avg_risk_score']*100:.1f}%)")
        else:
            print()
        
        # Step 6: Generate map
        print("\n6️⃣ Generating interactive map...")
        safest_coords = route_finder.get_route_coordinates(safest_path)
        shortest_coords = route_finder.get_route_coordinates(shortest_path)
        
        route_map = create_route_comparison_map(
            safest_coords,
            shortest_coords,
            safest_info,
            shortest_info,
            locations_df,
            risk_scores
        )
        
        # Save map
        map_filename = os.path.join(tempfile.gettempdir(), 'saferoute_demo_map.html')
        route_map.save(map_filename)
        print(f"   ✓ Map saved to: {map_filename}")
        
        # Safety recommendation
        print("\n7️⃣ Safety recommendation:")
        avg_risk = safest_info['avg_risk_score']
        if avg_risk < 0.33:
            print("   ✅ This route is relatively SAFE")
        elif avg_risk < 0.67:
            print("   ⚠️ This route has MODERATE risk - stay alert")
        else:
            print("   🚨 This route has ELEVATED risk - consider alternatives")
    else:
        print("   ❌ Unable to find a route between any connected nodes")
    
    print("\n" + "=" * 60)
    print("✅ Demo completed successfully!")
    print("\n💡 To run the interactive Streamlit app:")
    print("   streamlit run app.py")


if __name__ == "__main__":
    main()
