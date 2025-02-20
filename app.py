import os
import json
import pickle
import matplotlib.pyplot as plt
import time
import pandas as pd
import streamlit as st

from src.pipeline.prediction_pipeline import recursive_forecast

st.set_page_config(page_title='EcoSenseAI', layout='wide')
st.session_state['hour'] = 1

st.header("EcoSenseAI")
st.write("Know what's in the air before it's there!")

@st.cache_resource
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
    
    if not isinstance(results, dict):
        st.error("Invalid format: Expected a dictionary of models.")
        return None
    
    best_model_name = min(results, key=lambda x: results[x].get("mae", float("inf")))
    best_model_info = results[best_model_name]
    best_model_path = best_model_info.get("model_path", "")
    
    if not best_model_path or not os.path.exists(best_model_path):
        st.error(f"Model file not found: {best_model_path}")
        return None
    
    with open(best_model_path, "rb") as model_file:
        model = pickle.load(model_file)
    
    st.success(f"Loaded best model: {best_model_name} ({best_model_path}) with MAE {best_model_info.get('mae', 'N/A')}")
    return model

@st.cache_resource()
def load_data(aqi_filepath='artifacts/test.csv', pollutants_filepath='artifacts/test_pollutants.csv'):
    aqi_df = pd.read_csv(aqi_filepath)
    poll_df = pd.read_csv(pollutants_filepath)
    
    hour = st.session_state['hour']
    aqi_data = aqi_df[hour-1:hour+13].copy()
    poll_data = poll_df.iloc[hour+12].copy

    st.session_state['hour'] += 1
    
    return aqi_data, poll_data

def render_graph(data):
    model = load_best_model()

    data["hour"] = pd.Categorical(data["hour"], categories=data["hour"], ordered=True)
    data['AQI'] = data['Value']
    data = data.drop('Value', axis=1)
    st.line_chart(data.set_index('hour'), y='AQI', x_label='Time')

    last = data.drop('AQI', axis=1).iloc[-1]
    predictions = recursive_forecast(model, last, n_steps=7)
    st.write(predictions)
    
def show_pollutants(data):
    st.write("poll")
    
def main():
    col1, col2 = st.columns([1,1])
    aqi_data, poll_data = load_data()

    with col1:  
        render_graph(aqi_data)
    with col2:
        show_pollutants(poll_data)

if __name__ == '__main__':
    main()
