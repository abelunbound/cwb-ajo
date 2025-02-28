from dash import html
import dash_bootstrap_components as dbc

def create_login_layout(error_message=""):
    """Create the login page layout"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.Br(),
                html.Br(),
                html.H2("Credit Without Borders - Ajo Platform", className="text-center"),
                html.P("Sign in to access your account", className="text-center text-muted"),
                html.Br(),
            ], width={"size": 6, "offset": 3})
        ]),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            dbc.Label("Email"),
                            dbc.Input(
                                type="email",
                                id="email-input",
                                placeholder="Enter your email",
                                className="mb-3"
                            ),
                            dbc.Label("Password"),
                            dbc.Input(
                                type="password",
                                id="password-input",
                                placeholder="Enter your password",
                                className="mb-3"
                            ),
                            dbc.Row([
                                dbc.Col([
                                    html.A("Forgot password?", href="#", className="text-muted"),
                                ], width="auto", className="ml-auto mb-3"),
                            ]),
                            html.Div(error_message, id="login-error", className="text-danger mb-3"),
                            dbc.Button(
                                "Sign In",
                                id="login-button",
                                color="primary",
                                className="w-100 mb-3",
                                n_clicks=0
                            ),
                        ]),
                        html.Hr(),
                        html.P([
                            "Don't have an account? ",
                            html.A("Sign up", href="#"),
                        ], className="text-center"),
                        html.Div([
                            html.P("Demo Credentials:", className="font-weight-bold mt-3 mb-1 text-center"),
                            html.P("Email: demo@example.com", className="mb-0 text-center text-muted small"),
                            html.P("Password: password123", className="mb-0 text-center text-muted small"),
                        ])
                    ])
                ], className="shadow-sm")
            ], width={"size": 6, "offset": 3})
        ]),
    ], fluid=True, className="py-5 bg-light")