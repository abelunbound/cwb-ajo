import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import random
from gluonts.dataset.common import ListDataset
from gluonts.torch.model.deepar import DeepAREstimator
from gluonts.evaluation.backtest import make_evaluation_predictions
from gluonts.evaluation import Evaluator

import warnings
from sklearn.preprocessing import RobustScaler

import pandas as pd
import numpy as np
np.bool = np.bool_ # https://stackoverflow.com/questions/74893742/how-to-solve-attributeerror-module-numpy-has-no-attribute-bool




def prep_data_for_deep_ar_model(model_data):
    # Prepare dynamic features
    dynamic_features = [
        model_data['day_of_month'].values / 31.0,  # Normalize to [0,1]
        model_data['day_of_week'].values / 6.0,    # Normalize to [0,1]
        model_data['is_weekend'].values,
        model_data['rolling_7d_std'].values / model_data['rolling_7d_std'].max(),  # Normalize volatility
        model_data['is_salary_day'].values,
        model_data['is_rent_day'].values,
        model_data['is_major_expense'].values,
        model_data['trend_7d'].values
    ]

    # After generating data but before preparing for DeepAR

    # Step 2.1: Scale the target variable
    scaler = RobustScaler()
    scaled_balance = scaler.fit_transform(model_data['balance'].values.reshape(-1, 1)).flatten()


    # Training dataset in GluonTS format
    data_gluonts_fmt = ListDataset(
        [
            {
                "start": pd.Timestamp(model_data['date'].iloc[0]),
                # "target": train_data['balance'].values,
                "target": scaled_balance,
                "feat_dynamic_real": dynamic_features
            }
        ],
        freq="D"  # Daily frequency
    )

    return data_gluonts_fmt, scaler

# Step 3: Configure and train DeepAR model

def create_model_and_train(data_gluonts_fmt):
    
    # Configure the DeepAR model
    estimator = DeepAREstimator(
        freq="D",
        prediction_length=30,  # Forecast one month ahead
        context_length=60,     # Use 3 months of history
        num_layers=1,
        hidden_size=40,
        dropout_rate=0.1,
        num_feat_dynamic_real=8,  # Number of dynamic features in your dataset
        scaling=False,
        num_parallel_samples=100,
        batch_size=16,
        num_batches_per_epoch=12,
        trainer_kwargs={
            "max_epochs": 10,
            # "learning_rate": 1e-3,
        }
    )

    # Train the model
    predictor = estimator.train(data_gluonts_fmt)

    return predictor

# Step 4.1: Generate forecasts
# Step 4.1: Generate forecasts

def generate_forecasts(predictor, data_for_forecast):
    forecast_it, ts_it = make_evaluation_predictions(
        dataset=data_for_forecast,
        predictor=predictor,
        num_samples=1000  # Generate 100 sample paths for probabilistic forecasting
    )
    forecasts = list(forecast_it)
    tss = list(ts_it)

    return forecasts, tss


# Step 4.2: Generate forecasts - Transform forecasts back to original scale

# Create a function to inverse transform the forecasts
def inverse_transform_forecasts(forecast, scaler):
    """Transform the scaled forecasts back to original scale"""
    result = {}
    
    # Transform common quantiles
    for q in [0.01, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.92, 0.95, 0.99]:
        try: 
            # Get the forecast for this quantile
            forecast_values = forecast.quantile(q)
            
            # Inverse transform to original scale
            # If values are negative and original was positive, we need to handle this
            original_values = scaler.inverse_transform(forecast_values.reshape(-1, 1)).flatten()
            
            # Store the transformed values
            result[f'p{int(q*100)}'] = original_values
        except Exception as e:
            print(f"Warning: Could not transform quantile {q}: {str(e)}")
    
    return result



def get_forecast_data_frames (transformed_forecast_values, original_data_frame):
  
    forecast_df = pd.DataFrame(transformed_forecast_values)

    # combine validation forecast and actuals

    last_30_days_actual = original_data_frame['balance'].tail(30)
    last_30_dates_actual = original_data_frame['date'].tail(30)

    # Assuming both have 30 rows but different indices
    validation_forecast_df_copy = forecast_df.copy()
    validation_forecast_df_copy['actual'] = last_30_days_actual.values
    validation_forecast_df_copy['date'] = last_30_dates_actual.values
    validation_forecast_df_and_actual = validation_forecast_df_copy.copy()


    seven_days_forecast_df = validation_forecast_df_and_actual[0:7]
    fourteen_days_forecast_df = validation_forecast_df_and_actual[0:14]
    thirty_days_forecast_df = validation_forecast_df_and_actual[0:30]

    return seven_days_forecast_df, fourteen_days_forecast_df, thirty_days_forecast_df


