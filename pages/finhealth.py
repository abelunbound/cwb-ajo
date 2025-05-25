import dash
from dash import dcc, html, dash_table, Input, Output, callback
import dash_bootstrap_components as dbc


from components.graph import (
    required_amount,
    filtered_fin_history_df,
    most_recent_balance, # Most recent account balance 
    forecast_accuracy,
    best_rmse_value,
    cwb_validation_assessment_df,
    model_table, 
    create_timeline_fig,
    create_30_day_forecast_timeline_fig,
    create_30_exchange_rate_fig
)

# Register the page
dash.register_page(
    __name__, 
    path="/finhealth", 
    title="Financial Health | Financial Health", 
    name="Finhealth"
)
# 

##################### Data Ingestion #####################


##################### Data Ingestion #####################
# Define as a function
# def get_financial_data():
#     required_amount = 14000
#     fin_history_enhanced_table_name = 'fin_history_enhanced'
#     fin_history = retrieve_data_from_sql(fin_history_enhanced_table_name)
    
#     # Filter and process
#     filtered_fin_history_df = fin_history.query('applicant_id == "912345678"').sort_values('date_added')
#     most_recent_balance = f"£{round(filtered_fin_history_df['balance'].iloc[-1])}"
    
#     return filtered_fin_history_df, most_recent_balance

# This data will only be loaded when the function is explicitly called
# filtered_data, balance = get_financial_data()
##########################################################

########################################################## 


# Page header component
def create_page_header():
    return html.Div(
        className="dashboard-header",
        children=[
            html.H1("Financial Health Overview", className="dashboard-title"),
            html.P("View assessment of each applicants tution affordability", className="dashboard-subtitle"),
        ]
    )

# First Row: Personal Information Card


def create_personal_data_card():
    return dbc.Card([
        dbc.CardHeader([
            html.H4("Applicant Data", className="d-inline me-2"),
            dbc.Badge("Verified", color="success")
        ]),
        dbc.CardBody([
            dbc.ListGroup([
                # Line 1: Name and Course
                dbc.ListGroupItem([
                    dbc.Row([
                        dbc.Col([
                            html.Strong("Name:", className="me-2"),
                            html.Span("Abel Johnson")
                        ], width=4),
                        dbc.Col([
                            html.Strong("Course:", className="me-2"),
                            html.Span("MSc Applied Artificial Intelligence and Data Science ")
                        ], width=8)
                    ])
                ]),
                
                # Line 2: Email and Phone
                dbc.ListGroupItem([
                    dbc.Row([
                        dbc.Col([
                            html.Strong("Email:", className="me-2"),
                            html.Span("abel.johnson@example.com")
                        ], width=4),
                        dbc.Col([
                            html.Strong("Phone:", className="me-2"),
                            html.Span("+44 7700 900000")
                        ], width=8)
                    ])
                ]),
                
                # Line 3: Session and Country
                dbc.ListGroupItem([
                    dbc.Row([
                        dbc.Col([
                            html.Strong("Session:", className="me-2"),
                            html.Span("September 2025")
                        ], width=4),
                        dbc.Col([
                            html.Strong("Country:", className="me-2"),
                            html.Span("Nigeria")
                        ], width=8)
                    ])
                ]),
            ], flush=True),
            
            # Edit button
            dbc.Button(
                "\u21A9 Back - other applicants", 
                color="primary", 
                className="mt-3"
                )
        ])
    ], className="shadow-sm")



# Extra - Affordability Card
def create_notifications_card():
    return dbc.Card(
        # dbc.CardHeader([html.H4("Tuition Affordability Assessment")]),
        dbc.CardBody([
            # html.H5("Notifications", className="card-title mb-3"),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Div([
                                html.H4("Affordability Assessment"),
                                html.Div([
                                    html.Div([
                                        html.P("Tuition & Living Expenses (£)"),
                                        html.H3(f"£{required_amount}")
                                    ], className="metric-card"),

                                    html.Div([
                                        html.P("Applicant Bank Balance"),
                                        html.H3(f"{most_recent_balance}")
                                    ], className="metric-card warning"),

                                    html.Div([
                                        html.P("Threshold met"),
                                        html.H3("Yes")
                                    ], className="metric-card danger"),
                                    html.Div([
                                        html.P("Cross-border debt/liability"),
                                        html.H3("£0")
                                    ], className="metric-card danger")

                                ], className="metrics-container")
                            ], className="card-afford"),
                        ], md=3, xs=12
                    ), 
                    dbc.Col(
                        [
                            html.Div([
                                html.Div([
                                    dbc.RadioItems(
                                        options=[
                                            {"label": "Financial History (£)  – 12 Months", "value": "option1"}, 
                                            {"label": "Volatility check  - 7-Day rolling standard deviation", "value": "option2"}
                                        ],
                                        id="radio-buttons-inline",
                                        value="option1",
                                        inline=True,
                                        className="d-flex align-items-center gap-4"
                                    ),
                                ]),
                                html.Div(
                                    id="",
                                    children=[
                                        dcc.Graph(
                                            id="timeline-chart-container",
                                            config={'displayModeBar': False}
                                                    )
                                        
                                    ]
                                )
                                ], className="card-afford1"),
                        ], md=9, xs=12
                    )
                ]
                ),
            dbc.Row(),

            

            

        ], className="card-afford2")
    )

#  Forecast Card
def create_forecast_result_card():
    return dbc.Card(
        # dbc.CardHeader([html.H4("Tuition Affordability Assessment")]),
        dbc.CardBody([
            # html.H5("Notifications", className="card-title mb-3"),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Div([
                                html.H4("Affordability Forecast"),
                                html.Div([
                                    html.Div([
                                        html.Div([
                                            html.P("Tuition and Living Expenses(£)"),
                                            html.I(
                                                className="bi bi-info-circle text-info", 
                                                id="info-tooltip",
                                                style={"cursor": "pointer"}
                                            ),
                                            ]),
                                        html.H3(cwb_validation_assessment_df[cwb_validation_assessment_df["metric"] == "Required amount"]["value"].iloc[0])
                                    ], className="metric-card"),

                                    html.Div([
                                        html.P("30th day Forecast (£)"),
                                        html.H3(cwb_validation_assessment_df[cwb_validation_assessment_df["metric"] == "Optimistic forecast (90th percentile)"]["value"].iloc[0])
                                    ], className="metric-card warning"),

                                    html.Div([
                                        html.P("Buffer amount (£)"),
                                        html.H3(cwb_validation_assessment_df[cwb_validation_assessment_df["metric"] == "Buffer amount (median forecast)"]["value"].iloc[0])
                                    ], className="metric-card danger"),
                                    html.Div([
                                        html.Span("Probability of affording payments:", className="me-2"),
                                        html.Strong(
                                            f"{cwb_validation_assessment_df[cwb_validation_assessment_df["metric"] == "Probability of meeting threshold"]["value"].iloc[0]}",
                                            style={"color": "#e53e3e", "fontStyle": "italic"}
                                            )
                                    ], )

                                ], className="metrics-container")
                            ], className="card-afford"),
                        ], md=3, xs=12
                    ), 
                    dbc.Col(
                        [
                            html.Div([
                                html.Div([
                                    dbc.RadioItems(
                                        options=[
                                            {"label": "Next 30 days Forecast  (£)", "value": "option1"}, 
                                            {"label": "Forecast vs Validation data  (£) ", "value": "option2"}
                                        ],
                                        id="forecast-radio-buttons-inline",
                                        value="option1",
                                        inline=True,
                                        className="d-flex align-items-center gap-4"
                                    ),
                                ]),
                                html.Div(
                                    id="",
                                    children=[
                                        dcc.Graph(
                                            id="forecast-timeline-chart-container",
                                            config={'displayModeBar': False}
                                                    )
                                        
                                    ]
                                )
                                ], className="card-afford1"),
                        ], md=9, xs=12
                    )
                ]
                ),
            dbc.Row(),

            

            

        ], className="card-afford2")
    )

#  Forecast Card
def create_model_explain():
    return dbc.Card(
        # dbc.CardHeader([html.H4("Tuition Affordability Assessment")]),
        dbc.CardBody(
            
            [
            
            html.H4("Model Hyperparameters & Evaluation", className="mb-3 text-center"),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Div([
                                # html.H4("Model Transparency"),
                                html.Div([
                                    html.Div([
                                        html.Div([
                                            html.P("Root Mean Squared Error (RMSE)"),
                                            
                                            ]),
                                        html.H3(f"£{best_rmse_value}")
                                    ], className="metric-card warning"),

                                    html.Div([
                                        html.P("Forecast Accuracy"),
                                        html.H3(f"{forecast_accuracy}%")
                                    ], className="metric-card warning"),

                                    html.Div([
                                        html.P("Context Length"),
                                        html.H3(f"{cwb_validation_assessment_df[cwb_validation_assessment_df["metric"] == "model_kwargs.cardinality.context_length"]["value"].iloc[0]}")
                                    ], className="metric-card danger"),
                                    html.Div([
                                        html.P("Number of features"),
                                        html.H3(f"{cwb_validation_assessment_df[cwb_validation_assessment_df["metric"] == "num_feat_dynamic_real"]["value"].iloc[0]}")
                                    ], className="metric-card danger"),

                                ], className="metrics-container")
                            ], className="card-afford"),
                        ], md=3, xs=12
                    ), 
                    dbc.Col(
                        [
                            
                            html.Div([
                                
                                model_table
                             

                                ], className="card-afford1"),
                        ], md=9, xs=12
                    )
                ]
                ),
            dbc.Row(),

            

            

        ], className="card-afford2",)
    )

#  Exchange Rate Volatility
def create_exchange_rate_volatility_card():
    return dbc.Card(
        # dbc.CardHeader([html.H4("Tuition Affordability Assessment")]),
        dbc.CardBody(
            
            [
            
            # html.H4("Model Hyperparameters & Evaluation", className="mb-3 text-center"),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Div([
                                html.H4("Exchange Rate Volatility Risks"),
                                html.Div([
                                    html.Div([
                                        html.Div([
                                            html.P("Country"),
                                            ]),
                                        html.H3("Nigeria: NGN-GBP")
                                    ], className="metric-card warning"),
                                    html.Div([
                                        html.Strong("5 years:", className="me-2"),
                                        html.Span("325% \U0001F53B")
                                    ], className=""),

                                    html.Div([
                                        html.Strong("3 years:", className="me-2"),
                                        html.Span("20% \U0001F53B", style={"color": "red"})
                                    ], className=""),
                                    html.Div([
                                        html.Strong("1 year:", className="me-2"),
                                        html.Span("20% \U0001F53B", style={"color": "red"})
                                    ], className=""),
                                    html.Div([
                                        html.Strong("6-Months:", className="me-2"),
                                        html.Span("20% \U0001F53B", style={"color": "red"})
                                    ], className=""),
                                    html.Div([
                                        html.Strong("30-days forecast:", className="me-2"),
                                        html.Span("20% \U0001F53B", style={"color": "red"})
                                    ], className=""),
                                    

                                ], className="metrics-container")
                            ], className="card-afford"),
                        ], md=3, xs=12
                    ), 
                    dbc.Col(
                        [
                            html.Div([
                                html.Div([
                                    dbc.RadioItems(
                                        options=[
                                            {"label": "Next 30 days Forecast  (£)", "value": "option1"}, 
                                            {"label": "Forecast vs Validation data  (£) ", "value": "option2"}
                                        ],
                                        id="exchange-rate-radio-buttons-inline",
                                        value="option1",
                                        inline=True,
                                        className="d-flex align-items-center gap-4"
                                    ),
                                ]),
                                html.Div(
                                    id="",
                                    children=[
                                        dcc.Graph(
                                            id="exchange-rate-timeline-chart-container",
                                            config={'displayModeBar': False}
                                                    )
                                        
                                    ]
                                )
                            ], className="card-afford1"),
                        ], md=9, xs=12
                    )
                ]
                ),
            dbc.Row(),

            

            

        ], className="card-afford2",)
    )


# Change from static layout to function-based layout
def layout():
    return html.Div([
        # Page Header
        create_page_header(),
        
        # Container for all profile sections
        dbc.Container([
            # First Row: Personal Information
            html.Div(className="mb-4", children=[ create_personal_data_card()]),
            
            
            # Second Row: Assessments
            html.Div(children=[
                dbc.Row([
                    dbc.Col(create_notifications_card(), width=12)
                ])
            ]),
            html.Br(),
            # Third Row: Forecasts
            html.Div(children=[
                dbc.Row([
                    dbc.Col(create_forecast_result_card(), width=12)
                ])
            ]),
            html.Br(),
            # Fourth Row: Exchange Rate volatility
            html.Div(children=[
                dbc.Row([
                    dbc.Col(create_exchange_rate_volatility_card(), width=12)
                ])
            ]),
            html.Br(),
            # Fourth Row: Model Transparency
            html.Div(children=[
                dbc.Row([
                    dbc.Col(create_model_explain(), width=12)
                ])
            ]),
        ])
    ])



@callback(
    Output("timeline-chart-container", "figure"),
    Input("radio-buttons-inline", "value") 
)
def update_timeline_chart(selected_option):
    return create_timeline_fig(selected_option)

# Forecast chart callback
@callback(
    Output("forecast-timeline-chart-container", "figure"),
    Input("forecast-radio-buttons-inline", "value") 
)
def update_balance_forecast_chart(selected_option):
    return create_30_day_forecast_timeline_fig(selected_option)

# Exchange Rate chart callback
@callback(
    Output("exchange-rate-timeline-chart-container", "figure"),
    Input("exchange-rate-radio-buttons-inline", "value") 
)
def update_balance_exchange_rate_chart(selected_option):
    return create_30_exchange_rate_fig(selected_option)
