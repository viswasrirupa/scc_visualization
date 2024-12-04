'''
Created Dec 3, 2024. 
Authors: Viswa Sri Rupa Anne
'''

import streamlit as st
import pandas as pd
import folium
import requests
from streamlit_folium import st_folium

# Load data
ptc_network = pd.read_csv('Network.csv')
traffic_accidents = pd.read_csv('TrafficAccident.csv')
route_10A = pd.read_csv('Route10A.csv')
route_10B = pd.read_csv('Route10B.csv')
route_35 = pd.read_csv('Route35.csv')
route_35F1 = pd.read_csv('Route35F1.csv')

# Setup API endpoint for live data.
# API endpoint base URL (replace with the actual API endpoint URL)
API_URL_BASE = "http://realtimegwinnett.availtec.com/infopoint/rest/vehicles/getallvehiclesforroute?routeID={route}"

# Function to fetch live bus data
def fetch_live_bus_data(route_id):
    try:
        url = API_URL_BASE.format(route=route_id)
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for HTTP errors
        return response.json()  # Assuming the API returns a JSON response
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching live bus data for Route {route_id}: {e}")
        return []


# Set up the sidebar
st.sidebar.image('images/ptc_logo.png', caption='Peachtree Corners', width=100)
st.sidebar.image('images/nsf_scc_logo.jpg', caption='NSF Smart and Connected Communities', width=100)

st.sidebar.title("Dynamic Visualization Platform")
st.sidebar.write("""
This platform is designed for the City of Peachtree Corners to facilitate data-driven decision-making in transportation. 
It offers multiple data layers for insights and analysis, empowering stakeholders to make informed decisions.
""")
st.sidebar.markdown("### Data Layers")

# Button states
if "network_layer" not in st.session_state:
    st.session_state.network_layer = False
if "traffic_accidents" not in st.session_state:
    st.session_state.traffic_accidents = False
if "transit_layer" not in st.session_state:
    st.session_state.transit_layer = False

# Network Layer Button
if st.sidebar.button("Peachtree Corners Network Layer"):
    st.session_state.network_layer = not st.session_state.network_layer
if st.session_state.network_layer:
    st.sidebar.write("Network layer is active: showing transportation networks in Peachtree Corners.")

# Traffic Accidents Button
if st.sidebar.button("Traffic Accidents Layer"):
    st.session_state.traffic_accidents = not st.session_state.traffic_accidents
if st.session_state.traffic_accidents:
    st.sidebar.write("Traffic accidents layer is active: visualizing traffic accident hotspots.")

# Transit Layer Button
if "transit_layer" not in st.session_state:
    st.session_state.transit_layer = False

if st.sidebar.button("Gwinnett Transit Locations and Stops Layer"):
    st.session_state.transit_layer = not st.session_state.transit_layer

if st.session_state.transit_layer:
    st.sidebar.write("Transit layer is active: showing Gwinnett transit stops and locations.")
    st.sidebar.markdown("#### Routes in PTC")
    # Transit Route Checkboxes
    route_10A_toggle = st.sidebar.checkbox("Display Route 10A")
    route_10B_toggle = st.sidebar.checkbox("Display Route 10B")
    route_35_toggle = st.sidebar.checkbox("Display Route 35")
    route_35F1_toggle = st.sidebar.checkbox("Display Route 35F1")

    # Sidebar dropdown for live bus tracking
    bus_routes = ["10", "35"]  # Add the available route IDs
    selected_route = st.sidebar.selectbox("Select a Route to Track Live Buses", bus_routes, index=1)  # Default to Route 35

    # Dropdown for available buses (fetched dynamically)
    buses_data = fetch_live_bus_data(selected_route)
    bus_ids = [bus.get("BlockFareboxId", f"Bus {i+1}") for i, bus in enumerate(buses_data)]
    selected_bus = st.sidebar.selectbox("Select a Bus to Track", bus_ids)

# Sidebar team section
st.sidebar.markdown("### Team")
st.sidebar.write("""
- **Authors:** Rupa Anne, Yufei Xu
- For inquiries, contact: [actlab@ce.gatech.edu](mailto:actlab@ce.gatech.edu)
""")

# Display Data on Main View
st.title("Dynamic Visualization Platform for Peachtree Corners")

if st.session_state.transit_layer:
    st.write(f"Tracking live data for Route: {selected_route}, Bus: {selected_bus}")

# Create map
map_center = [33.9696, -84.2216]  # Approximate center of Peachtree Corners
m = folium.Map(location=map_center, zoom_start=12)

# Add network layer
if st.session_state.network_layer:
    for _, row in ptc_network.iterrows():
        folium.PolyLine(
            locations=[[row["Start Lat"], row["Start Long"]], [row["End Lat"], row["End Long"]]],
            color="blue",
            weight=2,
            opacity=0.7
        ).add_to(m)

# Add traffic accidents layer
if st.session_state.traffic_accidents:
    for _, row in traffic_accidents.iterrows():
        folium.CircleMarker(
            location=[row["StartLat"], row["StartLong"]],
            radius=5,
            color="red",
            fill=True,
            fill_opacity=0.6
        ).add_to(m)

# Add transit routes
if st.session_state.transit_layer:
    if route_10A_toggle:
        folium.PolyLine(
            locations=route_10A[["Lat", "Log"]].values.tolist(),
            color="blue",
            weight=3,
            opacity=0.8,
            tooltip="Route 10A"
        ).add_to(m)
    if route_10B_toggle:
        folium.PolyLine(
            locations=route_10B[["Lat", "Log"]].values.tolist(),
            color="green",
            weight=3,
            opacity=0.8,
            tooltip="Route 10B"
        ).add_to(m)
    if route_35_toggle:
        folium.PolyLine(
            locations=route_35[["Lat", "Log"]].values.tolist(),
            color="red",
            weight=3,
            opacity=0.8,
            tooltip="Route 35"
        ).add_to(m)
    if route_35F1_toggle:
        folium.PolyLine(
            locations=route_35F1[["Lat", "Log"]].values.tolist(),
            color="purple",
            weight=3,
            opacity=0.8,
            tooltip="Route 35F1"
        ).add_to(m)

    # Add selected bus location to the map
    for bus in buses_data:
        if str(bus.get("BlockFareboxId")) == str(selected_bus):
            bus_lat = bus.get("Latitude")
            bus_lon = bus.get("Longitude")
            destination = bus.get("Destination", "Unknown Destination")
            heading = bus.get("Heading", "Unknown Heading")
        
            if bus_lat and bus_lon:
                folium.Marker(
                    location=[bus_lat, bus_lon],
                    popup=f"Bus ID: {selected_bus}<br>Destination: {destination}<br>Heading: {heading}",
                    icon=folium.Icon(color="blue", icon="bus", prefix="fa"),
                ).add_to(m)


# Render the map
st_data = st_folium(m, width=700, height=500)