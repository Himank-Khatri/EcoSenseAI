import os
import json
import groq
import pickle
import pandas as pd
import streamlit as st
import altair as alt
from datetime import datetime
from sklearn.model_selection import train_test_split
from weather import fetch_weather_data, interpret_weather_code
from src.pipeline.prediction_pipeline import recursive_forecast
from sklearn.metrics import mean_absolute_error, mean_squared_error

GROQ_API_KEY = ""

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
    
#---------------------------------------------------------------
def retrain_models(X_df, y_df, artifacts_dir="artifacts/"):
    """
    Retrains models using new data, updates performance metrics, and saves them.
    """
    results_path = os.path.join(artifacts_dir, "model_results.json")

    if not os.path.exists(results_path):
        raise FileNotFoundError(f"{results_path} not found.")

    with open(results_path, "r") as file:
        results = json.load(file)

    X_train, X_test, y_train, y_test = train_test_split(X_df, y_df, test_size=0.2, random_state=42)

    updated_results = {}

    for model_name, model_info in results.items():
        model_path = model_info.get("model_path", "")

        if not os.path.exists(model_path):
            print(f"Model file not found: {model_path}, skipping {model_name}.")
            continue

        with open(model_path, "rb") as model_file:
            model = pickle.load(model_file)


        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = mean_squared_error(y_test, y_pred)

        with open(model_path, "wb") as model_file:
            pickle.dump(model, model_file)


        updated_results[model_name] = {
            "model_path": model_path,
            "mae": round(mae, 2),
            "rmse": round(rmse, 2)
        }

    with open(results_path, "w") as file:
        json.dump(updated_results, file, indent=4)

    st.info("Trained new models!")

# ----------------------- Data Loading -----------------------
def load_data(hour, aqi_filepath='artifacts/test.csv', pollutants_filepath='artifacts/test_pollutants.csv'):

    try:
        aqi_df = pd.read_csv(aqi_filepath)
        # if hour > 50:
        #     df = aqi_df.iloc[:50]
        #     X_df = df.drop('Value', axis=1)
        #     y_df = df['Value']
        #     retrain_models(X_df, y_df)

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

    return full_df

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
    
    return latest_values


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

    return weather_data

def get_ai_insights(observed_data, predicted_data, polls, weather_data, user_input):
    """Fetch AI-generated insights based on observed AQI, predicted AQI, and weather conditions."""
    client = groq.Client(api_key=GROQ_API_KEY)

    # Ensure we have valid data
    # observed_aqi = observed_data["Value"].iloc[-1] if not observed_data.empty else "N/A"
    # predicted_aqi = predicted_data["Value"].iloc[-1] if not predicted_data.empty else "N/A"
    temperature = weather_data.get('temperature', 'N/A')
    humidity = weather_data.get('humidity', 'N/A')
    wind_speed = weather_data.get('wind_speed', 'N/A')

    # Construct prompt dynamically
    prompt = f"""

    You are a sustainability consultant of a firm with these details: {user_input}

    The current observed AQI is {observed_data}, and the predicted AQI is {predicted_data} for the next hours.
    Pollutants:
    {polls}
    
    Weather conditions:
    - Temperature: {temperature}°C
    - Humidity: {humidity}%
    - Wind Speed: {wind_speed} km/h

    Based on this data, provide brief, **actionable safety recommendations**:
    - Health precautions for workers
    - Practical measures to improve air quality (with context of the firm)

    **Format the response in bullet points.**
    Bold important things
    **Ensure proper Markdown formatting and use a normal font size.**
    **Avoid headings, introductions, and conclusions.**
    Give concise output. Maximum 2 points n each category. don't give more htan 200 words.
    never say Implement a pollutant monitoring system 
    think of something tailored for the situation with pollutants, aqi, weather.
    use numbers and indicators, also round of big decimals to 2 place
    """

    response = client.chat.completions.create(
        # model="mixtral-8x7b-32768",
        model="llama-3.3-70b-versatile",
        # model="llama-3.3-70b-specdec",
        # model="gemma2-9b-it",
        messages=[
            {"role": "system", "content": "You are an AI assistant specializing in air quality analysis. Provide concise, specific, and innovative responses. think of something tailored for the situation with pollutants, aqi, weather. If AQI is high, give health warnings and mitigation steps. Avoid irrelevant topics. Only provide points—no starting/ending niceties. Assume the tips are for a cloth factory owner."},
            {"role": "user", "content": prompt}
        ],
        temperature=1.3,
        max_completion_tokens=512,
        top_p=1,
        stream=False
    )

    return response.choices[0].message.content if response.choices else "No insights available."
