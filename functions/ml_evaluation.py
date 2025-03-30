import os
import re
import pandas as pd
import numpy as np
np.bool = np.bool_ # https://stackoverflow.com/questions/74893742/how-to-solve-attributeerror-module-numpy-has-no-attribute-bool

from gluonts.evaluation.backtest import make_evaluation_predictions
from gluonts.evaluation import Evaluator



# Run evaluation on the scaled forecasts


def get_evaluation_metrics (tss, forecasts, scaler):
    evaluator = Evaluator(quantiles=[0.5, 0.9])
    agg_metrics, item_metrics = evaluator(tss, forecasts)

    # Calculate the scale factor from the scaler
    # For RobustScaler, scale factor is the IQR
    scale_factor = scaler.scale_[0]  # First (and only) feature's scale
    # agg_metrics
    # Select and display specific metrics
    metrics_to_display = ["RMSE", "MSE", "MASE", "MAPE", "sMAPE", "MSIS"]

    # Create DataFrame from the metrics
    agg_metrics_df = pd.DataFrame(list(agg_metrics.items()), columns=["Metric", "Value"])

    # Create a copy with transformed values for scale-dependent metrics
    agg_metrics_original_scale = agg_metrics_df.copy()

    # Transform scale-dependent metrics
    for metric in ["RMSE", "MSE"]:
        if metric in agg_metrics_original_scale["Metric"].values:
            idx = agg_metrics_original_scale[agg_metrics_original_scale["Metric"] == metric].index
            # For RMSE, multiply by scale_factor
            if metric == "RMSE":
                agg_metrics_original_scale.loc[idx, "Value"] *= scale_factor
            # For MSE, multiply by scale_factor squared
            elif metric == "MSE":
                agg_metrics_original_scale.loc[idx, "Value"] *= (scale_factor ** 2)

    # Filter for display
    agg_metrics_filtered_df = agg_metrics_original_scale[agg_metrics_original_scale["Metric"].isin(metrics_to_display)]

    # print("Selected evaluation metrics (original scale):")
    # print(agg_metrics_filtered_df)

    return agg_metrics_filtered_df



# Calculate RMSE for each column relative to 'actual'

def calculate_rmse(df, target_col='actual'):
    """
    Calculate the Root Mean Square Error (RMSE) for each predictive column
    relative to the target column (default: 'actual').
    
    Returns a dictionary with column names as keys and RMSE values as values.

    """


    rmse_values = {}
    
    # Get all columns except date and target
    pred_columns = [col for col in df.columns if col != 'date' and col != target_col]
    
    for col in pred_columns:
        # Calculate squared differences
        squared_diff = (df[col] - df[target_col]) ** 2
        
        # Calculate mean of squared differences
        mean_squared_diff = squared_diff.mean()
        
        # Calculate root of mean squared differences
        rmse = np.sqrt(mean_squared_diff)
        
        rmse_values[col] = rmse
    
    return rmse_values

def get_combined_rmse (forecast_7days, forecast_14days, forecast_30days):
    # Calculate RMSE for each dataframe
    rmse_7days = calculate_rmse(forecast_7days)
    rmse_14_days = calculate_rmse(forecast_14days)
    rmse_30_days = calculate_rmse(forecast_30days)

    combined_rmse = pd.DataFrame({
        'seven_day_forecast': pd.Series(rmse_7days),
        'fourteen_day_forecast': pd.Series(rmse_14_days),
        'thirty_day_forecast': pd.Series(rmse_30_days)
        })
    # Reset index and rename it to 'quartiles'
    combined_rmse = combined_rmse.reset_index().rename(columns={'index': 'quartiles'})
    
    return combined_rmse


def get_experiment_number (logs_dir):
    
    # Get all subdirectories in the lightning_logs folder
    if os.path.exists(logs_dir):
        subdirs = [d for d in os.listdir(logs_dir) if os.path.isdir(os.path.join(logs_dir, d))]
        
        # Extract version numbers using regex
        version_numbers = []
        for subdir in subdirs:
            match = re.search(r'version_(\d+)', subdir)
            if match:
                version_numbers.append(int(match.group(1)))
        
        # Find the highest version number
        if version_numbers:
            highest_version = max(version_numbers)
            print(f"Highest experiment number found: {highest_version}")
            return highest_version
        else:
            print("No version subdirectories found.")
    else:
        print(f"Directory '{logs_dir}' not found.")

#  extract hyperparameters

def get_hyperparameters(file_path, experiment_id):
    # Read file as text
    with open(file_path, 'r') as file:
        content = file.read()
    
    # Initialize lists to store categories, metrics, and values
    categories = []
    metrics = []
    values = []
    experiment_ids = []  # New list for experiment IDs
    
    # Track current path in the nested structure
    current_path = []
    indent_level = 0
    
    lines = content.split('\n')
    for line in lines:
        if not line.strip():  # Skip empty lines
            continue
            
        # Count leading spaces for indentation
        spaces = len(line) - len(line.lstrip())
        
        # If indentation decreases, pop from path
        if spaces < indent_level:
            # Determine how many levels to pop
            levels_to_pop = (indent_level - spaces) // 2  # Assuming 2-space indentation
            for _ in range(levels_to_pop):
                if current_path:
                    current_path.pop()
        
        # Update indent level
        indent_level = spaces
        
        # Skip complex object definitions
        if '!!python/' in line:
            continue
            
        # Check if line contains a key-value pair
        if ':' in line:
            parts = line.split(':', 1)
            key = parts[0].strip()
            value_str = parts[1].strip()
            
            # Handle nested structures
            if not value_str:  # This is a parent key
                current_path.append(key)
                continue
                
            # Process value
            # Try to convert to appropriate type
            if value_str.lower() == 'true':
                value = True
            elif value_str.lower() == 'false':
                value = False
            elif value_str.lower() == 'null' or value_str.lower() == 'none':
                value = None
            elif re.match(r'^-?\d+$', value_str):
                value = int(value_str)
            elif re.match(r'^-?\d+\.\d+e?-?\d*$', value_str):
                value = float(value_str)
            else:
                value = value_str
                
            # Create the full key path
            full_key = '.'.join(current_path + [key]) if current_path else key
            
            # Add to our lists
            categories.append("Hyperparameter")
            metrics.append(full_key)
            values.append(value)
            experiment_ids.append(experiment_id)  # Add experiment_id to each row
    
    # Convert to DataFrame with four columns
    df = pd.DataFrame({
        'Category': categories,
        'Metric': metrics,
        'Value': values,
        'ExperimentID': experiment_ids  # New column for experiment IDs
    })
    
    return df