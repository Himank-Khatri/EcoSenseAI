import requests
import pandas as pd

def fetch_weather_data(latitude=12.9716, longitude=77.5946):
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={latitude}&longitude={longitude}&hourly=temperature_2m,"
        f"relative_humidity_2m,precipitation,weathercode&current_weather=true"
    )

    response = requests.get(url)
    if response.status_code != 200:
        return None

    data = response.json()
    current_weather = data.get("current_weather", {})
    
    return {
        "temperature": current_weather.get("temperature"),
        "humidity": data["hourly"]["relative_humidity_2m"][0],
        "precipitation": data["hourly"]["precipitation"][0],
        "weather_code": current_weather.get("weathercode"),
    }

def interpret_weather_code(code):
    weather_dict = {
        0: "Clear sky ☀️",
        1: "Mainly clear 🌤️",
        2: "Partly cloudy ⛅",
        3: "Overcast ☁️",
        45: "Fog 🌫️",
        48: "Depositing rime fog 🌫️",
        51: "Light drizzle 🌦️",
        53: "Moderate drizzle 🌧️",
        55: "Heavy drizzle 🌧️",
        61: "Light rain 🌦️",
        63: "Moderate rain 🌧️",
        65: "Heavy rain 🌧️",
        71: "Light snow ❄️",
        73: "Moderate snow ❄️",
        75: "Heavy snow ❄️",
    }
    return weather_dict.get(code, "Unknown conditions 🤷")

