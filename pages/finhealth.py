import dash
from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc


from components.graph import affordability_df, timeline_fig, gauge_fig, model_table

# Register the page
dash.register_page(
    __name__, 
    path="/finhealth", 
    title="Profile | Financial Health", 
    name="Finhealth"
)
# 
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



def create_personal_info_card():
    return dbc.Card(
        dbc.CardBody([
            # Verified Badge in top right corner
            html.Div(
                "Verified", 
                className="position-absolute badge", 
                style={
                    "top": "10px", 
                    "right": "10px",
                    "backgroundColor": "rgba(46, 204, 113, 0.15)", 
                    "color": "#2ECC71"
                }
            ),
            dbc.Row([
                dbc.Col([
                    html.H4("Personal Information", className="card-title mb-4"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("First Name"),
                            dbc.Input(
                                type="text", 
                                placeholder="Enter first name", 
                                value="Abel",
                                className="mb-3"
                            )
                        ], width=6),
                        dbc.Col([
                            dbc.Label("Last Name"),
                            dbc.Input(
                                type="text", 
                                placeholder="Enter last name", 
                                value="Johnson",
                                className="mb-3"
                            )
                        ], width=6),
                        
                        dbc.Col([
                            dbc.Label("Email Address"),
                            dbc.Input(
                                type="email", 
                                placeholder="Enter email", 
                                value="abel.johnson@example.com",
                                className="mb-3"
                            )
                        ], width=12),
                        
                        dbc.Col([
                            dbc.Label("Phone Number"),
                            dbc.InputGroup([
                                dbc.InputGroupText("+44"),
                                dbc.Input(
                                    type="tel", 
                                    placeholder="Phone number", 
                                    value="7700 900000"
                                )
                            ], className="mb-3")
                        ], width=12),
                        
                        dbc.Col([
                            dbc.Button("Update Profile", color="primary")
                        ], width=12)
                    ])
                ], width=12)
            ])
        ], className="position-relative")
    )

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
                                html.H4("Tuition Affordability Assessment"),
                                html.Div([
                                    html.Div([
                                        html.P("Required Tuition Amount"),
                                        html.H3(affordability_df[affordability_df["Metric"] == "Required amount"]["Value"].iloc[0])
                                    ], className="metric-card"),

                                    html.Div([
                                        html.P("Applicant Bank Balance"),
                                        html.H3(affordability_df[affordability_df["Metric"] == "Required amount"]["Value"].iloc[0])
                                    ], className="metric-card warning"),

                                    html.Div([
                                        html.P("Threshold met"),
                                        html.H3(affordability_df[affordability_df["Metric"] == "Assessment"]["Value"].iloc[0])
                                    ], className="metric-card danger"),
                                    html.Div([
                                        html.P("Pending liability"),
                                        html.H3(affordability_df[affordability_df["Metric"] == "Assessment"]["Value"].iloc[0])
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
                                dcc.Graph(
                                    figure=timeline_fig,
                                    config={'displayModeBar': False},
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
                                            html.P("Next Installment Amount"),
                                            html.I(
                                                className="bi bi-info-circle text-info", 
                                                id="info-tooltip",
                                                style={"cursor": "pointer"}
                                            ),
                                            ]),
                                        html.H3(affordability_df[affordability_df["Metric"] == "Required amount"]["Value"].iloc[0])
                                    ], className="metric-card"),

                                    html.Div([
                                        html.P("Best Case forecast (£)"),
                                        html.H3(affordability_df[affordability_df["Metric"] == "Required amount"]["Value"].iloc[0])
                                    ], className="metric-card warning"),

                                    html.Div([
                                        html.P("Buffer amount (£)"),
                                        html.H3(affordability_df[affordability_df["Metric"] == "Assessment"]["Value"].iloc[0])
                                    ], className="metric-card danger"),
                                    html.Div([
                                        html.Span("Probability of meeting threshold:", className="me-2"),
                                        html.Strong(
                                            "50%",
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
                                        id="radio-buttons-inline",
                                        value="option1",
                                        inline=True,
                                        className="d-flex align-items-center gap-4"
                                    ),
                                ]),
                                dcc.Graph(
                                    figure=timeline_fig,
                                    config={'displayModeBar': False},
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
                                # html.H4("Affordability Forecast"),
                                html.Div([
                                    html.Div([
                                        html.Div([
                                            html.P("Root Mean Squared Error (RMSE)"),
                                            
                                            ]),
                                        html.H3(affordability_df[affordability_df["Metric"] == "Required amount"]["Value"].iloc[0])
                                    ], className="metric-card"),

                                    html.Div([
                                        html.P("Number of features"),
                                        html.H3(affordability_df[affordability_df["Metric"] == "Required amount"]["Value"].iloc[0])
                                    ], className="metric-card warning"),

                                    html.Div([
                                        html.P("Number of Samples"),
                                        html.H3(affordability_df[affordability_df["Metric"] == "Assessment"]["Value"].iloc[0])
                                    ], className="metric-card danger"),
                                    html.Div([
                                        html.P("Prediction length"),
                                        html.H3(affordability_df[affordability_df["Metric"] == "Assessment"]["Value"].iloc[0])
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


# Change from static layout to function-based layout
def layout():
    return html.Div([
        # Page Header
        create_page_header(),
        
        # Container for all profile sections
        dbc.Container([
            # First Row: Personal Information
            html.Div(className="mb-4", children=[ create_personal_data_card()]),
            
            
            # Second Row: Notifications
            html.Div(children=[
                dbc.Row([
                    dbc.Col(create_notifications_card(), width=12)
                ])
            ]),
            html.Br(),
            # Third Row: Notifications
            html.Div(children=[
                dbc.Row([
                    dbc.Col(create_forecast_result_card(), width=12)
                ])
            ]),
            html.Br(),
            # Fourth Row: Notifications
            html.Div(children=[
                dbc.Row([
                    dbc.Col(create_model_explain(), width=12)
                ])
            ])
        ])
    ])