import os
import json
import pickle
import pandas as pd
import streamlit as st
import altair as alt
from datetime import datetime
from weather import fetch_weather_data, interpret_weather_code
from src.pipeline.prediction_pipeline import recursive_forecast

# ----------------------- Model Loading -----------------------
def load_best_model(artifacts_dir="artifacts/"):
    results_path = os.path.join(artifacts_dir, "model_results.json")

    if not os.path.exists(results_path):
        st.error("model_results.json not found in artifacts/")
        return None

    with open(results_path, "r") as file:
        try:
            results = json.load(file)
        except json.JSONDecodeError:
            st.error("Error decoding JSON.")
            return None

    best_model_name = min(results, key=lambda x: results[x].get("mae", float("inf")))
    best_model_info = results[best_model_name]
    best_model_path = best_model_info.get("model_path", "")

    if not best_model_path or not os.path.exists(best_model_path):
        st.error(f"Model file not found: {best_model_path}")
        return None

    with open(best_model_path, "rb") as model_file:
        return pickle.load(model_file)

# ----------------------- Data Loading -----------------------
def load_data(hour, aqi_filepath='artifacts/test.csv', pollutants_filepath='artifacts/test_pollutants.csv'):
    try:
        aqi_df = pd.read_csv(aqi_filepath)
        poll_df = pd.read_csv(pollutants_filepath)

        aqi_data = aqi_df[hour-1:hour+13].copy()
        poll_data = poll_df.iloc[hour+12:hour+13].copy()

        return aqi_data, poll_data
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None, None

# ----------------------- AQI Category -----------------------
def get_aqi_category(aqi):
    if aqi <= 50:
        return "Good", "🟢", "#2ECC71"
    elif aqi <= 100:
        return "Moderate", "🟡", "#F1C40F"
    else:
        return "Unhealthy", "🔴", "#E74C3C"

# ----------------------- Visualization -----------------------
def render_graph(data):
    model = load_best_model()
    if model is None:
        return

    data["hour"] = data["hour"].astype(int)
    data['AQI'] = data['Value']
    data = data.drop('Value', axis=1)

    last = data.drop('AQI', axis=1).iloc[-1]
    predictions = recursive_forecast(model, last, n_steps=7)

    observed_hours = list(data["hour"])
    predicted_hours = [(h % 24 if h % 24 != 0 else 24) for h in range(observed_hours[-1] + 1, observed_hours[-1] + 8)]

    observed_df = pd.DataFrame({"hour": observed_hours, "AQI": data["AQI"], "segment": "Observed"})
    predicted_df = pd.DataFrame({"hour": predicted_hours, "AQI": predictions, "segment": "Predicted"})

    first_predicted = pd.DataFrame({"hour": [observed_hours[-1]], "AQI": [data["AQI"].iloc[-1]], "segment": "Predicted"})
    predicted_df = pd.concat([first_predicted, predicted_df])

    full_df = pd.concat([observed_df, predicted_df])

    correct_order = observed_hours + predicted_hours
    full_df["hour"] = pd.Categorical(full_df["hour"], categories=correct_order, ordered=True)

    chart = (
        alt.Chart(full_df)
        .mark_line(point=True, strokeWidth=3)
        .encode(
            x=alt.X("hour:O", title="Time (hours)", sort=correct_order),
            y=alt.Y("AQI:Q", title="AQI"),
            color=alt.Color("segment", scale=alt.Scale(domain=["Observed", "Predicted"], range=["#6baed6", "#fb6a4a"]), title="AQI"),
            strokeDash=alt.condition(
                alt.datum.segment == "Predicted",
                alt.value([5, 5]),
                alt.value([0])
            )
        )
    )
    st.altair_chart(chart, use_container_width=True)

# ----------------------- Pollutants Data Display -----------------------
def show_pollutants(data):
    pollutants = {"PM2.5": 50, "PM10": 100, "NO2": 40, "SO2": 20, "CO": 10, "O3": 60}
    latest_values = data.iloc[-1:]

    st.subheader("Air Pollutants Levels")
    for pollutant, max_value in pollutants.items():
        value = latest_values[pollutant].values[0]
        progress_value = min(value / max_value, 1.0)
        st.write(f"##### {pollutant}: {value:.2f} µg/m³")
        st.progress(progress_value)


def get_weather_info():
    """Fetch and display current weather conditions."""
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("### 🌦 **Current Weather Conditions in Bangalore**")
    
    weather_data = fetch_weather_data()
    if weather_data:
        weather_desc = interpret_weather_code(weather_data["weather_code"])
        st.markdown(f"**{weather_desc}**")
        st.write(f"🌡 Temperature: {weather_data['temperature']}°C")
        st.write(f"💧 Humidity: {weather_data['humidity']}%")
        st.write(f"🌧 Precipitation: {weather_data['precipitation']} mm")
    else:
        st.write("⚠ Unable to fetch weather data.")