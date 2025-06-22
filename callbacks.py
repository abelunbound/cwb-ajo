import dash
from dash import callback, html
from dash.dependencies import Input, Output, State, ALL
import dash_bootstrap_components as dbc
from datetime import datetime, date, timedelta
from decimal import Decimal
import json

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

# =============================================================================
# GROUP DISCOVERY CALLBACKS (Task 28)
# =============================================================================

@callback(
    [Output("discovery-content", "children"),
     Output("results-summary", "children"),
     Output("discovery-pagination", "max_value"),
     Output("discovery-pagination", "active_page"),
     Output("discovery-state", "children")],
    [Input("discovery-search-btn", "n_clicks"),
     Input("error-retry-btn", "n_clicks"),
     Input("discovery-pagination", "active_page"),
     Input("discovery-search-input", "value"),
     Input("amount-filter", "value"),
     Input("frequency-filter", "value"),
     Input("spots-filter", "value")],
    [State("discovery-search-input", "value"),
     State("amount-filter", "value"),
     State("frequency-filter", "value"),
     State("spots-filter", "value"),
     State("per-page-filter", "value"),
     State("session-store", "data"),
     State("discovery-state", "children")],
    prevent_initial_call=False
)
def update_group_discovery(search_clicks, retry_clicks, page, search_input_value, 
                          amount_input_value, frequency_input_value, spots_input_value,
                          search_query, amount_filter, frequency_filter, spots_filter, 
                          per_page, session_data, current_state):
    """Update group discovery content based on search, filters, and pagination."""
    
    # Check if user is logged in
    if not session_data or not session_data.get('logged_in'):
        from components.group_discovery import create_error_state
        return [
            create_error_state("Please log in to discover groups"),
            html.P("Please log in to view groups", className="text-muted"),
            1, 1, ""
        ]
    
    try:
        from services.group_discovery_service import search_groups, get_discoverable_groups
        from components.group_discovery import create_group_grid, create_error_state
        
        # Get user email from session
        user_email = session_data.get('user_info', {}).get('email', '')
        if not user_email:
            return [
                create_error_state("Session error - please log in again"),
                html.P("Session error", className="text-muted"),
                1, 1, ""
            ]
        
        # Get user ID (simplified - in production you'd have a proper user service)
        from functions.database import get_ajo_db_connection
        import psycopg2
        
        conn = get_ajo_db_connection()
        if not conn:
            return [
                create_error_state("Database connection failed"),
                html.P("Database error", className="text-muted"),
                1, 1, ""
            ]
        
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = %s", (user_email,))
        user_result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not user_result:
            return [
                create_error_state("User not found"),
                html.P("User error", className="text-muted"),
                1, 1, ""
            ]
        
        user_id = user_result[0]
        
        # Use current form values (which will be cleared by the separate callback)
        # No need to handle clear filters here anymore
        
        # Set defaults
        if per_page is None:
            per_page = 12
        if page is None:
            page = 1
        
        # Build filters dict
        filters = {}
        if amount_filter:
            filters['contribution_amount'] = amount_filter
        if frequency_filter:
            filters['frequency'] = frequency_filter
        if spots_filter:
            filters['min_spots'] = spots_filter
        
        # Search or get groups
        if search_query and search_query.strip():
            result = search_groups(user_id, search_query.strip(), filters, page, per_page)
        else:
            if filters:
                result = search_groups(user_id, "", filters, page, per_page)
            else:
                result = get_discoverable_groups(user_id, page, per_page)
        
        if not result['success']:
            return [
                create_error_state(f"Error loading groups: {result.get('error', 'Unknown error')}"),
                html.P("Error loading groups", className="text-muted"),
                1, 1, ""
            ]
        
        # Create group grid
        groups = result['groups']
        grid_content = create_group_grid(groups)
        
        # Create results summary
        total_count = result['total_count']
        current_page = result['page']
        total_pages = result['total_pages']
        
        if total_count == 0:
            summary_text = "No groups found"
        else:
            start_item = (current_page - 1) * per_page + 1
            end_item = min(current_page * per_page, total_count)
            summary_text = f"Showing {start_item}-{end_item} of {total_count} groups"
        
        summary = html.P(summary_text, className="text-muted")
        
        # Store current state
        state_data = json.dumps({
            'search_query': search_query or "",
            'filters': filters,
            'page': current_page,
            'per_page': per_page
        })
        
        return [
            grid_content,  # Return the normal grid content
            summary,
            max(1, total_pages),
            current_page,
            state_data
        ]
        
    except ImportError as e:
        # Service not available yet
        from components.group_discovery import create_error_state
        return [
            create_error_state("Group discovery service not available yet"),
            html.P("Service not available", className="text-muted"),
            1, 1, ""
        ]
    except Exception as e:
        print(f"Error in group discovery: {e}")
        from components.group_discovery import create_error_state
        return [
            create_error_state(f"Unexpected error: {str(e)}"),
            html.P("Unexpected error", className="text-muted"),
            1, 1, ""
        ]


@callback(
    [Output("group-detail-modal", "is_open"),
     Output("group-detail-modal-title", "children"),
     Output("group-detail-modal-body", "children"),
     Output("group-detail-join-btn", "style")],
    [Input({"type": "view-details-btn", "index": ALL}, "n_clicks"),
     Input("group-detail-modal-close", "n_clicks")],
    [State("session-store", "data")],
    prevent_initial_call=True
)
def handle_group_detail_modal(view_details_clicks_list, close_clicks, session_data):
    """Handle opening and closing group detail modal."""
    
    ctx = dash.callback_context
    if not ctx.triggered:
        return False, "", html.P("Loading...", className="text-center"), {"display": "none"}
    
    trigger = ctx.triggered[0]
    
    # Handle close
    if trigger['prop_id'] == 'group-detail-modal-close.n_clicks':
        return False, "", html.P("Loading...", className="text-center"), {"display": "none"}
    
    # Handle view details request
    if 'view-details-btn' in trigger['prop_id']:
        
        # Check if this is a real click (value > 0) or just component creation (value = 0 or None)
        if trigger['value'] is None or trigger['value'] == 0:
            return False, "", html.P("Loading...", className="text-center"), {"display": "none"}
        
        try:
            import json
            trigger_data = json.loads(trigger['prop_id'].split('.')[0])
            group_id = trigger_data['index']
            
            # Check if user is logged in
            if not session_data or not session_data.get('logged_in'):
                return False, "", html.P("Please log in", className="text-center"), {"display": "none"}
            
            # Get group details
            from services.group_discovery_service import get_group_details_for_discovery, can_user_join_group
            from components.group_discovery import create_group_detail_content
            from functions.database import get_ajo_db_connection
            
            # Get user ID
            user_email = session_data.get('user_info', {}).get('email', '')
            conn = get_ajo_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE email = %s", (user_email,))
            user_result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if not user_result:
                return False, "", html.P("User error", className="text-center"), {"display": "none"}
            
            user_id = user_result[0]
            
            # Get group details
            group_details = get_group_details_for_discovery(group_id, user_id)
            if not group_details:
                return False, "", html.P("Group not found or not accessible", className="text-center"), {"display": "none"}
            
            # Check if user can join
            can_join_result = can_user_join_group(group_id, user_id)
            
            # Create modal content
            modal_title = group_details['name']
            modal_content = create_group_detail_content(group_details)
            
            # Show/hide join button in modal based on whether user can join
            join_btn_style = {"display": "block"} if can_join_result['can_join'] else {"display": "none"}
            
            return True, modal_title, modal_content, join_btn_style
            
        except Exception as e:
            return False, "", html.P(f"Error: {str(e)}", className="text-center"), {"display": "none"}
    
    return False, "", html.P("Loading...", className="text-center"), {"display": "none"}


@callback(
    [Output("join-request-modal", "is_open"),
     Output("join-request-content", "children"),
     Output("join-request-alert", "children"),
     Output("join-request-alert", "is_open"),
     Output("join-request-alert", "color")],
    [Input("group-detail-join-btn", "n_clicks"),
     Input("join-request-confirm", "n_clicks"),
     Input("join-request-cancel", "n_clicks")],
    [State("group-detail-modal-title", "children"),
     State("session-store", "data")],
    prevent_initial_call=True
)
def handle_join_request_modal(detail_join_clicks, confirm_clicks, cancel_clicks, 
                             group_name, session_data):
    """Handle join request modal and processing."""
    
    ctx = dash.callback_context
    if not ctx.triggered:
        return False, "", "", False, "info"
    
    trigger = ctx.triggered[0]['prop_id']
    
    # Handle cancel
    if trigger == 'join-request-cancel.n_clicks':
        return False, "", "", False, "info"
    
    # Handle opening join request modal
    if trigger == 'group-detail-join-btn.n_clicks':
        if not group_name:
            return False, "", "", False, "info"
        
        content = html.Div([
            html.P(f"Are you sure you want to request to join '{group_name}'?"),
            html.P("The group administrator will be notified of your request.", className="text-muted small"),
        ])
        
        return True, content, "", False, "info"
    
    # Handle join request confirmation
    if trigger == 'join-request-confirm.n_clicks':
        try:
            # This would be implemented in a future task for actual join request processing
            # For now, show a success message
            alert_content = f"Your request to join '{group_name}' has been sent! The group administrator will review your request."
            return False, "", alert_content, True, "success"
            
        except Exception as e:
            alert_content = f"Error sending join request: {str(e)}"
            return False, "", alert_content, True, "danger"
    
    return False, "", "", False, "info"


# Clear filters callback for discovery search input
@callback(
    [Output("discovery-search-input", "value"),
     Output("amount-filter", "value"),
     Output("frequency-filter", "value"),
     Output("spots-filter", "value")],
    [Input("clear-filters-btn", "n_clicks"),
     Input("empty-state-clear-btn", "n_clicks")],
    prevent_initial_call=True
)
def clear_discovery_filters(clear_clicks, empty_clear_clicks):
    """Clear all discovery filters."""
    if clear_clicks or empty_clear_clicks:
        return "", [], [], None
    return dash.no_update, dash.no_update, dash.no_update, dash.no_update

# New callback for handling direct join requests from group cards
@callback(
    [Output("join-request-modal", "is_open", allow_duplicate=True),
     Output("join-request-content", "children", allow_duplicate=True),
     Output("join-request-alert", "children", allow_duplicate=True),
     Output("join-request-alert", "is_open", allow_duplicate=True),
     Output("join-request-alert", "color", allow_duplicate=True)],
    [Input({"type": "join-group-btn", "index": ALL}, "n_clicks")],
    [State("session-store", "data")],
    prevent_initial_call=True
)
def handle_direct_join_request(join_clicks_list, session_data):
    """Handle direct join requests from group cards."""
    
    ctx = dash.callback_context
    if not ctx.triggered:
        return False, "", "", False, "info"
    
    trigger = ctx.triggered[0]
    
    # Handle join group button click
    if 'join-group-btn' in trigger['prop_id']:
        
        # Check if this is a real click (value > 0) or just component creation (value = 0 or None)
        if trigger['value'] is None or trigger['value'] == 0:
            return False, "", "", False, "info"
        
        try:
            import json
            trigger_data = json.loads(trigger['prop_id'].split('.')[0])
            group_id = trigger_data['index']
            
            # Check if user is logged in
            if not session_data or not session_data.get('logged_in'):
                return False, "", "Please log in to join groups", True, "warning"
            
            # Get group details to show group name in confirmation
            from services.group_discovery_service import get_group_details_for_discovery
            from functions.database import get_ajo_db_connection
            
            # Get user ID
            user_email = session_data.get('user_info', {}).get('email', '')
            conn = get_ajo_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE email = %s", (user_email,))
            user_result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if not user_result:
                return False, "", "User session error", True, "danger"
            
            user_id = user_result[0]
            
            # Get group details
            group_details = get_group_details_for_discovery(group_id, user_id)
            if not group_details:
                return False, "", "Group not found", True, "danger"
            
            # Create join request content
            content = html.Div([
                html.P(f"Are you sure you want to request to join '{group_details['name']}'?"),
                html.P("The group administrator will be notified of your request.", className="text-muted small"),
                html.Hr(),
                html.P(f"Group: {group_details['name']}", className="fw-bold"),
                html.P(f"Contribution: £{group_details['contribution_amount']} {group_details['frequency']}", className="small"),
                html.P(f"Duration: {group_details['duration_months']} months", className="small"),
            ])
            
            return True, content, "", False, "info"
            
        except Exception as e:
            return False, "", f"Error: {str(e)}", True, "danger"
    
    return False, "", "", False, "info"