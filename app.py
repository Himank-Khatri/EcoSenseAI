import os
import json
import pickle
import pandas as pd
import streamlit as st
import altair as alt
from datetime import datetime

from src.pipeline.prediction_pipeline import recursive_forecast
from weather import fetch_weather_data, interpret_weather_code

st.set_page_config(page_title='EcoSenseAI', layout='wide')

st.markdown(
    """
    <style>
        .css-18e3th9 {
            padding-top: 10px !important;
            padding-bottom: 0px !important;
        }
        .stApp {
            margin-top: -80px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

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
        model = pickle.load(model_file)

    return model

def load_data(hour, aqi_filepath='artifacts/test.csv', pollutants_filepath='artifacts/test_pollutants.csv'):
    aqi_df = pd.read_csv(aqi_filepath)
    poll_df = pd.read_csv(pollutants_filepath)

    aqi_data = aqi_df[hour-1:hour+13].copy()
    poll_data = poll_df.iloc[hour+12:hour+13].copy()

    return aqi_data, poll_data

def get_aqi_category(aqi):
    if aqi <= 50:
        return "Good", "🟢", "#2ECC71"
    elif aqi <= 100:
        return "Moderate", "🟡", "#F1C40F"
    else:
        return "Unhealthy", "🔴", "#E74C3C"

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
            color=alt.Color("segment", scale=alt.Scale(domain=["Observed", "Predicted"], range=["#6baed6", "#fb6a4a"]), legend=alt.Legend(title="AQI")),
            strokeDash=alt.condition(
                alt.datum.segment == "Predicted",
                alt.value([5, 5]),
                alt.value([0])
            )
        )
    )
    st.altair_chart(chart, use_container_width=True)

def show_pollutants(data):
    pollutants = {"PM2.5": 50, "PM10": 100, "NO2": 40, "SO2": 20, "CO": 10, "O3": 60}
    latest_values = data.iloc[-1:]

    # with st.expander("Pollutants", expanded=True):  
    st.subheader("Air Pollutants Levels")
    for pollutant, max_value in pollutants.items():
        value = latest_values[pollutant].values[0] 
        progress_value = min(value / max_value, 1.0)
        st.write(f"##### {pollutant}: {value:.2f} µg/m³")  
        st.progress(progress_value)


def main():
    st.markdown("<h1 >EcoSenseAI</h1>", unsafe_allow_html=True)
    st.markdown("<h4 >What's in the air before it's there!</h4>", unsafe_allow_html=True)
    
    col1, col_mid, col2 = st.columns([1.2, 0.1, 1])
    
    with col1:
        with st.popover('Developer Settings'):
            hour = st.slider("Select Hour", min_value=1, max_value=100, value=1)
    
    aqi_data, poll_data = load_data(hour)
    current_aqi = aqi_data["Value"].iloc[-1]
    category, emoji, color = get_aqi_category(current_aqi)
    
    with col1:
        render_graph(aqi_data)
        show_pollutants(poll_data)
    
    with col2:
    # AQI Display
        st.markdown(f"<h1 style='text-align: center; margin-top: 0px; padding-top: 0px; color: {color};'> {emoji} AQI: {current_aqi} ({category}) </h1>", unsafe_allow_html=True)
        
        # Date and Time
        st.markdown(f"<h4 style='text-align: center;'>📅 {datetime.now().strftime('%Y-%m-%d | %H:%M:%S')} </h4>", unsafe_allow_html=True)

        # AI Insights and Suggestions
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center;'>🔍 AI Insights & Recommendations</h3>", unsafe_allow_html=True)

        st.write("### **Safety Measures**")
        st.write("- **Wear protective gear**: Use N95 masks in high AQI conditions.")
        st.write("- **Improve indoor air quality**: Use air purifiers, houseplants, and proper ventilation strategies.")
        st.write("- **Monitor health symptoms**: Respiratory issues can worsen with poor air quality; seek medical advice if needed.")

        st.write("### **Mitigation Strategies**")
        st.write("- **Industrial Compliance**: Enforce stricter emission controls and monitoring in industries like cement and steel manufacturing.")
        st.write("- **Sustainable Urban Planning**: Increase green zones, rooftop gardens, and urban forests to absorb pollutants.")

        # Climate Information
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("### 🌦 **Current Weather Conditions in Bangalore**")
        
        weather_data = fetch_weather_data()
        if weather_data:
            weather_desc = interpret_weather_code(weather_data["weather_code"])
            st.markdown(f"**{weather_desc}**")
            st.write(f"🌡 Temperature: {weather_data['temperature']}°C")
            st.write(f"💧 Humidity: {weather_data['humidity']}%")
            st.write(f"🌧 Precipitation: {weather_data['precipitation']} mm")

if __name__ == '__main__':
    main()
