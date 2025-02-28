import dash
from dash import dcc, html, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import datetime
import uuid
import time
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize the app with Bootastrap for styling
app = dash.Dash(__name__, 
                external_stylesheets=[dbc.themes.BOOTSTRAP],
                suppress_callback_exceptions=True,
                prevent_initial_callbacks=True)  # Prevent all callbacks from firing at startup

# Mock user database - in production, replace with real database
USERS_DB = {
    'demo@example.com': {
        'password': generate_password_hash('password123'),
        'name': 'Demo User',
        'created': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    'admin@example.com': {
        'password': generate_password_hash('admin123'),
        'name': 'Admin User',
        'created': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
}

# Session timeout (24 hours)
SESSION_TIMEOUT = 24 * 60 * 60  # in seconds

# Login page layout
def create_login_layout(error_message=""):
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.Br(),
                html.Br(),
                html.H2("Welcome", className="text-center"),
                html.P("Sign in to continue", className="text-center text-muted"),
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

# Simple welcome page layout
def create_welcome_layout(username):
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.Br(),
                html.H1(f"Welcome, {username}!", className="text-center"),
                html.P("You have successfully logged in.", className="text-center"),
                html.Br(),
                dbc.Button(
                    "Logout",
                    id="logout-button",
                    color="primary",
                    className="d-block mx-auto"
                ),
            ], width={"size": 6, "offset": 3})
        ]),
    ])

# Main app layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),  # Don't refresh the page
    html.Div(id='page-content'),
    dcc.Store(id='session-store', storage_type='session'),
    dcc.Store(id='error-store', storage_type='memory')
])

# Callback to handle authentication
@app.callback(
    [Output('session-store', 'data'),
     Output('error-store', 'data')],

    [Input('login-button', 'n_clicks')],

    [State('email-input', 'value'),
     State('password-input', 'value'),
     State('session-store', 'data')],
    prevent_initial_call=True
)
def process_login(n_clicks, email, password, session_data):
    if not n_clicks:
        return dash.no_update, dash.no_update
    
    # Validate inputs
    if not email or not password:
        return dash.no_update, {"error": "Please enter email and password"}
    
    # Check if user exists
    if email not in USERS_DB:
        return dash.no_update, {"error": "Invalid email"}
    
    # Check password
    if not check_password_hash(USERS_DB[email]['password'], password):
        return dash.no_update, {"error": "Invalid password"}
    
    # Create session
    session_data = {
        'logged_in': True,
        'time': time.time(),
        'session_id': str(uuid.uuid4()),
        'user_info': {
            'email': email,
            'name': USERS_DB[email]['name']
        }
    }
    
    return session_data, {"error": ""}

# Callback for logout
@app.callback(
    Output('session-store', 'clear_data'),
    Input('logout-button', 'n_clicks'),
    prevent_initial_call=True
)
def logout(n_clicks):
    if n_clicks:
        return True
    return dash.no_update

# Callback to update URL after authentication state changes
@app.callback(
    Output('url', 'pathname'),
    [Input('session-store', 'data'),
     Input('session-store', 'clear_data')],
    prevent_initial_call=True
)
def update_url(session_data, clear_data):
    ctx = callback_context
    
    if ctx.triggered_id == 'session-store' and session_data and session_data.get('logged_in'):
        return '/welcome'
    
    if ctx.triggered_id == 'session-store.clear_data':
        return '/'
    
    return dash.no_update

# Callback to handle page content
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname'),
     Input('session-store', 'data'),
     Input('error-store', 'data')]
)
def display_page(pathname, session_data, error_data):
    error_message = ""
    if error_data and 'error' in error_data:
        error_message = error_data['error']
    
    # If user is logged in
    if session_data and session_data.get('logged_in'):
        # Check if session is expired
        if time.time() - session_data.get('time', 0) > SESSION_TIMEOUT:
            # Session expired
            return create_login_layout("Session expired. Please log in again.")
        
        # Show welcome page for logged in users
        if pathname == '/welcome':
            username = session_data.get('user_info', {}).get('name', 'User')
            return create_welcome_layout(username)
    
    # Show login page for non-logged in users or unknown paths
    return create_login_layout(error_message)

if __name__ == '__main__':
    app.run_server(debug=True)