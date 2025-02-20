import sys
import numpy as np
from src.logger import logging
from src.exception import CustomException
# from src.components.data_transformation import DataTransformationConfig
# from src.components.model_trainer import ModelTrainerConfig
from src.utils import load_object
import pandas as pd

def recursive_forecast(model, X_last, n_steps, rolling_window=3):
    predictions = []
    
    for i in range(n_steps):
        rolling_mean = np.mean(X_last[-rolling_window:])
        rolling_std = np.std(X_last[-rolling_window:])
        
        is_weekend = 1 if (i % 7) >= 5 else 0
        hour = (X_last[-1] + 1) % 24
        
        X_last = np.roll(X_last, shift=-1)
        X_last[-1] = rolling_mean
        X_last = np.roll(X_last, shift=-1)
        X_last[-2] = rolling_std
        X_last = np.roll(X_last, shift=-1)
        X_last[-3] = is_weekend
        X_last = np.roll(X_last, shift=-1)
        X_last[-4] = hour
        
        next_pred = model.predict(X_last.reshape(1, -1))[0]
        predictions.append(next_pred)
        
    return np.array(predictions)

