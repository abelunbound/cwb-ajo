# import dash
# from dash import html, dcc
# import dash_bootstrap_components as dbc


# # Initialize the Dash app with multi-page support
# app = dash.Dash(
#     __name__,
#     external_stylesheets=[
#         dbc.themes.BOOTSTRAP,
#         'https://use.fontawesome.com/releases/v5.15.1/css/all.css'
#     ],
#     suppress_callback_exceptions=True,
#     use_pages=True,  # Enable pages
#     meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}]
# )

# # Define colors for global use
# colors = {
#     'primary': '#5F2EEA',
#     'primary-light': '#8A6EF3',
#     'primary-dark': '#4A1FB8',
#     'success': '#2ECC71',
#     'success-light': '#4CD787',
#     'warning': '#F7B731',
#     'danger': '#E74C3C',
#     'dark': '#333333',
#     'text': '#545454',
#     'light-gray': '#F5F5F5',
#     'medium-gray': '#E0E0E0',
#     'white': '#FFFFFF',
# }

# # Custom CSS for the app
# app.index_string = '''
# <!DOCTYPE html>
# <html>
#     <head>
#         {%metas%}
#         <title>Ajo - Community Savings Platform</title>
#         {%favicon%}
#         {%css%}
#         <style>
            
#         </style>
#     </head>
#     <body>
#         {%app_entry%}
#         <footer>
#             {%config%}
#             {%scripts%}
#             {%renderer%}
#         </footer>
#     </body>
# </html>
# '''

# # Header Navigation component 
# def create_header():
#     return html.Header(
#         className="header mb-4",
#         children=[
#             html.Div(
#                 className="container",
#                 children=[
#                     html.Div(
#                         className="d-flex justify-content-between align-items-center",
#                         children=[
#                             html.A("CWB", className="logo", href="/"),
#                             html.Nav(
#                                 className="d-none d-md-block",
#                                 children=[
#                                     html.Ul(
#                                         className="nav",
#                                         children=[
#                                             html.Li(html.A("Dashboard", href="/", className="nav-link active")),
#                                             html.Li(html.A("My Groups", href="/groups", className="nav-link")),
#                                             html.Li(html.A("Payments", href="/payments", className="nav-link")),
#                                             html.Li(html.A("Support", href="/support", className="nav-link")),
#                                         ]
#                                     )
#                                 ]
#                             ),
#                             html.Div(
#                                 className="d-flex",
#                                 children=[
#                                     dbc.Button("Profile", color="", className="btn-outline-primary me-2", href="/profile"),
#                                     dbc.Button("+ Create Group", color="primary", className="d-none", id="create-group-btn"),
#                                     dbc.Button("Logout", color="primary", className="", id="logout-test"),
#                                 ]
#                             )
#                         ]
#                     )
#                 ]
#             )
#         ]
#     )

# # Main layout with page container
# app.layout = html.Div([
#     # Header/Navigation
#     create_header(),
    
#     # Page content - this is where pages will be loaded
#     html.Main(
#         className="dashboard",
#         children=[
#             html.Div(
#                 className="container",
#                 children=[
#                     # This is where the current page content will be rendered
#                     dash.page_container
#                 ]
#             )
#         ]
#     )
# ])



# # For development
# if __name__ == '__main__':
#     app.run_server(debug=True, use_reloader=True)


import dash
from dash import html, dcc, callback
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import time
import uuid

# Import authentication components
from components.login import create_login_layout
from auth import USERS_DB, SESSION_TIMEOUT, validate_user


from components.graph import (
    create_timeline_fig
)


# 
# Initialize the Dash app with multi-page support
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        'https://use.fontawesome.com/releases/v5.15.1/css/all.css'
    ],
    suppress_callback_exceptions=True,
    use_pages=True,  # Enable pages
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}]
)
server = app.server  # Expose the Flask server


# Define colors for global use
colors = {
    'primary': '#5F2EEA',
    'primary-light': '#8A6EF3',
    'primary-dark': '#4A1FB8',
    'success': '#2ECC71',
    'success-light': '#4CD787',
    'warning': '#F7B731',
    'danger': '#E74C3C',
    'dark': '#333333',
    'text': '#545454',
    'light-gray': '#F5F5F5',
    'medium-gray': '#E0E0E0',
    'white': '#FFFFFF',
}

# Custom CSS for the app
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>Ajo - Community Savings Platform</title>
        {%favicon%}
        {%css%}
        <style>
            
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Header Navigation component 
def create_header():
    return html.Header(
        className="header mb-4",
        children=[
            html.Div(
                className="container",
                children=[
                    html.Div(
                        className="d-flex justify-content-between align-items-center",
                        children=[
                            html.A("CWB", className="logo", href="/"),
                            html.Nav(
                                className="d-none d-md-block",
                                children=[
                                    html.Ul(
                                        className="nav",
                                        children=[
                                            html.Li(html.A("Dashboard", href="/", className="nav-link active")),
                                            html.Li(html.A("My Groups", href="/groups", className="nav-link")),
                                            html.Li(html.A("Payments", href="/payments", className="nav-link")),
                                            html.Li(html.A("Support", href="/support", className="nav-link")),
                                            html.Li(html.A("FinHealth", href="/finhealth", className="nav-link")),
                                        ]
                                    )
                                ]
                            ),
                            html.Div(
                                className="d-flex",
                                children=[
                                    dbc.Button("Profile", color="", className="btn-outline-primary me-2", href="/profile"),
                                    dbc.Button("+ Create Group", color="primary", className="me-2", id="create-group-btn"),
                                    dbc.Button("Logout", color="danger", className="", id="logout-btn"),
                                ]
                            )
                        ]
                    )
                ]
            )
        ]
    )

# Authentication wrapper layout
def serve_layout():
    return html.Div([
        dcc.Location(id='url', refresh=False),
        # Session stores
        dcc.Store(id='session-store', storage_type='session'),
        dcc.Store(id='error-store', storage_type='memory'),
        
        # Conditional content based on authentication
        html.Div(id='page-content')
    ])

# Set app layout
app.layout = serve_layout

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
    
    # Use the validate_user function from auth.py
    user_data = validate_user(email, password)
    if not user_data:
        return dash.no_update, {"error": "Invalid email or password"}
    
    # Create session
    session_data = {
        'logged_in': True,
        'time': time.time(),
        'session_id': str(uuid.uuid4()),
        'user_info': user_data
    }
    
    return session_data, {"error": ""}

# Callback for logout
@app.callback(
    Output('session-store', 'clear_data'),
    Input('logout-btn', 'n_clicks'),
    prevent_initial_call=True
)
def logout(n_clicks):
    if n_clicks:
        return True
    return dash.no_update

# Callback to display the correct page content based on authentication
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
    
    # Check if user is logged in
    is_authenticated = False
    if session_data and session_data.get('logged_in'):
        # Check if session is expired
        if time.time() - session_data.get('time', 0) <= SESSION_TIMEOUT:
            is_authenticated = True
    
    # If not authenticated, always show login page
    if not is_authenticated:
        return create_login_layout(error_message)
    
    # If authenticated, show the app with header and page content
    return html.Div([
        # Header/Navigation
        create_header(),
        
        # Page content
        html.Main(
            className="dashboard",
            children=[
                html.Div(
                    className="container",
                    children=[
                        # This is where the current page content will be rendered
                        dash.page_container
                    ]
                )
            ]
        )
    ])

# Import callbacks
# import callbacks

# callbacks 



# For development

if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)
else:
    # This branch is used by App Engine
    server = app.server

# print("Registered pages:")
# for page in dash.page_registry.values():
#     print(page["module"], "→", page["path"])