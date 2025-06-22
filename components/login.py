from dash import html, dcc
import dash_bootstrap_components as dbc

def create_login_layout(error_message="", mode="login"):
    """Create the login/registration page layout.
    
    Args:
        error_message (str): Error message to display
        mode (str): Either 'login' or 'register' to determine which form to show
        
    Returns:
        dbc.Container: The login/registration layout
    """
    # Determine form content based on mode
    if mode == "register":
        title = "Create Your Account"
        subtitle = "Join the Ajo Community Savings Platform"
        form_content = _create_registration_form(error_message)
        toggle_text = "Already have an account? "
        toggle_link = "Sign in"
        toggle_id = "switch-to-login"
    else:
        title = "Credit Without Borders - Ajo Platform"
        subtitle = "Sign in to access your account"
        form_content = _create_login_form(error_message)
        toggle_text = "Don't have an account? "
        toggle_link = "Sign up"
        toggle_id = "switch-to-register"
    
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.Br(),
                html.Br(),
                html.H2(title, className="text-center"),
                html.P(subtitle, className="text-center text-muted"),
                html.Br(),
            ], width={"size": 6, "offset": 3})
        ]),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        form_content,
                        html.Hr(),
                        html.P([
                            toggle_text,
                            html.A(toggle_link, href="#", id=toggle_id),
                        ], className="text-center"),
                        _create_demo_credentials() if mode == "login" else html.Div()
                    ])
                ], className="shadow-sm")
            ], width={"size": 6, "offset": 3})
        ]),
    ], fluid=True, className="py-5 bg-light")

def _create_login_form(error_message=""):
    """Create the login form fields.
    
    Args:
        error_message (str): Error message to display
        
    Returns:
        html.Div: Login form content
    """
    return html.Div([
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
    ])

def _create_registration_form(error_message=""):
    """Create the registration form fields.
    
    Args:
        error_message (str): Error message to display
        
    Returns:
        html.Div: Registration form content
    """
    return html.Div([
        dbc.Label("Full Name"),
        dbc.Input(
            type="text",
            id="name-input",
            placeholder="Enter your full name",
            className="mb-3"
        ),
        dbc.Label("Email"),
        dbc.Input(
            type="email",
            id="email-input",
            placeholder="Enter your email address",
            className="mb-3"
        ),
        dbc.Label("Password"),
        dbc.Input(
            type="password",
            id="password-input",
            placeholder="Create a password",
            className="mb-2"
        ),
        # Password requirements
        html.Div([
            html.Small("Password must contain:", className="text-muted"),
            html.Ul([
                html.Li([
                    html.Span("At least 8 characters", id="req-length"),
                    html.Span(" ❌", id="req-length-icon", className="ms-1")
                ], className="small", id="req-length-item"),
                html.Li([
                    html.Span("One uppercase letter", id="req-upper"),
                    html.Span(" ❌", id="req-upper-icon", className="ms-1")
                ], className="small", id="req-upper-item"),
                html.Li([
                    html.Span("One lowercase letter", id="req-lower"),
                    html.Span(" ❌", id="req-lower-icon", className="ms-1")
                ], className="small", id="req-lower-item"),
                html.Li([
                    html.Span("One number", id="req-number"),
                    html.Span(" ❌", id="req-number-icon", className="ms-1")
                ], className="small", id="req-number-item"),
            ], className="mb-3 small")
        ]),
        dbc.Label("Confirm Password"),
        dbc.Input(
            type="password",
            id="password-confirm-input",
            placeholder="Confirm your password",
            className="mb-3"
        ),
        html.Div(error_message, id="register-error", className="text-danger mb-3"),
        dbc.Button(
            "Create Account",
            id="register-button",
            color="primary",
            className="w-100 mb-3",
            n_clicks=0
        ),
    ])

def _create_demo_credentials():
    """Create demo credentials display for login mode.
    
    Returns:
        html.Div: Demo credentials section
    """
    return html.Div([
                            html.P("Demo Credentials:", className="font-weight-bold mt-3 mb-1 text-center"),
                            html.P("Email: demo@example.com", className="mb-0 text-center text-muted small"),
                            html.P("Password: password123", className="mb-0 text-center text-muted small"),
                        ])