import pandas as pd
import geopandas as gpd
import networkx as nx
import matplotlib.pyplot as plt
import folium
import folium.plugins as plugins
import random
from shapely.geometry import Point
import os
import webbrowser
import geopy.distance
import matplotlib.colors as mcolors
import branca.colormap as cm
import geopy.distance


# Data Preprocessing - implemented again in order to remove possible error-generating cells occured
def preprocess_data(filepath):
    bus_stops_data = pd.read_csv(filepath)
    bus_stops_data.fillna('', inplace=True)
    time_columns = [col for col in bus_stops_data.columns if 'Time' in col]
    bus_stops_data['Times'] = bus_stops_data[time_columns].apply(lambda row: [time for time in row if time != ''], axis=1)
    bus_stops_data.drop(columns=time_columns, inplace=True)
    bus_stops_data['Latitude'] = pd.to_numeric(bus_stops_data['Latitude'], errors='coerce')
    bus_stops_data['Longitude'] = pd.to_numeric(bus_stops_data['Longitude'], errors='coerce')
    return bus_stops_data

# Geospatial Analysis: Converts the bus stops data into a GeoDataFrame for spatial analysis.
#Purpose: This is essential for performing operations that take geographical locations into account.

def geospatial_analysis(bus_stops_data):
    geo_data = bus_stops_data.dropna(subset=['Latitude', 'Longitude'])
    geometry = [Point(xy) for xy in zip(geo_data['Longitude'], geo_data['Latitude'])]
    geo_df = gpd.GeoDataFrame(geo_data, geometry=geometry)
    return geo_df

# Network Analysis: Creates a network graph of bus stops and routes.
#Purpose: This allows us to understand and analyze the relationships and connectivity between different bus stops.

def create_network_graph(geo_df):
    G = nx.Graph()
    for index, row in geo_df.iterrows():
        G.add_node(row['Stop Name'], pos=(row['Longitude'], row['Latitude']))
    for route in geo_df['Route'].unique():
        route_stops = geo_df[geo_df['Route'] == route]['Stop Name'].tolist()
        route_edges = [(route_stops[i], route_stops[i + 1]) for i in range(len(route_stops) - 1)]
        G.add_edges_from(route_edges)
    return G

# Visualization of Network Graph: Visualizes the bus network with nodes and edges using different colors for each route.
#Purpose: This helps in visually understanding the structure and layout of the bus network.

def visualize_network(G, geo_df, title):
    pos = nx.get_node_attributes(G, 'pos')
    plt.figure(figsize=(15, 10))
    
    # Generate a color palette
    color_map = plt.cm.get_cmap('hsv', len(geo_df['Route'].unique()))
    
    for i, route in enumerate(geo_df['Route'].unique()):
        route_stops = geo_df[geo_df['Route'] == route]['Stop Name']
        route_color = color_map(i)
        nx.draw_networkx_nodes(G, pos, nodelist=route_stops, node_color=[route_color]*len(route_stops), label=route, node_size=100)
        nx.draw_networkx_edges(G, pos, edgelist=create_edges_for_route(G, route_stops), edge_color=route_color, width=2)

    nx.draw_networkx_labels(G, pos)
    plt.title(title)
    plt.legend()
    plt.show()


# Create Edges for Route: Helper function to create edges for a specific route in the network graph.
#Purpose: This supports the visualization by ensuring each route is represented accurately.

def create_edges_for_route(G, route_stops):
    return [(route_stops.iloc[i], route_stops.iloc[i+1]) for i in range(len(route_stops)-1) if G.has_edge(route_stops.iloc[i], route_stops.iloc[i+1])]

    
    
# Adjust Timetable for High-Demand Stops: Adjusts the bus timetable for stops with high demand.
#Purpose: Aimed at improving service frequency where it's needed most.

def adjust_timetable_for_high_demand(bus_stops_data):
    # Defining time_columns within the function
    time_columns = [col for col in bus_stops_data.columns if 'Time' in col]
    
    # Identifying high-demand stops (for example, stops with the most time entries)
    bus_stops_data['Total Times'] = bus_stops_data[time_columns].notna().sum(axis=1)
    high_demand_stops = bus_stops_data[bus_stops_data['Total Times'] > bus_stops_data['Total Times'].mean()]

    for index, row in high_demand_stops.iterrows():
        for i, time_col in enumerate(time_columns, start=1):
            if pd.isna(row[time_col]):
                # Adjust the following line to assign a more appropriate time
                bus_stops_data.at[index, time_col] = pd.Timestamp(f'2024-01-01 08:{30 * (i % 2):02d}')
    return bus_stops_data


# Visualization of Network Graph with Colored Nodes: Visualizes the network graph highlighting high and low connectivity nodes.
#Purpose: Helps in identifying critical nodes and potential areas for service improvement.
def visualize_network_with_colored_nodes(G, high_degree_nodes, low_degree_nodes, title):
    pos = nx.get_node_attributes(G, 'pos')
    plt.figure(figsize=(12, 8))
    nx.draw(G, pos, with_labels=True, node_size=50, node_color='lightblue', font_size=8)
    nx.draw_networkx_nodes(G, pos, nodelist=high_degree_nodes.keys(), node_color="red", node_size=100)
    nx.draw_networkx_nodes(G, pos, nodelist=low_degree_nodes, node_color="green", node_size=100)
    plt.title(title)
    plt.show()


# Merge Routes Function: Merges two bus routes into a new route in the network graph.
#Purpose: Used for optimizing the network by reducing redundancy and improving route efficiency.
def merge_routes(G, geo_df, route1, route2, new_route_name):
    stops_route1 = geo_df[geo_df['Route'] == route1]['Stop Name'].tolist()
    stops_route2 = geo_df[geo_df['Route'] == route2]['Stop Name'].tolist()
    combined_stops = list(set(stops_route1 + stops_route2))
    G.remove_nodes_from(stops_route1)
    G.remove_nodes_from(stops_route2)
    combined_edges = [(combined_stops[i], combined_stops[i + 1]) for i in range(len(combined_stops) - 1)]
    G.add_edges_from(combined_edges)
    print(f"Routes {route1} and {route2} merged into {new_route_name}")

# Identify High and Low Degree Nodes for Route Optimization: Identifies nodes in the network with high and low connectivity for optimization.
#Purpose: This analysis is crucial for enhancing the overall efficiency of the bus network.
def identify_optimization_nodes(G):
    high_degree_nodes = {node: degree for node, degree in G.degree() if degree > 2}
    low_degree_nodes = {node for node, degree in G.degree() if degree < 2}
    return high_degree_nodes, low_degree_nodes

# Visualization of Routes on Map: Visualizes bus routes on a map with different colors for each bus line.
#Purpose: Provides a geographic representation of the routes, making it easier to understand their real-world layout.
def visualize_routes_on_map(geo_df, G):
    bus_map = folium.Map(location=[geo_df['Latitude'].mean(), geo_df['Longitude'].mean()], zoom_start=12)
    colormap = cm.linear.Set1_09.scale(0, len(geo_df['Route'].unique()))
    
    for route in geo_df['Route'].unique():
        route_color = colormap(geo_df[geo_df['Route'] == route].index[0] % len(geo_df['Route'].unique()))
        route_stops = geo_df[geo_df['Route'] == route]
        for _, row in route_stops.iterrows():
            folium.CircleMarker(
                location=[row['Latitude'], row['Longitude']],
                radius=5,
                color=route_color,
                fill=True,
                fill_color=route_color,
                fill_opacity=0.7,
                popup=row['Stop Name']
            ).add_to(bus_map)
        for i in range(len(route_stops) - 1):
            stop1 = route_stops.iloc[i]
            stop2 = route_stops.iloc[i + 1]
            line = folium.PolyLine([stop1[['Latitude', 'Longitude']], stop2[['Latitude', 'Longitude']]], color=route_color, weight=2)
            bus_map.add_child(line)
    return bus_map

# Visualization of Optimized Routes: Visualizes optimized routes on a map, highlighting them with distinct colors based on optimization scores.
#Purpose: This allows us to see which routes have been optimized and understand the impact of optimizations.

def visualize_optimized_routes(geo_df, optimized_routes):
    optimized_route_map = visualize_routes_on_map(geo_df, G)
    colormap = cm.linear.YlGnBu_09.scale(0, max(optimized_routes.values()))
    colormap.caption = 'Optimization Score'
    optimized_route_map.add_child(colormap)
    
    for route, distance in optimized_routes.items():
        route_color = colormap(distance)
        route_stops = geo_df[geo_df['Route'] == route]
        route_points = [[row['Latitude'], row['Longitude']] for index, row in route_stops.iterrows()]
        folium.PolyLine(route_points, color=route_color, weight=3, opacity=1).add_to(optimized_route_map)
    return optimized_route_map

# Dynamic Routing Simulation: Simulates dynamic routing by increasing frequency on routes with high-demand stops.
#Purpose: Aims to enhance service responsiveness and adaptability in high-traffic areas.

def simulate_dynamic_routing(bus_stops_data, G):
    high_demand_stops = random.sample(bus_stops_data['Stop Name'].dropna().tolist(), 5)
    for stop in high_demand_stops:
        connected_routes = bus_stops_data[bus_stops_data['Stop Name'] == stop]['Route'].unique()
        for route in connected_routes:
            print(f"Increasing frequency of Route {route} to cover high-demand stop: {stop}")



# Calculate Distance: Calculates the geographical distance between two points.
#Purpose: Essential for route optimization algorithms that consider physical distances.

def calculate_distance(point1, point2):
    return geopy.distance.distance(point1, point2).km

# Optimize Routes by Distance: Optimizes bus routes based on the average distance between stops.
# Aims to make routes more efficient by minimizing unnecessary travel distance.
 
def optimize_routes_by_distance(G, geo_df):
    optimized_routes = {}
    for route in geo_df['Route'].unique():
        route_stops = geo_df[geo_df['Route'] == route]
        total_distance = 0
        for i in range(len(route_stops) - 1):
            stop1 = route_stops.iloc[i]
            stop2 = route_stops.iloc[i + 1]
            distance = calculate_distance((stop1['Latitude'], stop1['Longitude']), (stop2['Latitude'], stop2['Longitude']))
            total_distance += distance
        average_distance = total_distance / (len(route_stops) - 1)
        optimized_routes[route] = average_distance
    return optimized_routes

# Visualization of Heatmap: Creates a heatmap visualization of bus stops to show density.
#Purpose: Useful for identifying areas with high bus stop concentration and potential demand.
def visualize_heatmap(geo_df):
    heatmap_map = folium.Map(location=[geo_df['Latitude'].mean(), geo_df['Longitude'].mean()], zoom_start=12)
    heat_data = [[row['Latitude'], row['Longitude']] for index, row in geo_df.iterrows()]
    plugins.HeatMap(heat_data).add_to(heatmap_map)
    return heatmap_map




# Main Execution Block: The main block where all the functions are called to process data, create visualizations, and perform optimizations.
if __name__ == "__main__":
    filepath = 'data/all_routes_with_coords.csv'
    bus_stops_data = preprocess_data(filepath)
    geo_df = geospatial_analysis(bus_stops_data)
    G = create_network_graph(geo_df)
    optimized_routes = optimize_routes_by_distance(G, geo_df)
    
    # Route optimization by distance
    route_optimizations = optimize_routes_by_distance(G, geo_df)
    print("Route Optimizations by Distance:", route_optimizations)

    # Identify high and low degree nodes for route optimization
    high_degree_nodes, low_degree_nodes = identify_optimization_nodes(G)
    
    # Merge routes '31' and '33'
    merge_routes(G, geo_df, '31', '33', 'MergedRoute_31_33')
    
    # Visualization of network graph with color-coded routes
    visualize_network(G, geo_df, "Bus Network Graph with Color-coded Routes")


    # Visualize the network graph with colored nodes
    visualize_network_with_colored_nodes(G, high_degree_nodes, low_degree_nodes, "Adjusted Bus Network in Savona")

    # Adjust the timetable for high-demand stops
    adjusted_bus_stops_data = adjust_timetable_for_high_demand(bus_stops_data)

    # Visualize routes on Map with color-coded routes
    bus_map = visualize_routes_on_map(geo_df, G)
    bus_map.save("bus_routes_map.html")
    webbrowser.open("bus_routes_map.html", new=2)

    # Visualize optimized routes with highlighted optimization
    optimized_route_map = visualize_optimized_routes(geo_df, optimized_routes)
    optimized_route_map.save("optimized_routes_map.html")
    webbrowser.open("optimized_routes_map.html", new=2)



    # Simulate dynamic routing
    simulate_dynamic_routing(bus_stops_data, G)

    # Print adjusted timetable (for demonstration purposes)
    print(adjusted_bus_stops_data.head())
    
    # Heatmap bus stops visualization
    heatmap = visualize_heatmap(geo_df)
    heatmap.save("bus_stops_heatmap.html")
    webbrowser.open("bus_stops_heatmap.html", new=2)
   

   