import dash
from dash import callback
from dash.dependencies import Input, Output, State

# Callbacks for modal functionality
@callback(
    Output("create-group-modal", "is_open"),
    [Input("create-group-btn", "n_clicks"), 
     Input("new-group-btn", "n_clicks"),
     Input("create-group-card", "n_clicks"),
     Input("close-modal", "n_clicks"),
     Input("save-group", "n_clicks")],
    [State("create-group-modal", "is_open")],
    prevent_initial_call=True
)
def toggle_modal(n1, n2, n3, n4, n5, is_open):
    """Toggle the create group modal when any trigger button is clicked."""
    # Use callback context to determine which input triggered the callback
    ctx = dash.callback_context
    if not ctx.triggered:
        return is_open
    
    # If any button was clicked, toggle the modal
    if any([n1, n2, n3, n4, n5]):
        return not is_open
    return is_open

@callback(
    [Output("success-modal", "is_open"),
     Output("create-group-modal", "is_open", allow_duplicate=True)],
    [Input("save-group", "n_clicks")],
    [State("success-modal", "is_open"),
     State("create-group-modal", "is_open")],
    prevent_initial_call=True,
)
def show_success_modal(n, success_open, group_open):
    if n:
        return True, False
    return success_open, group_open

@callback(
    Output("success-modal", "is_open", allow_duplicate=True),
    [Input("close-success", "n_clicks")],
    [State("success-modal", "is_open")],
    prevent_initial_call=True,
)
def close_success_modal(n, is_open):
    if n:
        return False
    return is_open

@callback(
    Output("url", "pathname"),
    Input("session-store", "clear_data"),
    prevent_initial_call=True
)
def redirect_after_logout(clear_data):
    if clear_data:
        return "/"
    return dash.no_update

# Authentication mode switching callback
@callback(
    Output('auth-mode-store', 'data'),
    [Input('switch-to-register', 'n_clicks')],
    [State('auth-mode-store', 'data')],
    prevent_initial_call=True
)
def switch_to_register_mode(register_clicks, current_mode):
    """Switch to registration mode."""
    if register_clicks:
        return {'mode': 'register'}
    return current_mode

@callback(
    Output('auth-mode-store', 'data', allow_duplicate=True),
    [Input('switch-to-login', 'n_clicks')],
    [State('auth-mode-store', 'data')],
    prevent_initial_call=True
)
def switch_to_login_mode(login_clicks, current_mode):
    """Switch to login mode."""
    if login_clicks:
        return {'mode': 'login'}
    return current_mode

# User registration callback
@callback(
    [Output('session-store', 'data', allow_duplicate=True),
     Output('error-store', 'data', allow_duplicate=True)],
    [Input('register-button', 'n_clicks')],
    [State('name-input', 'value'),
     State('email-input', 'value'),
     State('password-input', 'value'),
     State('password-confirm-input', 'value')],
    prevent_initial_call=True
)
def process_registration(n_clicks, name, email, password, password_confirm):
    """Process user registration with password validation."""
    if not n_clicks:
        return dash.no_update, dash.no_update
    
    # Import here to avoid circular imports
    from auth import register_user
    import time
    import uuid
    
    # Validate inputs
    if not all([name, email, password, password_confirm]):
        return dash.no_update, {"error": "Please fill in all fields"}
    
    # Register user
    result = register_user(email, password, password_confirm, name)
    
    if result['success']:
        # Create session for newly registered user
        session_data = {
            'logged_in': True,
            'time': time.time(),
            'session_id': str(uuid.uuid4()),
            'user_info': {'email': email, 'name': name}
        }
        return session_data, {"error": ""}
    else:
        return dash.no_update, {"error": result['error']}

# Real-time password validation (client-side)
dash.clientside_callback(
    """
    function(password) {
        if (!password) {
            // Reset all to red X when password is empty
            return [
                '❌', 'text-danger',
                '❌', 'text-danger', 
                '❌', 'text-danger',
                '❌', 'text-danger'
            ];
        }
        
        // Check each requirement
        const hasLength = password.length >= 8;
        const hasUpper = /[A-Z]/.test(password);
        const hasLower = /[a-z]/.test(password);
        const hasNumber = /\\d/.test(password);
        
        return [
            hasLength ? '✅' : '❌',
            hasLength ? 'text-success' : 'text-danger',
            hasUpper ? '✅' : '❌', 
            hasUpper ? 'text-success' : 'text-danger',
            hasLower ? '✅' : '❌',
            hasLower ? 'text-success' : 'text-danger', 
            hasNumber ? '✅' : '❌',
            hasNumber ? 'text-success' : 'text-danger'
        ];
    }
    """,
    [
        Output('req-length-icon', 'children'),
        Output('req-length-item', 'className'),
        Output('req-upper-icon', 'children'),
        Output('req-upper-item', 'className'),
        Output('req-lower-icon', 'children'), 
        Output('req-lower-item', 'className'),
        Output('req-number-icon', 'children'),
        Output('req-number-item', 'className')
    ],
    [Input('password-input', 'value')]
)