import streamlit as st
import folium
from streamlit_folium import folium_static

# --- Configurations ---
TOKEN_ID = "4bbc8e207d0f57ada1feaa78923d563262f901dc"  # Replace with your actual token

# --- Streamlit UI ---
st.title("Real-time Air Quality Map")
st.write("This app displays real-time air quality data using the AQICN Tile API.")

# --- Map Center ---
lat, lon = 51.505, -0.09  # Default: London (Change to your preferred location)
zoom_level = 11

# --- Create Folium Map ---
m = folium.Map(location=[lat, lon], zoom_start=zoom_level)

# --- AQI Tile Overlay ---
aqi_tile_url = f"https://tiles.aqicn.org/tiles/usepa-aqi/{{z}}/{{x}}/{{y}}.png?token={TOKEN_ID}"
folium.TileLayer(
    tiles=aqi_tile_url,
    attr='Air Quality Tiles &copy; <a href="http://waqi.info">waqi.info</a>',
    name="AQI Overlay",
).add_to(m)

# --- Add Layer Control ---
folium.LayerControl().add_to(m)

# --- Display Map in Streamlit ---
folium_static(m)
