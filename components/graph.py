import dash
from dash import dcc, html, dash_table
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

# import importlib
# import functions.database
# importlib.reload(functions.database)

from functions.database import (
    get_column_name_and_datatype_dictionary, 
    prepare_sql_queries_and_values,
    insert_data_into_sql_data_base,
    retrieve_data_from_sql,
    add_metadata_columns
)

##################### Data Ingestion #####################

required_amount = 14000
applicant_id = '912345678'
applicant_id_query = f'applicant_id == "{applicant_id}"'

cwb_combined_rmse_table_name = 'cwb_combined_rmse' # Combined results for validation and future set
cwb_combined_rmse_df = retrieve_data_from_sql(cwb_combined_rmse_table_name)
# Get data for only target applicant
cwb_combined_rmse_df = cwb_combined_rmse_df.query(applicant_id_query)
print(f"\n:::::Graph Page: RMSE Data frame with length: {len(cwb_combined_rmse_df)} retrieved from {cwb_combined_rmse_table_name}\n")

### Get best RMSE quartile
### Get index of minimum RMSE in thirty_day_forecast
min_index = cwb_combined_rmse_df['thirty_day_forecast'].idxmin()
# Get the corresponding quartile value for best RMSE
quartile_with_best_rmse = cwb_combined_rmse_df.loc[min_index, 'quartiles']
# value for best RMSE
best_rmse_value = cwb_combined_rmse_df['thirty_day_forecast'].min()
best_rmse_value = round(best_rmse_value)


fin_history_enhanced_table_name = 'fin_history_enhanced' # Feature engineered data, applicant id, date, time etc
fin_history = retrieve_data_from_sql(fin_history_enhanced_table_name)
# Sort by date column (replace 'date_column' with your actual column name)
filtered_fin_history_df = fin_history.query(applicant_id_query).sort_values('date')
print(f"\n:::::Graph Page: Data frame with length: {len(filtered_fin_history_df)} retrieved from {fin_history_enhanced_table_name}\n")



cwb_validation_forecasts_table_name = 'cwb_validation_forecasts'
cwb_validation_forecasts_df = retrieve_data_from_sql(cwb_validation_forecasts_table_name)
# Sort by date column (replace 'date_column' with your actual column name)
cwb_validation_forecasts_df = cwb_validation_forecasts_df.query(applicant_id_query).sort_values('date')
print(f"\n:::::Graph Page: Data frame with length: {len(cwb_validation_forecasts_df)} retrieved from {cwb_validation_forecasts_table_name}\n")

# Get MAPE & Forecast Accuracy using 'actual' and 'p90' columns
mape = np.mean(np.abs((cwb_validation_forecasts_df['actual'] - cwb_validation_forecasts_df['p92']) / cwb_validation_forecasts_df['actual'])) * 100
# mape = round(mape)
forecast_accuracy = round(100-mape, 2)
print(f"Calculating MAPE for Quartile with best RMSE:- {quartile_with_best_rmse }: {mape:.2f}%")
print(f"Calculating Forecast Accuracy for Quartile with best RMSE:: {forecast_accuracy:.2f}%")

# Then get the last entry 
most_recent_balance = f"£{round(filtered_fin_history_df['balance'].iloc[-1])}"

########################################################## 

# Hyperparameters and Results
cwb_validation_assessment_table_name = 'cwb_validation_assessment' # Assessment and Hyperparameters for validation set

cwb_validation_assessment_df = retrieve_data_from_sql(cwb_validation_assessment_table_name)
cwb_validation_assessment_df = cwb_validation_assessment_df.query(applicant_id_query)


# 
cwb_exchange_rate_table_name = 'cwb_exchange_rate'
get_cwb_exchange_rate_df = retrieve_data_from_sql(cwb_exchange_rate_table_name)
get_cwb_exchange_rate_df = get_cwb_exchange_rate_df.query(applicant_id_query)





# Convert to DataFrame

#  Table 
# Define the metrics to show
show_metrics = [
    "Forecast for 30 days later (median)", 
    "Conservative forecast (10th percentile)", 
    "Optimistic forecast (90th percentile)", 
    "Actual final balance", 
    "Forecast error",
    "model_kwargs.cardinality.context_length",
    "patience",

]

# Filter the DataFrame to only show rows where Metric is in the show_metrics list
cwb_validation_assessment_filtered_df = cwb_validation_assessment_df[cwb_validation_assessment_df['metric'].isin(show_metrics)]

model_table = dash_table.DataTable(
    data=cwb_validation_assessment_filtered_df.to_dict('records'),
    columns=[
        {"name": "category", "id": "category"}, 
        {"name": "metric", "id": "metric"}, 
        {"name": "value", "id": "value"}
    ],
    style_table={'overflowX': 'auto'},
    style_cell={
        'textAlign': 'left',
        'padding': '10px',
        'fontFamily': 'Arial'
    },
    style_header={
        'backgroundColor': 'rgb(230, 230, 230)',
        'fontWeight': 'bold',
        'border': '1px solid black'
    },
    style_data_conditional=[
        {
            'if': {'row_index': 'odd'},
            'backgroundColor': 'rgb(248, 248, 248)'
        },
        {
            'if': {'filter_query': '{category} = "Hyperparameter"'},
            'backgroundColor': '#e6f7ff',
            'borderTop': '1px solid #b3e0ff'
        },
        {
            'if': {'filter_query': '{category} = "Affordability"'},
            'backgroundColor': '#fff2e6',
            'borderTop': '1px solid #ffcc99'
        },
        {
            'if': {'filter_query': '{category} = "Forecast"'},
            'backgroundColor': '#e6ffe6',
            'borderTop': '1px solid #99ff99'
        },
        {
            'if': {'filter_query': '{category} = "Comparative"'},
            'backgroundColor': '#f0e6ff',
            'borderTop': '1px solid #cc99ff'
        }
    ],
    style_as_list_view=True,
)



def create_timeline_fig(option):
    """
    Create a timeline chart based on the selected option.
    """
    timeline_fig = go.Figure()
    
    # Determine which column to use based on the selected option
    if option == "option1":
        y_values = filtered_fin_history_df['balance']
        y_title = 'Balance (£)'
        line_name = 'Daily Bank Balance'
    else:  # option2
        y_values = filtered_fin_history_df['rolling_7d_std']
        y_title = 'Volatility (7-Day Rolling Std Dev)'
        line_name = '7-Day Rolling Volatility'
    
    # Make sure date column is in datetime format
    filtered_fin_history_df_copy = filtered_fin_history_df.copy()
    if not pd.api.types.is_datetime64_any_dtype(filtered_fin_history_df_copy['date']):
        filtered_fin_history_df_copy['date'] = pd.to_datetime(filtered_fin_history_df_copy['date'])
    
    # Calculate the start date for the last 3 months
    last_date = filtered_fin_history_df_copy['date'].max()
    three_months_ago = last_date - pd.DateOffset(months=3)
    
    # Filter data for the last 3 months
    filtered_recent = filtered_fin_history_df_copy[filtered_fin_history_df_copy['date'] >= three_months_ago]
    
    # Add shaded area for the last 3 months
    if not filtered_recent.empty:
        y_column = 'balance' if option == "option1" else 'rolling_7d_std'
        timeline_fig.add_trace(go.Scatter(
            x=filtered_recent['date'],
            y=filtered_recent[y_column],
            fill='tozeroy',
            mode='none',
            fillcolor="rgba(173, 216, 230, 0.3)",
            name="Last 3 Months",
            hoverinfo="skip"
        ))
    
    # Add main line
    timeline_fig.add_trace(go.Scatter(
        x=filtered_fin_history_df_copy['date'],
        y=y_values,
        fill=None,
        mode='lines',
        line_color='#5F2EEA',
        name=line_name
    ))
    
    # Only add the required amount line for the balance option
    if option == "option1":
        timeline_fig.add_trace(go.Scatter(
            x=filtered_fin_history_df_copy['date'],
            y=[required_amount] * len(filtered_fin_history_df_copy['date']),
            mode='lines',
            line=dict(color='rgb(255, 99, 71)', width=2, dash='dash'),
            name='Required Amount'
        ))
    
    timeline_fig.update_layout(
        margin=dict(t=10), 
        xaxis_title='Date',
        yaxis_title=y_title,
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        height=350
    )
    
    return timeline_fig

def create_30_day_forecast_timeline_fig(option):
    """
    Create a timeline chart based on the selected option.
    """
    timeline_fig = go.Figure()
    
    # Determine which column to use based on the selected option
    if option == "option1":
        y_values = cwb_validation_forecasts_df[quartile_with_best_rmse]  # update to 30 days test forecast instead of validation forecast
        y_values_actual = cwb_validation_forecasts_df[quartile_with_best_rmse]
        y_title = 'Balance (£)'
        line_name = 'Forecasted Balance (£)'
    else:  # option2
        y_values = cwb_validation_forecasts_df[quartile_with_best_rmse]
        y_values_actual = cwb_validation_forecasts_df['actual']
        y_title = 'Balance (£)'
        line_name = 'Forecasted Balance (£)'
    
    # Make sure date column is in datetime format
    cwb_validation_forecasts_df_copy = cwb_validation_forecasts_df.copy()
    if not pd.api.types.is_datetime64_any_dtype(cwb_validation_forecasts_df_copy['date']):
        cwb_validation_forecasts_df_copy['date'] = pd.to_datetime(cwb_validation_forecasts_df_copy['date'])
    
    
    # Only add the required amount line for the balance option
    if option == "option1":
        timeline_fig.add_trace(go.Scatter(
            x=cwb_validation_forecasts_df_copy['date'],
            y=[required_amount] * len(cwb_validation_forecasts_df_copy['date']),
            mode='lines',
            line=dict(color='rgb(255, 99, 71)', width=2, dash='dash'),
            name='Required Amount'
        ))

        # Add main forecast line
        timeline_fig.add_trace(go.Scatter(
            x=cwb_validation_forecasts_df_copy['date'],
            y=y_values,
            fill=None,
            mode='lines',
            line_color='#5F2EEA',
            name=line_name
        ))


    if option == "option2":
        # Add actual line
        timeline_fig.add_trace(go.Scatter(
            x=cwb_validation_forecasts_df_copy['date'],
            y= y_values_actual,
            fill=None,
            mode='lines',
            line_color='red',
            name='Actual - for validation (£)'
        ))
        
        # Add main forecast line
        timeline_fig.add_trace(go.Scatter(
            x=cwb_validation_forecasts_df_copy['date'],
            y=y_values,
            fill=None,
            mode='lines',
            line_color='#5F2EEA',
            name=line_name
        ))
    
    timeline_fig.update_layout(
        margin=dict(t=10), 
        xaxis_title='Date',
        yaxis_title=y_title,
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        height=350
    )
    
    return timeline_fig

def create_30_exchange_rate_fig(option):
    """
    Create a timeline chart based on the selected option.
    """
    timeline_fig = go.Figure()
    
    # Determine which column to use based on the selected option
    if option == "option1":
        y_values = get_cwb_exchange_rate_df['naira_value']  # update to 30 days test forecast instead of validation forecast
        y_title = 'Balance (£)'
        line_name = 'Historical NGN-GBP exchange Rate'
    else:  # option2
        y_values = get_cwb_exchange_rate_df['naira_value']
        y_title = 'Balance (£)'
        line_name = 'Forecasted NGN-GBP exchange Rate'
    
    # Make sure date column is in datetime format
    get_cwb_exchange_rate_df_copy = get_cwb_exchange_rate_df.copy()
    if not pd.api.types.is_datetime64_any_dtype(get_cwb_exchange_rate_df_copy['date']):
        get_cwb_exchange_rate_df_copy['date'] = pd.to_datetime(get_cwb_exchange_rate_df_copy['date'])
    
    
    # Only add the required amount line for the balance option
    if option == "option1":
        timeline_fig.add_trace(go.Scatter(
            x=get_cwb_exchange_rate_df_copy['date'],
            y=y_values,
            fill=None,
            mode='lines',
            line_color='red',
            name=line_name
        ))


    if option == "option2":
        # Add actual line
        timeline_fig.add_trace(go.Scatter(
            x=get_cwb_exchange_rate_df_copy['date'],
            y= y_values,
            fill=None,
            mode='lines',
            line_color='#5F2EEA',
            name=line_name
        ))
        
    
    timeline_fig.update_layout(
        margin=dict(t=10), 
        xaxis_title='Date',
        yaxis_title=y_title,
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        height=350
    )
    
    return timeline_fig