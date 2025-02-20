import pandas as pd
import numpy as np

# Read the AQI dataset
df = pd.read_csv("data/data.csv")

# Define AQI breakpoints (approximate real-world values)
def generate_pollutants(aqi):
    if aqi <= 50:  # Good
        return np.random.uniform(5, 20), np.random.uniform(10, 40), np.random.uniform(5, 30), np.random.uniform(2, 10), np.random.uniform(0.1, 1), np.random.uniform(10, 50)
    elif aqi <= 100:  # Moderate
        return np.random.uniform(20, 50), np.random.uniform(40, 80), np.random.uniform(30, 70), np.random.uniform(10, 20), np.random.uniform(0.5, 2), np.random.uniform(50, 100)
    elif aqi <= 150:  # Unhealthy for sensitive groups
        return np.random.uniform(50, 100), np.random.uniform(80, 150), np.random.uniform(70, 150), np.random.uniform(20, 50), np.random.uniform(1, 4), np.random.uniform(100, 150)
    elif aqi <= 200:  # Unhealthy
        return np.random.uniform(100, 150), np.random.uniform(150, 200), np.random.uniform(150, 200), np.random.uniform(50, 80), np.random.uniform(2, 6), np.random.uniform(150, 200)
    elif aqi <= 300:  # Very Unhealthy
        return np.random.uniform(150, 250), np.random.uniform(200, 300), np.random.uniform(200, 300), np.random.uniform(80, 120), np.random.uniform(4, 10), np.random.uniform(200, 300)
    else:  # Hazardous
        return np.random.uniform(250, 500), np.random.uniform(300, 600), np.random.uniform(300, 500), np.random.uniform(120, 200), np.random.uniform(8, 20), np.random.uniform(300, 400)

# Generate pollutant values for each row
df[["PM2.5", "PM10", "NO2", "SO2", "CO", "O3"]] = df["Value"].apply(lambda x: pd.Series(generate_pollutants(x)))

# Save as pollutants_data.csv
df.to_csv("data/pollutants_data.csv", index=False)

print("pollutants_data.csv has been generated successfully!")
