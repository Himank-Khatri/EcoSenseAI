import os
import sys
import pickle
from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.exception import CustomException
from src.logger import logging
from src.utils import save_object
from src.components.model_tainer import ModelTrainer

class DataIngestionTransformation:
    def __init__(self, filepath: str):
        self.data_file_path = filepath 
    
    def initiate_data_ingestion_transformation(self):
        try:
            df = pd.read_csv(self.data_file_path)
            logging.info("Data ingested.")

            df['Datetime'] = pd.to_datetime(df['Datetime'])
            df.set_index('Datetime', inplace=True)

            df['hour'] = df.index.hour + 1
            df['day_of_week'] = df.index.dayofweek
            df['is_weekend'] = df['day_of_week'].apply(lambda x: 1 if x >= 5 else 0)

            lag_hours = 3
            for i in range(1, lag_hours+1):
                df[f'lag_{i}'] = df['Value'].shift(i)

            df['rolling_mean_3'] = df['Value'].rolling(window=3).mean() 
            df['rolling_std_3'] = df['Value'].rolling(window=3).std()

            df = df.dropna(axis=0)
            dataset = df.drop('day_of_week', axis=1)
            logging.info("Data preprocessed")

            split_ratio = 0.8
            split_index = int(len(dataset) * split_ratio)

            train_df = dataset.iloc[:split_index]
            train_pollutants = train_df[['PM2.5', 'PM10', 'NO2', 'SO2', 'CO', 'O3']]
            train_df = train_df.drop(columns=['PM2.5', 'PM10', 'NO2', 'SO2', 'CO', 'O3'], axis=1)


            test_df = dataset.iloc[split_index:]
            test_pollutants = test_df[['PM2.5', 'PM10', 'NO2', 'SO2', 'CO', 'O3']]
            test_df = test_df.drop(columns=['PM2.5', 'PM10', 'NO2', 'SO2', 'CO', 'O3'], axis=1)

            train_df.to_csv('artifacts/train.csv', header=True, index=False)
            test_df.to_csv('artifacts/test.csv', header=True, index=False)
            train_pollutants.to_csv('artifacts/train_pollutants.csv', header=True)
            test_pollutants.to_csv('artifacts/test_pollutants.csv', header=True)


            return train_df, test_df

        except Exception as e:
            logging.info(e)
            raise CustomException(e, sys)
    
if __name__ == '__main__':
    obj = DataIngestionTransformation('notebook/data/pollutants_data.csv')
    train_data, test_data = obj.initiate_data_ingestion_transformation()

    model_trainer = ModelTrainer()
    model_trainer.initiate_model_trainer(train_data, test_data)