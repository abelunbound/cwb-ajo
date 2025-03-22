import dash
from dash import dcc, html, dash_table
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

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

# Extract numeric values for visualization
current_balance = float(forecast_df[forecast_df["Metric"] == "Current balance"]["Value"].iloc[0].replace("£", "").replace(",", ""))
forecast_median = float(forecast_df[forecast_df["Metric"] == "Forecast for 30 days later (median)"]["Value"].iloc[0].replace("£", "").replace(",", ""))
forecast_10th = float(forecast_df[forecast_df["Metric"] == "Conservative forecast (10th percentile)"]["Value"].iloc[0].replace("£", "").replace(",", ""))
forecast_90th = float(forecast_df[forecast_df["Metric"] == "Optimistic forecast (90th percentile)"]["Value"].iloc[0].replace("£", "").replace(",", ""))
actual_balance = float(comparative_df[comparative_df["Metric"] == "Actual final balance"]["Value"].iloc[0].replace("£", "").replace(",", ""))
required_amount = float(affordability_df[affordability_df["Metric"] == "Required amount"]["Value"].iloc[0].replace("£", "").replace(",", ""))

# Create forecast timeline data
dates = pd.date_range(start='2023-01-01', periods=31, freq='D')
forecast_range = np.linspace(current_balance, forecast_median, 31)
forecast_lower = np.linspace(current_balance, forecast_10th, 31)
forecast_upper = np.linspace(current_balance, forecast_90th, 31)
actual_range = np.linspace(current_balance, actual_balance, 31)

# Create gauge chart for affordability assessment
assessment_value = "Low" if affordability_df[affordability_df["Metric"] == "Assessment"]["Value"].iloc[0] == "Low confidence" else "High"
gauge_fig = go.Figure(go.Indicator(
    mode="gauge+number+delta",
    value=forecast_median,
    domain={'x': [0, 1], 'y': [0, 1]},
    title={'text': "Forecast vs Required Amount"},
    delta={'reference': required_amount, 'increasing': {'color': "green"}, 'decreasing': {'color': "red"}},
    gauge={
        'axis': {'range': [None, required_amount * 1.2]},
        'bar': {'color': "#1f77b4"},
        'steps': [
            {'range': [0, required_amount * 0.7], 'color': "red"},
            {'range': [required_amount * 0.7, required_amount * 0.9], 'color': "orange"},
            {'range': [required_amount * 0.9, required_amount], 'color': "yellow"},
            {'range': [required_amount, required_amount * 1.2], 'color': "green"}
        ],
        'threshold': {
            'line': {'color': "red", 'width': 4},
            'thickness': 0.75,
            'value': required_amount
        }
    }
))
gauge_fig.update_layout(height=250)

# Create forecast timeline chart
timeline_fig = go.Figure()

# Add forecast range as a filled area
timeline_fig.add_trace(go.Scatter(
    x=dates,
    y=forecast_upper,
    fill=None,
    mode='lines',
    line_color='rgba(73, 160, 213, 0.2)',
    name='90th Percentile'
))

timeline_fig.add_trace(go.Scatter(
    x=dates,
    y=forecast_lower,
    fill='tonexty',
    mode='lines',
    line_color='rgba(73, 160, 213, 0.2)',
    name='10th Percentile'
))

# Add median forecast line
timeline_fig.add_trace(go.Scatter(
    x=dates,
    y=forecast_range,
    mode='lines',
    line=dict(color='rgb(73, 160, 213)', width=2),
    name='Median Forecast'
))

# Add actual balance line
timeline_fig.add_trace(go.Scatter(
    x=dates,
    y=actual_range,
    mode='lines',
    line=dict(color='rgb(44, 160, 44)', width=2, dash='dot'),
    name='Actual Balance'
))

# Add target line
timeline_fig.add_trace(go.Scatter(
    x=dates,
    y=[required_amount] * len(dates),
    mode='lines',
    line=dict(color='rgb(255, 99, 71)', width=2, dash='dash'),
    name='Required Amount'
))

timeline_fig.update_layout(
    title='Balance Forecast Timeline (30 Days)',
    xaxis_title='Date',
    yaxis_title='Balance (£)',
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

# Create a donut chart for recommendation
recommendation = affordability_df[affordability_df["Metric"] == "Recommendation"]["Value"].iloc[0]
probability = affordability_df[affordability_df["Metric"] == "Probability of meeting threshold"]["Value"].iloc[0]
prob_value = 40 if probability == "Under 50%" else 75  # Approximate for visualization

donut_fig = go.Figure(go.Pie(
    labels=["Below Threshold", "Above Threshold"],
    values=[100-prob_value, prob_value],
    hole=.7,
    marker_colors=['#ff9999', '#66b3ff']
))

donut_fig.update_layout(
    title_text="Probability of Meeting Threshold",
    annotations=[dict(text=f"{probability}", x=0.5, y=0.5, font_size=20, showarrow=False)],
    height=250,
    showlegend=False
)

# Create a bar chart comparing forecasts
bar_data = {
    'Category': ['Current', 'Forecast (Median)', 'Required', 'Actual'],
    'Value': [current_balance, forecast_median, required_amount, actual_balance]
}
bar_df = pd.DataFrame(bar_data)

comparison_fig = px.bar(
    bar_df, 
    x='Category', 
    y='Value',
    color='Category',
    color_discrete_map={
        'Current': '#1f77b4',
        'Forecast (Median)': '#ff7f0e',
        'Required': '#d62728',
        'Actual': '#2ca02c'
    },
    title='Balance Comparison'
)
comparison_fig.update_layout(height=250)
