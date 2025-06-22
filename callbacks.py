import dash
from dash import callback
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from datetime import datetime, date, timedelta
from decimal import Decimal

# Group Modal Toggle Callbacks
@callback(
    Output("create-group-modal", "is_open"),
    [Input("create-group-btn", "n_clicks"), 
     Input("new-group-btn", "n_clicks"),
     Input("create-group-card", "n_clicks"),
     Input("cancel-group-btn", "n_clicks")],
    [State("create-group-modal", "is_open")],
    prevent_initial_call=True
)
def toggle_group_modal(create_clicks, new_clicks, card_clicks, cancel_clicks, is_open):
    """Toggle the create group modal when any trigger button is clicked."""
    ctx = dash.callback_context
    if not ctx.triggered:
        return is_open
    
    # If any button was clicked, toggle the modal
    if any([create_clicks, new_clicks, card_clicks, cancel_clicks]):
        return not is_open
    return is_open

# Group Creation Form Validation and Submission
@callback(
    [Output("form-validation-alert", "children"),
     Output("group-name-feedback", "children"),
     Output("contribution-amount-feedback", "children"),
     Output("frequency-feedback", "children"),
     Output("duration-feedback", "children"),
     Output("max-members-feedback", "children"),
     Output("start-date-feedback", "children"),
     Output("create-group-btn", "disabled"),
     Output("success-modal", "is_open"),
     Output("create-group-modal", "is_open", allow_duplicate=True),
     Output("success-message-text", "children")],
    [Input("create-group-btn", "n_clicks")],
    [State("group-name-input", "value"),
     State("group-description-input", "value"),
     State("contribution-amount-input", "value"),
     State("frequency-input", "value"),
     State("duration-input", "value"),
     State("max-members-input", "value"),
     State("start-date-input", "value"),
     State("session-store", "data")],
    prevent_initial_call=True
)
def handle_group_creation(n_clicks, name, description, amount, frequency, duration, max_members, start_date, session_data):
    """Handle group creation form validation and submission."""
    if not n_clicks:
        return [dash.no_update] * 11
    
    # Initialize validation results
    validation_alert = ""
    name_feedback = ""
    amount_feedback = ""
    frequency_feedback = ""
    duration_feedback = ""
    members_feedback = ""
    date_feedback = ""
    form_valid = True
    
    # Validate required fields
    if not name or len(name.strip()) < 3:
        name_feedback = "Group name must be at least 3 characters long"
        form_valid = False
    elif len(name.strip()) > 100:
        name_feedback = "Group name must be less than 100 characters"
        form_valid = False
    
    if not amount:
        amount_feedback = "Please select a contribution amount"
        form_valid = False
    elif amount not in [50, 100, 500, 800]:
        amount_feedback = "Please select a valid contribution amount"
        form_valid = False
    
    if not frequency:
        frequency_feedback = "Please select a contribution frequency"
        form_valid = False
    elif frequency not in ["weekly", "monthly"]:
        frequency_feedback = "Please select a valid frequency"
        form_valid = False
    
    if not duration:
        duration_feedback = "Please enter the duration in months"
        form_valid = False
    elif not isinstance(duration, int) or duration < 3 or duration > 24:
        duration_feedback = "Duration must be between 3 and 24 months"
        form_valid = False
    
    if not max_members:
        members_feedback = "Please select maximum number of members"
        form_valid = False
    elif max_members not in [5, 6, 7, 8, 9, 10]:
        members_feedback = "Please select a valid number of members (5-10)"
        form_valid = False
    
    if not start_date:
        date_feedback = "Please select a start date"
        form_valid = False
    else:
        try:
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
            today = date.today()
            if start_date_obj <= today:
                date_feedback = "Start date must be in the future"
                form_valid = False
            elif start_date_obj > today + timedelta(days=90):
                date_feedback = "Start date cannot be more than 90 days in the future"
                form_valid = False
        except ValueError:
            date_feedback = "Please enter a valid date"
            form_valid = False
    
    # Check if user is logged in
    if not session_data or not session_data.get('logged_in'):
        validation_alert = dbc.Alert(
            "You must be logged in to create a group",
            color="danger",
            dismissable=True
        )
        form_valid = False
    
    if not form_valid:
        if not validation_alert:
            validation_alert = dbc.Alert(
                "Please correct the errors below and try again",
                color="danger",
                dismissable=True
            )
        return [
            validation_alert, name_feedback, amount_feedback, frequency_feedback,
            duration_feedback, members_feedback, date_feedback, False, False, False, ""
        ]
    
    # If validation passes, create the group
    try:
        # Import here to avoid circular imports
        from services.group_service import create_group
        
        # Get user info from session
        user_email = session_data.get('user_info', {}).get('email', '')
        
        # Create group data
        group_data = {
            'name': name.strip(),
            'description': description.strip() if description else None,
            'contribution_amount': Decimal(str(amount)),
            'frequency': frequency,
            'start_date': datetime.strptime(start_date, "%Y-%m-%d").date(),
            'duration_months': duration,
            'max_members': max_members,
            'created_by_email': user_email
        }
        
        # Create the group
        result = create_group(group_data)
        
        if result['success']:
            success_message = f"Your group '{name}' has been created successfully! You can now invite members to join."
            return [
                "", "", "", "", "", "", "", False, True, False, success_message
            ]
        else:
            validation_alert = dbc.Alert(
                f"Error creating group: {result.get('error', 'Unknown error')}",
                color="danger",
                dismissable=True
            )
            return [
                validation_alert, "", "", "", "", "", "", False, False, True, ""
            ]
            
    except ImportError:
        # If group service doesn't exist yet, show a placeholder success
        success_message = f"Group creation form validated successfully! Group '{name}' would be created with £{amount} {frequency} contributions."
        return [
            "", "", "", "", "", "", "", False, True, False, success_message
        ]
    except Exception as e:
        validation_alert = dbc.Alert(
            f"Unexpected error: {str(e)}",
            color="danger",
            dismissable=True
        )
        return [
            validation_alert, "", "", "", "", "", "", False, False, True, ""
        ]

# Success Modal Callbacks
@callback(
    Output("success-modal", "is_open", allow_duplicate=True),
    [Input("close-success-btn", "n_clicks"),
     Input("view-group-btn", "n_clicks")],
    [State("success-modal", "is_open")],
    prevent_initial_call=True,
)
def close_success_modal(close_clicks, view_clicks, is_open):
    """Close the success modal."""
    if close_clicks or view_clicks:
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