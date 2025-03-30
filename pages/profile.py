import dash
from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc



# Register the page
dash.register_page(
    __name__, 
    path="/profile", 
    title="Profile | Ajo", 
    name="Profile"
)

# Page header component
def create_page_header():
    return html.Div(
        className="dashboard-header",
        children=[
            html.H1("Profile Overview", className="dashboard-title"),
            html.P("Manage and complete your profile details", className="dashboard-subtitle"),
        ]
    )

# First Row: Personal Information Card
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

# Second Row: Timeline Cards
def create_timeline_cards():
    # Affordability Check Card
    affordability_card = dbc.Card(
        dbc.CardBody([
            html.Div(
                "Pending", 
                className="position-absolute badge", 
                style={
                    "top": "10px", 
                    "right": "10px",
                    "backgroundColor": "rgba(231, 76, 60, 0.15)", 
                    "color": "#E74C3C"
                }
            ),
            html.Div([
                html.I(className="fas fa-chart-pie mb-3", style={"fontSize": "36px", "color": "#5F2EEA"}),
                html.H5("Affordability Check", className="mb-3"),
                html.P("Verify your income and expenses", className="text-muted mb-3"),
                dbc.Button("Start Check", color="primary", outline=True)
            ], className="text-center")
        ]),
        className="h-100 position-relative"
    )

    # Credit Check Card
    credit_check_card = dbc.Card(
        dbc.CardBody([
            html.Div(
                "Pending", 
                className="position-absolute badge", 
                style={
                    "top": "10px", 
                    "right": "10px",
                    "backgroundColor": "rgba(231, 76, 60, 0.15)", 
                    "color": "#E74C3C"
                }
            ),
            html.Div([
                html.I(className="fas fa-chart-line mb-3", style={"fontSize": "36px", "color": "#5F2EEA"}),
                html.H5("Credit Check", className="mb-3"),
                html.P("Soft credit check for group trust", className="text-muted mb-3"),
                dbc.Button("Perform Check", color="primary", outline=True)
            ], className="text-center")
        ]),
        className="h-100 position-relative"
    )

    # Direct Debit Card
    direct_debit_card = dbc.Card(
        dbc.CardBody([
            html.Div(
                "Pending", 
                className="position-absolute badge", 
                style={
                    "top": "10px", 
                    "right": "10px",
                    "backgroundColor": "rgba(231, 76, 60, 0.15)", 
                    "color": "#E74C3C"
                }
            ),
            html.Div([
                html.I(className="fas fa-credit-card mb-3", style={"fontSize": "36px", "color": "#5F2EEA"}),
                html.H5("Setup Direct Debit", className="mb-3"),
                html.P("Configure automatic contributions", className="text-muted mb-3"),
                dbc.Button("Add Bank Details", color="primary", outline=True)
            ], className="text-center")
        ]),
        className="h-100 position-relative"
    )

    return dbc.Row([
        dbc.Col(affordability_card, width=4),
        dbc.Col(credit_check_card, width=4),
        dbc.Col(direct_debit_card, width=4)
    ])

# Account Settings Card
def create_account_settings_card():
    return dbc.Card(
        dbc.CardBody([
            html.H5("Account Settings", className="card-title mb-3"),
            html.Div([
                html.Div(
                    className="mb-3",
                    children=[
                        html.Label("Language", className="mb-2"),
                        dbc.Select(
                            options=[
                                {"label": "English", "value": "en"},
                                {"label": "French", "value": "fr"},
                                {"label": "Spanish", "value": "es"}
                            ],
                            value="en"
                        )
                    ]
                ),
                html.Div(
                    className="mb-3",
                    children=[
                        html.Label("Currency", className="mb-2"),
                        dbc.Select(
                            options=[
                                {"label": "£ British Pound", "value": "GBP"},
                                {"label": "$ US Dollar", "value": "USD"},
                                {"label": "€ Euro", "value": "EUR"}
                            ],
                            value="GBP"
                        )
                    ]
                ),
                html.Div(
                    className="mb-3",
                    children=[
                        html.Label("Theme", className="mb-2"),
                        dbc.RadioItems(
                            options=[
                                {"label": "Light Mode", "value": "light"},
                                {"label": "Dark Mode", "value": "dark"}
                            ],
                            value="light",
                            inline=True
                        )
                    ]
                ),
                dbc.Button("Save Preferences", color="primary", outline=True)
            ])
        ])
    )

# Security Card
def create_security_card():
    return dbc.Card(
        dbc.CardBody([
            html.H5("Security", className="card-title mb-3"),
            html.Div([
                html.Div(
                    className="mb-3",
                    children=[
                        html.Label("Change Password", className="mb-2"),
                        dbc.Input(
                            type="password", 
                            placeholder="Current Password", 
                            className="mb-2"
                        ),
                        dbc.Input(
                            type="password", 
                            placeholder="New Password", 
                            className="mb-2"
                        ),
                        dbc.Input(
                            type="password", 
                            placeholder="Confirm New Password", 
                            className="mb-3"
                        ),
                        dbc.Button("Update Password", color="primary", outline=True)
                    ]
                ),
                html.Div(
                    className="mb-3",
                    children=[
                        html.Label("Two-Factor Authentication", className="mb-2"),
                        dbc.Row([
                            dbc.Col([
                                html.P("Add an extra layer of security to your account", className="mb-2"),
                                dbc.Button(
                                    "Enable 2FA", 
                                    color="primary", 
                                    outline=True,
                                    className="me-2"
                                ),
                            ], width=8),
                            dbc.Col([
                                html.Div(
                                    className="text-muted small",
                                    children=[
                                        html.I(className="fas fa-info-circle me-2"),
                                        "Recommended for added security"
                                    ]
                                )
                            ], width=4),
                        ])
                    ]
                )
            ])
        ])
    )


# Change from static layout to function-based layout
def layout():
    return html.Div([
        # Page Header
        create_page_header(),
        
        # Container for all profile sections
        dbc.Container([
            # First Row: Personal Information
            html.Div(className="mb-4", children=[create_personal_info_card()]),
            
            # Second Row: Timeline Cards
            html.Div(className="mb-4", children=[create_timeline_cards()]),
            
            # Third Row: Account Settings
            html.Div(className="mb-4", children=[
                dbc.Row([
                    dbc.Col(create_account_settings_card(), width=12)
                ])
            ]),
            
            # Fourth Row: Security
            html.Div(className="mb-4", children=[
                dbc.Row([
                    dbc.Col(create_security_card(), width=12)
                ])
            ]),
            
            # # Fifth Row: Notifications
            # html.Div(children=[
            #     dbc.Row([
            #         dbc.Col(create_notifications_card(), width=12)
            #     ])
            # ])
        ])
    ])