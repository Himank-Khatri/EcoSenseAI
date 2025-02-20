import os
import sys
import json
import pickle
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
import xgboost as xgb
from sklearn.svm import SVR
import warnings

warnings.filterwarnings("ignore", message=".*does not have valid feature names.*")

from src.exception import CustomException
from src.logger import logging

class ModelTrainer:
    def initiate_model_trainer(self, train_df, test_df):
        try:
            train_df = pd.read_csv('artifacts/train.csv')
            test_df = pd.read_csv('artifacts/test.csv')
            X_train, y_train = train_df.drop('Value', axis=1), train_df['Value']
            X_test, y_test = test_df.drop('Value', axis=1), test_df['Value']

            models = {
                "Random Forest": RandomForestRegressor(n_estimators=100, random_state=42),
                "Gradient Boosting": GradientBoostingRegressor(n_estimators=100, random_state=42),
                "XGBoost": xgb.XGBRegressor(n_estimators=100, random_state=42),
                "SVR": SVR(kernel='rbf')
            }

            os.makedirs("artifacts", exist_ok=True)

            results = {}

            for model_name, model in models.items():
                model.fit(X_train, y_train)
                model_path = f'artifacts/{model_name}.pkl'
                
                with open(model_path, "wb") as file:
                    pickle.dump(model, file)
                
                y_pred = model.predict(X_test)
                mae = mean_absolute_error(y_test, y_pred)
                rmse = np.sqrt(mean_squared_error(y_test, y_pred))
                
                results[model_name] = {
                    "model_path": model_path,
                    "mae": round(mae, 2),
                    "rmse": round(rmse, 2)
                }
                
                logging.info(f"{model_name} - MAE: {mae:.2f}, RMSE: {rmse:.2f}")

            with open("artifacts/model_results.json", "w") as json_file:
                json.dump(results, json_file, indent=4)

            logging.info("Model results saved in 'artifacts/models.json'")

        except Exception as e:
            logging.info(e)
            raise CustomException(e, sys)