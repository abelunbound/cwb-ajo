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
print(f"\n:::::Graph Page: Data frame with length: {len(cwb_combined_rmse_df)} retrieved from {cwb_combined_rmse_table_name}\n")

### Get best RMSE quartile
### Get index of minimum RMSE in thirty_day_forecast
# Convert column to integers
# cwb_combined_rmse_df['thirty_day_forecast'] = cwb_combined_rmse_df['thirty_day_forecast'].astype(int)
min_index = cwb_combined_rmse_df['thirty_day_forecast'].idxmin()
# Get the corresponding quartile value
quartile_with_best_rmse = cwb_combined_rmse_df.loc[min_index, 'quartiles']


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


# Then get the last entry 
most_recent_balance = f"£{round(filtered_fin_history_df['balance'].iloc[-1])}"

########################################################## 




# Sample data from the assessment
data = {
    "Category": [
        "Hyperparameter", "Hyperparameter", "Hyperparameter", "Hyperparameter", "Hyperparameter",
        "Hyperparameter", "Hyperparameter", "Hyperparameter", "Hyperparameter", "Hyperparameter",
        "Hyperparameter", "Hyperparameter", "Hyperparameter", "Hyperparameter", "Hyperparameter",
        "Hyperparameter", "Hyperparameter", "Hyperparameter", "Hyperparameter", "Hyperparameter",
        "Affordability", "Affordability", "Affordability", "Affordability", "Affordability",
        "Forecast", "Forecast", "Forecast", "Forecast", "Forecast",
        "Comparative", "Comparative", "Comparative"
    ],
    "Metric": [
        "lr", "model_kwargs.cardinality.context_length", "model_kwargs.cardinality.default_scale", 
        "state.__init_args__", "state.beta", "dropout_rate", "embedding_dimension", "freq", 
        "hidden_size", "lags_seq", "nonnegative_pred_samples", "num_feat_dynamic_real", 
        "num_feat_static_cat", "num_feat_static_real", "num_layers", "num_parallel_samples", 
        "prediction_length", "scaling", "patience", "weight_decay",
        "Required amount", "Assessment", "Probability of meeting threshold", "Recommendation", "Buffer amount (median forecast)",
        "Current balance", "Forecast for 30 days later (median)", "Conservative forecast (10th percentile)", 
        "Optimistic forecast (90th percentile)", "Forecast range width",
        "Actual final balance", "Forecast error", "Actual balance within 80% prediction interval"
    ],
    "Value": [
        "0.001", "90", "", "*id001", "0.0", "0.1", "", "D", "40", "", "False", "12", "1", "1", 
        "1", "100", "30", "False", "10", "1e-08",
        "£16000.00", "Low confidence", "Under 50%", "Request additional financial guarantees", "£-698.67",
        "£13813.30", "£15301.33", "£14555.34", "£16270.11", "£1714.77",
        "£16258.10", "£956.77 (5.88%)", "True"
    ],
    "ExperimentID": ["exp_69"] * 33
}

# Convert to DataFrame
df = pd.DataFrame(data)

# Extract data for affordability analysis
affordability_df = df[df["Category"] == "Affordability"]
forecast_df = df[df["Category"] == "Forecast"]
comparative_df = df[df["Category"] == "Comparative"]

# # Extract numeric values for visualization
# current_balance = float(forecast_df[forecast_df["Metric"] == "Current balance"]["Value"].iloc[0].replace("£", "").replace(",", ""))
# forecast_median = float(forecast_df[forecast_df["Metric"] == "Forecast for 30 days later (median)"]["Value"].iloc[0].replace("£", "").replace(",", ""))
# forecast_10th = float(forecast_df[forecast_df["Metric"] == "Conservative forecast (10th percentile)"]["Value"].iloc[0].replace("£", "").replace(",", ""))
# forecast_90th = float(forecast_df[forecast_df["Metric"] == "Optimistic forecast (90th percentile)"]["Value"].iloc[0].replace("£", "").replace(",", ""))
# actual_balance = float(comparative_df[comparative_df["Metric"] == "Actual final balance"]["Value"].iloc[0].replace("£", "").replace(",", ""))
# required_amount = float(affordability_df[affordability_df["Metric"] == "Required amount"]["Value"].iloc[0].replace("£", "").replace(",", ""))

# # Create forecast timeline data
# dates = pd.date_range(start='2023-01-01', periods=31, freq='D')
# forecast_range = np.linspace(current_balance, forecast_median, 31)
# forecast_lower = np.linspace(current_balance, forecast_10th, 31)
# forecast_upper = np.linspace(current_balance, forecast_90th, 31)
# actual_range = np.linspace(current_balance, actual_balance, 31)

# # Create gauge chart for affordability assessment
# assessment_value = "Low" if affordability_df[affordability_df["Metric"] == "Assessment"]["Value"].iloc[0] == "Low confidence" else "High"
# gauge_fig = go.Figure(go.Indicator(
#     mode="gauge+number+delta",
#     value=forecast_median,
#     domain={'x': [0, 1], 'y': [0, 1]},
#     title={'text': "Forecast vs Required Amount"},
#     delta={'reference': required_amount, 'increasing': {'color': "green"}, 'decreasing': {'color': "red"}},
#     gauge={
#         'axis': {'range': [None, required_amount * 1.2]},
#         'bar': {'color': "#1f77b4"},
#         'steps': [
#             {'range': [0, required_amount * 0.7], 'color': "red"},
#             {'range': [required_amount * 0.7, required_amount * 0.9], 'color': "orange"},
#             {'range': [required_amount * 0.9, required_amount], 'color': "yellow"},
#             {'range': [required_amount, required_amount * 1.2], 'color': "green"}
#         ],
#         'threshold': {
#             'line': {'color': "red", 'width': 4},
#             'thickness': 0.75,
#             'value': required_amount
#         }
#     }
# ))
# gauge_fig.update_layout(height=250)

# # Create forecast timeline chart
# timeline_fig = go.Figure()

# # Add forecast range as a filled area
# timeline_fig.add_trace(go.Scatter(
#     x=filtered_fin_history_df['date'],
#     y=filtered_fin_history_df['balance'],
#     fill=None,
#     mode='lines',
#     line_color='#5F2EEA',
#     name='Daily Bank Balance'
# ))

# # timeline_fig.add_trace(go.Scatter(
# #     x=dates,
# #     y=forecast_lower,
# #     fill='tonexty',
# #     mode='lines',
# #     line_color='rgba(73, 160, 213, 0.2)',
# #     name='10th Percentile'
# # ))

# # # Add median forecast line
# # timeline_fig.add_trace(go.Scatter(
# #     x=dates,
# #     y=forecast_range,
# #     mode='lines',
# #     line=dict(color='rgb(73, 160, 213)', width=2),
# #     name='Median Forecast'
# # ))

# # # Add actual balance line
# # timeline_fig.add_trace(go.Scatter(
# #     x=dates,
# #     y=actual_range,
# #     mode='lines',
# #     line=dict(color='rgb(44, 160, 44)', width=2, dash='dot'),
# #     name='Actual Balance'
# # ))

# # Add target line
# timeline_fig.add_trace(go.Scatter(
#     x=filtered_fin_history_df['date'],
#     y=[required_amount1] * len(filtered_fin_history_df['date']),
#     mode='lines',
#     line=dict(color='rgb(255, 99, 71)', width=2, dash='dash'),
#     name='Required Amount'
# ))

# timeline_fig.update_layout(
#     # title='Balance Forecast Timeline (30 Days)',
#     margin=dict(t=10), 
#     xaxis_title='Date',
#     yaxis_title='Balance (£)',
#     hovermode='x unified',
#     legend=dict(
#         orientation="h",
#         yanchor="bottom",
#         y=1.02,
#         xanchor="right",
#         x=1
#     ),
#     height=350
# )

# # Create a donut chart for recommendation
# recommendation = affordability_df[affordability_df["Metric"] == "Recommendation"]["Value"].iloc[0]
# probability = affordability_df[affordability_df["Metric"] == "Probability of meeting threshold"]["Value"].iloc[0]
# prob_value = 40 if probability == "Under 50%" else 75  # Approximate for visualization

# donut_fig = go.Figure(go.Pie(
#     labels=["Below Threshold", "Above Threshold"],
#     values=[100-prob_value, prob_value],
#     hole=.7,
#     marker_colors=['#ff9999', '#66b3ff']
# ))

# donut_fig.update_layout(
#     title_text="Probability of Meeting Threshold",
#     annotations=[dict(text=f"{probability}", x=0.5, y=0.5, font_size=20, showarrow=False)],
#     height=250,
#     showlegend=False
# )

# # Create a bar chart comparing forecasts
# bar_data = {
#     'Category': ['Current', 'Forecast (Median)', 'Required', 'Actual'],
#     'Value': [current_balance, forecast_median, required_amount, actual_balance]
# }
# bar_df = pd.DataFrame(bar_data)

# comparison_fig = px.bar(
#     bar_df, 
#     x='Category', 
#     y='Value',
#     color='Category',
#     color_discrete_map={
#         'Current': '#1f77b4',
#         'Forecast (Median)': '#ff7f0e',
#         'Required': '#d62728',
#         'Actual': '#2ca02c'
#     },
#     title='Balance Comparison'
# )
# comparison_fig.update_layout(height=250)




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
filtered_df = df[df['Metric'].isin(show_metrics)]

model_table = dash_table.DataTable(
    data=filtered_df.to_dict('records'),
    columns=[
        {"name": "Category", "id": "Category"}, 
        {"name": "Metric", "id": "Metric"}, 
        {"name": "Value", "id": "Value"}
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
            'if': {'filter_query': '{Category} = "Hyperparameter"'},
            'backgroundColor': '#e6f7ff',
            'borderTop': '1px solid #b3e0ff'
        },
        {
            'if': {'filter_query': '{Category} = "Affordability"'},
            'backgroundColor': '#fff2e6',
            'borderTop': '1px solid #ffcc99'
        },
        {
            'if': {'filter_query': '{Category} = "Forecast"'},
            'backgroundColor': '#e6ffe6',
            'borderTop': '1px solid #99ff99'
        },
        {
            'if': {'filter_query': '{Category} = "Comparative"'},
            'backgroundColor': '#f0e6ff',
            'borderTop': '1px solid #cc99ff'
        }
    ],
    style_as_list_view=True,
)






# def create_timeline_fig(option):
#     """
#     Create a timeline chart based on the selected option.
    
#     Parameters:
#     option (str): Either "option1" (Financial History) or "option2" (Volatility)
    
#     Returns:
#     plotly.graph_objects.Figure: The configured timeline chart
#     """
#     timeline_fig = go.Figure()
    
#     # Determine which column to use based on the selected option
#     if option == "option1":
#         y_values = filtered_fin_history_df['balance']
#         y_title = 'Balance (£)'
#         line_name = 'Daily Bank Balance'
#     else:  # option2
#         y_values = filtered_fin_history_df['rolling_7d_std']
#         y_title = 'Volatility (7-Day Rolling Std Dev)'
#         line_name = '7-Day Rolling Volatility'
    
#     # Add main line
#     timeline_fig.add_trace(go.Scatter(
#         x=filtered_fin_history_df['date'],
#         y=y_values,
#         fill=None,
#         mode='lines',
#         line_color='#5F2EEA',
#         name=line_name
#     ))
    
#     # Only add the required amount line for the balance option
#     if option == "option1":
#         timeline_fig.add_trace(go.Scatter(
#             x=filtered_fin_history_df['date'],
#             y=[required_amount] * len(filtered_fin_history_df['date']),
#             mode='lines',
#             line=dict(color='rgb(255, 99, 71)', width=2, dash='dash'),
#             name='Required Amount'
#         ))
    
#     timeline_fig.update_layout(
#         margin=dict(t=10), 
#         xaxis_title='Date',
#         yaxis_title=y_title,
#         hovermode='x unified',
#         legend=dict(
#             orientation="h",
#             yanchor="bottom",
#             y=1.02,
#             xanchor="right",
#             x=1
#         ),
#         height=350
#     )
    
#     return timeline_fig

# def create_timeline_fig(option):
#     """
#     Create a timeline chart based on the selected option.
    
#     Parameters:
#     option (str): Either "option1" (Financial History) or "option2" (Volatility)
    
#     Returns:
#     plotly.graph_objects.Figure: The configured timeline chart
#     """
#     timeline_fig = go.Figure()
    
#     # Determine which column to use based on the selected option
#     if option == "option1":
#         y_values = filtered_fin_history_df['balance']
#         y_title = 'Balance (£)'
#         line_name = 'Daily Bank Balance'
#     else:  # option2
#         y_values = filtered_fin_history_df['rolling_7d_std']
#         y_title = 'Volatility (7-Day Rolling Std Dev)'
#         line_name = '7-Day Rolling Volatility'
    
#     # Calculate the start date for the last 3 months
#     last_date = filtered_fin_history_df['date'].max()
#     three_months_ago = last_date - pd.DateOffset(months=3)
    
#     # Filter data for the last 3 months
#     filtered_recent = filtered_fin_history_df[filtered_fin_history_df['date'] >= three_months_ago]
    
#     # Add shaded area for the last 3 months
#     timeline_fig.add_trace(go.Scatter(
#         x=filtered_recent['date'],
#         y=filtered_recent[y_values.name],  # Use the column name from the Series
#         fill='tozeroy',  # Fill down to the x-axis
#         mode='none',  # No lines or markers
#         fillcolor="rgba(173, 216, 230, 0.3)",
#         name="Last 3 Months",
#         hoverinfo="skip"
#     ))
    
#     # Add main line
#     timeline_fig.add_trace(go.Scatter(
#         x=filtered_fin_history_df['date'],
#         y=y_values,
#         fill=None,
#         mode='lines',
#         line_color='#5F2EEA',
#         name=line_name
#     ))
    
#     # Only add the required amount line for the balance option
#     if option == "option1":
#         timeline_fig.add_trace(go.Scatter(
#             x=filtered_fin_history_df['date'],
#             y=[required_amount] * len(filtered_fin_history_df['date']),
#             mode='lines',
#             line=dict(color='rgb(255, 99, 71)', width=2, dash='dash'),
#             name='Required Amount'
#         ))
    
#     timeline_fig.update_layout(
#         margin=dict(t=10), 
#         xaxis_title='Date',
#         yaxis_title=y_title,
#         hovermode='x unified',
#         legend=dict(
#             orientation="h",
#             yanchor="bottom",
#             y=1.02,
#             xanchor="right",
#             x=1
#         ),
#         height=350
#     )
    
#     return timeline_fig


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
    
    # # Calculate the start date for the last 3 months
    # last_date = filtered_fin_history_df_copy['date'].max()
    # three_months_ago = last_date - pd.DateOffset(months=3)
    
    # # Filter data for the last 3 months
    # filtered_recent = filtered_fin_history_df_copy[filtered_fin_history_df_copy['date'] >= three_months_ago]
    
    # # Add shaded area for the last 3 months
    # if not filtered_recent.empty:
    #     y_column = 'balance' if option == "option1" else 'rolling_7d_std'
    #     timeline_fig.add_trace(go.Scatter(
    #         x=filtered_recent['date'],
    #         y=filtered_recent[y_column],
    #         fill='tozeroy',
    #         mode='none',
    #         fillcolor="rgba(173, 216, 230, 0.3)",
    #         name="Last 3 Months",
    #         hoverinfo="skip"
    #     ))
    
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