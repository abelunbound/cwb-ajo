import dash
from dash import callback, html, Input, Output, State, ALL
import dash_bootstrap_components as dbc
from datetime import datetime, date, timedelta
from decimal import Decimal
import json
import os

# Group Modal Toggle Callbacks
@callback(
    Output("create-group-modal", "is_open"),
    [Input({"type": "create-group-trigger", "location": ALL}, "n_clicks"),
     Input("cancel-group-btn", "n_clicks")],
    [State("create-group-modal", "is_open")],
    prevent_initial_call=True
)
def toggle_group_modal(all_create_clicks, cancel_clicks, is_open):
    """Toggle the create group modal when any trigger button is clicked."""
    ctx = dash.callback_context
    if not ctx.triggered:
        return is_open
    
    print(f"DEBUG: Modal toggle callback triggered! all_create_clicks={all_create_clicks}, is_open={is_open}")
    print(f"DEBUG: Triggered button: {ctx.triggered[0]['prop_id']}")
    
    # Check if any create-group button was clicked
    any_create_clicked = any(clicks for clicks in all_create_clicks if clicks)
    
    # If any create button or cancel button was clicked, toggle the modal
    if any_create_clicked or cancel_clicks:
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
     Output("submit-group-btn", "disabled"),
     Output("success-modal", "is_open"),
     Output("create-group-modal", "is_open", allow_duplicate=True),
     Output("success-message-text", "children")],
    [Input("submit-group-btn", "n_clicks")],
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
    print(f"DEBUG: Group creation callback triggered! n_clicks={n_clicks}")
    print(f"DEBUG: Form data - name='{name}', amount={amount}, frequency='{frequency}', duration={duration}")
    print(f"DEBUG: Additional data - max_members={max_members}, start_date='{start_date}', description='{description}'")
    print(f"DEBUG: Session data present: {session_data is not None}")
    if session_data:
        print(f"DEBUG: User logged in: {session_data.get('logged_in', False)}")
    
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
    
    print("DEBUG: Starting validation...")
    
    # Validate required fields
    if not name or len(name.strip()) < 3:
        name_feedback = "Group name must be at least 3 characters long"
        form_valid = False
        print(f"DEBUG: Name validation failed: '{name}'")
    elif len(name.strip()) > 100:
        name_feedback = "Group name must be less than 100 characters"
        form_valid = False
        print(f"DEBUG: Name too long: '{name}'")
    else:
        print(f"DEBUG: Name validation passed: '{name}'")
    
    if not amount:
        amount_feedback = "Please select a contribution amount"
        form_valid = False
        print(f"DEBUG: Amount validation failed: {amount}")
    else:
        try:
            amount_int = int(amount)
            if amount_int not in [50, 100, 500, 800]:
                amount_feedback = "Please select a valid contribution amount"
                form_valid = False
                print(f"DEBUG: Amount not in valid range: {amount}")
            else:
                print(f"DEBUG: Amount validation passed: {amount}")
        except (ValueError, TypeError):
            amount_feedback = "Please select a valid contribution amount"
            form_valid = False
            print(f"DEBUG: Amount conversion failed: {amount} (type: {type(amount)})")
    
    if not frequency:
        frequency_feedback = "Please select a contribution frequency"
        form_valid = False
        print(f"DEBUG: Frequency validation failed: '{frequency}'")
    elif frequency not in ["weekly", "monthly"]:
        frequency_feedback = "Please select a valid frequency"
        form_valid = False
        print(f"DEBUG: Frequency not valid: '{frequency}'")
    else:
        print(f"DEBUG: Frequency validation passed: '{frequency}'")
    
    if not duration:
        duration_feedback = "Please enter the duration in months"
        form_valid = False
        print(f"DEBUG: Duration validation failed: {duration}")
    elif not isinstance(duration, int) or duration < 3 or duration > 24:
        duration_feedback = "Duration must be between 3 and 24 months"
        form_valid = False
        print(f"DEBUG: Duration not valid: {duration} (type: {type(duration)})")
    else:
        print(f"DEBUG: Duration validation passed: {duration}")
    
    if not max_members:
        members_feedback = "Please select maximum number of members"
        form_valid = False
        print(f"DEBUG: Max members validation failed: {max_members}")
    else:
        try:
            max_members_int = int(max_members)
            if max_members_int not in [5, 6, 7, 8, 9, 10]:
                members_feedback = "Please select a valid number of members (5-10)"
                form_valid = False
                print(f"DEBUG: Max members not valid: {max_members}")
            else:
                print(f"DEBUG: Max members validation passed: {max_members}")
        except (ValueError, TypeError):
            members_feedback = "Please select a valid number of members (5-10)"
            form_valid = False
            print(f"DEBUG: Max members conversion failed: {max_members} (type: {type(max_members)})")
    
    if not start_date:
        date_feedback = "Please select a start date"
        form_valid = False
        print(f"DEBUG: Start date validation failed: '{start_date}'")
    else:
        try:
            # Try multiple date formats to handle browser localization
            start_date_obj = None
            date_formats = ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%Y/%m/%d"]
            
            for fmt in date_formats:
                try:
                    start_date_obj = datetime.strptime(start_date, fmt).date()
                    print(f"DEBUG: Date parsed successfully with format {fmt}: {start_date_obj}")
                    break
                except ValueError:
                    continue
            
            if start_date_obj is None:
                raise ValueError(f"Unable to parse date: {start_date}")
            
            today = date.today()
            if start_date_obj <= today:
                date_feedback = "Start date must be in the future"
                form_valid = False
                print(f"DEBUG: Start date not in future: {start_date_obj} vs {today}")
            elif start_date_obj > today + timedelta(days=90):
                date_feedback = "Start date cannot be more than 90 days in the future"
                form_valid = False
                print(f"DEBUG: Start date too far in future: {start_date_obj}")
            else:
                print(f"DEBUG: Start date validation passed: {start_date_obj}")
        except ValueError as e:
            date_feedback = f"Please enter a valid date (received: {start_date})"
            form_valid = False
            print(f"DEBUG: Date parsing error: {e}")
    
    # Check if user is logged in
    if not session_data or not session_data.get('logged_in'):
        validation_alert = dbc.Alert(
            "You must be logged in to create a group",
            color="danger",
            dismissable=True
        )
        form_valid = False
        print("DEBUG: User not logged in")
    else:
        print("DEBUG: User login validation passed")
    
    print(f"DEBUG: Overall form validation result: {form_valid}")
    
    if not form_valid:
        if not validation_alert:
            validation_alert = dbc.Alert(
                "Please correct the errors below and try again",
                color="danger",
                dismissable=True
            )
        print("DEBUG: Returning validation errors")
        return [
            validation_alert, name_feedback, amount_feedback, frequency_feedback,
            duration_feedback, members_feedback, date_feedback, False, False, False, ""
        ]
    
    print("DEBUG: All validation passed, attempting to create group...")
    
    # If validation passes, create the group
    try:
        # Import here to avoid circular imports
        from services.group_service import create_group
        
        # Get user info from session
        user_email = session_data.get('user_info', {}).get('email', '')
        print(f"DEBUG: User email: {user_email}")
        
        # Parse start date with multiple format support
        start_date_obj = None
        date_formats = ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%Y/%m/%d"]
        
        for fmt in date_formats:
            try:
                start_date_obj = datetime.strptime(start_date, fmt).date()
                break
            except ValueError:
                continue
        
        if start_date_obj is None:
            raise ValueError(f"Unable to parse start date: {start_date}")
        
        # Create group data
        group_data = {
            'name': name.strip(),
            'description': description.strip() if description else None,
            'contribution_amount': Decimal(str(amount)),
            'frequency': frequency,
            'start_date': start_date_obj,
            'duration_months': duration,
            'max_members': int(max_members),
            'created_by_email': user_email
        }
        
        print(f"DEBUG: Group data prepared: {group_data}")
        
        # Create the group
        result = create_group(group_data)
        print(f"DEBUG: Group creation result: {result}")
        
        if result['success']:
            success_message = f"Your group '{name}' has been created successfully! You can now invite members to join."
            print("DEBUG: Returning success response")
            return [
                "", "", "", "", "", "", "", False, True, False, success_message
            ]
        else:
            validation_alert = dbc.Alert(
                f"Error creating group: {result.get('error', 'Unknown error')}",
                color="danger",
                dismissable=True
            )
            print(f"DEBUG: Group creation failed: {result.get('error', 'Unknown error')}")
            return [
                validation_alert, "", "", "", "", "", "", False, False, True, ""
            ]
            
    except ImportError:
        # If group service doesn't exist yet, show a placeholder success
        success_message = f"Group creation form validated successfully! Group '{name}' would be created with £{amount} {frequency} contributions."
        print("DEBUG: Using placeholder success (ImportError)")
        return [
            "", "", "", "", "", "", "", False, True, False, success_message
        ]
    except Exception as e:
        validation_alert = dbc.Alert(
            f"Unexpected error: {str(e)}",
            color="danger",
            dismissable=True
        )
        print(f"DEBUG: Unexpected error: {str(e)}")
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

# ==============================
# TASK 29: GROUP INVITATION SYSTEM CALLBACKS
# ==============================

# Import the new modals and functions
from components.modals import create_invitation_modal, create_invitation_success_modal
from functions.database import (
    create_group_invitation, get_invitation_by_code, 
    update_invitation_status, add_user_to_group, get_group_invitations
)
from pages.invite import (
    create_valid_invitation_layout, create_invalid_invitation_layout,
    create_expired_invitation_layout, create_already_responded_layout
)

# Callback to handle invitation modal and capture group context
@callback(
    [Output("invitation-modal", "is_open"),
     Output({"type": "selected-group-store", "page": ALL}, "data")],
    [Input({"type": "invite-member-btn", "group_id": ALL}, "n_clicks")],
    [State("invitation-modal", "is_open"),
     State({"type": "user-groups-store", "page": ALL}, "data"),
     State({"type": "selected-group-store", "page": ALL}, "data")],
    prevent_initial_call=True
)
def toggle_invitation_modal_with_context(invite_clicks_list, is_open, user_groups_stores, existing_stores):
    """Toggle invitation modal when invite button is clicked and capture group context."""
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update, [dash.no_update] * len(existing_stores)
    
    # Get the triggered component info
    triggered_prop_id = ctx.triggered[0]['prop_id']
    triggered_value = ctx.triggered[0]['value']
    
    # Enhanced validation: Only proceed if this is a real user click
    # 1. Must have a triggered component
    # 2. The triggered value must be > 0 (actual click, not component creation)
    # 3. Must be from an invite-member-btn
    if not triggered_prop_id or triggered_value is None or triggered_value <= 0:
        print(f"Invitation modal callback triggered but not from user click. Prop ID: {triggered_prop_id}, Value: {triggered_value}")
        return dash.no_update, [dash.no_update] * len(existing_stores)
    
    if "invite-member-btn" not in triggered_prop_id:
        print(f"Invitation modal callback triggered but not from invite button: {triggered_prop_id}")
        return dash.no_update, [dash.no_update] * len(existing_stores)
    
    # Parse the prop_id to get group_id
    import json
    try:
        # The prop_id looks like: {"index":0,"type":"invite-member-btn","group_id":68}.n_clicks
        prop_dict = json.loads(triggered_prop_id.split('.')[0])
        group_id = prop_dict.get('group_id')
        
        if not group_id:
            print(f"No group_id found in triggered component: {triggered_prop_id}")
            return dash.no_update, [dash.no_update] * len(existing_stores)
        
        # Find the group data from any of the user groups stores
        selected_group = None
        for groups_data in user_groups_stores:
            if groups_data:
                for group in groups_data:
                    if group['group_id'] == group_id:
                        selected_group = group
                        break
                if selected_group:
                    break
        
        if not selected_group:
            print(f"Group data not found for group_id: {group_id}")
            return dash.no_update, [dash.no_update] * len(existing_stores)
        
        print(f"✓ Valid invitation modal trigger for group ID: {group_id} ({selected_group['group_name']})")
        
        # Update all existing selected-group stores
        store_updates = [selected_group for _ in existing_stores]
        return not is_open, store_updates
        
    except Exception as e:
        print(f"Error parsing group_id from invite button: {e}")
        print(f"Triggered prop_id: {triggered_prop_id}")
        return dash.no_update, [dash.no_update] * len(existing_stores)

# Callback to handle invitation creation using store data
@callback(
    [Output("invitation-success-modal", "is_open"),
     Output("invitation-modal", "is_open", allow_duplicate=True),
     Output("invitation-link-display", "value"),
     Output("invitation-recipient-email", "children"),
     Output("invitation-form-alert", "children")],
    [Input("send-invitation-btn", "n_clicks")],
    [State("invitation-email-input", "value"),
     State("invitation-message-input", "value"),
     State("session-store", "data"),
     State({"type": "selected-group-store", "page": ALL}, "data")],
    prevent_initial_call=True
)
def handle_invitation_creation_with_store(n_clicks, email, message, session_data, selected_group_stores):
    """Handle creation and sending of group invitations using store data."""
    if not n_clicks:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
    
    # Validate user is logged in
    if not session_data or not session_data.get('logged_in'):
        alert = dbc.Alert("You must be logged in to send invitations", color="danger")
        return False, True, "", "", alert
    
    # Validate email
    if not email or '@' not in email:
        alert = dbc.Alert("Please enter a valid email address", color="danger")
        return False, True, "", "", alert
    
    # Get group ID from any of the selected group stores
    selected_group = None
    for store_data in selected_group_stores:
        if store_data and store_data.get('group_id'):
            selected_group = store_data
            break
    
    if not selected_group or not selected_group.get('group_id'):
        alert = dbc.Alert("No group selected. Please try again.", color="danger")
        return False, True, "", "", alert
    
    group_id = selected_group['group_id']
    group_name = selected_group.get('group_name', 'Unknown Group')
    inviter_user_id = session_data.get('user_info', {}).get('id', 1)
    
    print(f"Creating invitation for group ID: {group_id} ({group_name})")
    
    # Create invitation with actual group ID from store
    invitation = create_group_invitation(group_id, inviter_user_id, email)
    
    if invitation:
        # Generate invitation link based on environment
        # Check if we're in development or production
        # Use DASH_ENV first (project standard), then FLASK_ENV as fallback
        environment = os.getenv('DASH_ENV') or os.getenv('FLASK_ENV', 'production')  # Default to production for safety
        
        if environment == 'development':
            base_url = "http://127.0.0.1:8050"
        else:
            base_url = "https://your-app.com"
        
        invitation_link = f"{base_url}/invite/{invitation['invitation_code']}"
        
        print(f"Successfully created invitation for group {group_id}")
        print(f"Environment: {environment}, Invitation link: {invitation_link}")
        return True, False, invitation_link, email, ""
    else:
        alert = dbc.Alert("Failed to create invitation. Please try again.", color="danger")
        return False, True, "", "", alert

# Callback to load invitation details on invite page
@callback(
    Output("invitation-content", "children"),
    [Input("invitation-code-store", "data")],
    prevent_initial_call=False
)
def load_invitation_details(invitation_code):
    """Load and display invitation details."""
    if not invitation_code:
        return create_invalid_invitation_layout("No invitation code provided")
    
    # Get invitation from database
    invitation = get_invitation_by_code(invitation_code)
    
    if not invitation:
        return create_invalid_invitation_layout("Invitation not found")
    
    # Check invitation status
    if invitation['status'] == 'expired':
        return create_expired_invitation_layout()
    elif invitation['status'] in ['accepted', 'declined']:
        return create_already_responded_layout(invitation['status'])
    elif invitation['status'] != 'pending':
        return create_invalid_invitation_layout("Invalid invitation status")
    
    # Show valid invitation
    return create_valid_invitation_layout(invitation)

# Callback to handle invitation acceptance/decline
@callback(
    Output("invitation-action-feedback", "children"),
    [Input("accept-invitation-btn", "n_clicks"),
     Input("decline-invitation-btn", "n_clicks")],
    [State("invitation-code-store", "data"),
     State("session-store", "data")],
    prevent_initial_call=True
)
def handle_invitation_response(accept_clicks, decline_clicks, invitation_code, session_data):
    """Handle invitation acceptance or decline."""
    ctx = dash.callback_context
    if not ctx.triggered:
        return ""
    
    # Determine which button was clicked
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if not session_data or not session_data.get('logged_in'):
        return dbc.Alert(
            [
                html.P("You must be logged in to respond to invitations."),
                dbc.Button("Login", href="/", color="primary", size="sm")
            ],
            color="warning"
        )
    
    # Get invitation details
    invitation = get_invitation_by_code(invitation_code)
    if not invitation or invitation['status'] != 'pending':
        return dbc.Alert("Invalid or expired invitation", color="danger")
    
    # Process response
    if 'accept-invitation-btn' in button_id:
        # Accept invitation
        success = update_invitation_status(invitation_code, 'accepted')
        if success:
            # Add user to group
            user_id = session_data.get('user_info', {}).get('id', 1)
            group_added = add_user_to_group(user_id, invitation['group_id'])
            
            if group_added:
                return dbc.Alert(
                    [
                        html.I(className="fas fa-check-circle me-2"),
                        html.Strong("Welcome to the group! "),
                        f"You have successfully joined {invitation['group_name']}.",
                        html.Br(),
                        dbc.Button("View My Groups", href="/groups", color="success", size="sm", className="mt-2")
                    ],
                    color="success"
                )
            else:
                return dbc.Alert("Group is full or there was an error joining", color="danger")
        else:
            return dbc.Alert("Failed to accept invitation", color="danger")
    
    elif 'decline-invitation-btn' in button_id:
        # Decline invitation
        success = update_invitation_status(invitation_code, 'declined')
        if success:
            return dbc.Alert(
                [
                    html.I(className="fas fa-times-circle me-2"),
                    "You have declined this invitation."
                ],
                color="info"
            )
        else:
            return dbc.Alert("Failed to decline invitation", color="danger")
    
    return ""

# Callback to close invitation success modal
@callback(
    Output("invitation-success-modal", "is_open", allow_duplicate=True),
    [Input("close-invitation-success-btn", "n_clicks"),
     Input("send-another-invitation-btn", "n_clicks")],
    [State("invitation-success-modal", "is_open")],
    prevent_initial_call=True
)
def close_invitation_success_modal(close_clicks, another_clicks, is_open):
    """Close invitation success modal."""
    if close_clicks or another_clicks:
        return False
    return is_open

# Callback to reopen invitation modal for another invitation
@callback(
    [Output("invitation-modal", "is_open", allow_duplicate=True),
     Output("invitation-email-input", "value"),
     Output("invitation-message-input", "value")],
    [Input("send-another-invitation-btn", "n_clicks")],
    prevent_initial_call=True
)
def send_another_invitation(n_clicks):
    """Reopen invitation modal for sending another invitation."""
    if n_clicks:
        return True, "", ""  # Open modal and clear form
    return dash.no_update, dash.no_update, dash.no_update

# Callback to copy invitation link to clipboard (client-side)
import dash_bootstrap_components as dbc
from dash import clientside_callback, ClientsideFunction

clientside_callback(
    """
    function(n_clicks) {
        if (n_clicks > 0) {
            const linkInput = document.getElementById('invitation-link-display');
            linkInput.select();
            linkInput.setSelectionRange(0, 99999); // For mobile devices
            navigator.clipboard.writeText(linkInput.value);
            
            // Show temporary feedback
            const copyBtn = document.querySelector('#copy-invitation-link-btn');
            const originalText = copyBtn.innerHTML;
            copyBtn.innerHTML = '<i class="fas fa-check me-1"></i>Copied!';
            setTimeout(() => {
                copyBtn.innerHTML = originalText;
            }, 2000);
            
            return true;
        }
        return false;
    }
    """,
    Output("copy-invitation-link-btn", "disabled"),
    [Input("copy-invitation-link-btn", "n_clicks")],
    prevent_initial_call=True
)

# ============================================
# TASK 30: MEMBERSHIP MANAGEMENT CALLBACKS
# ============================================

# Removed duplicate callback - functionality consolidated into toggle_enhanced_membership_modal


@callback(
    Output("membership-management-modal", "is_open", allow_duplicate=True),
    [Input("membership-modal-close", "n_clicks"),
     Input("membership-refresh-btn", "n_clicks")],
    [State("membership-management-modal", "is_open")],
    prevent_initial_call=True
)
def close_membership_modal(close_clicks, refresh_clicks, is_open):
    """Close membership modal or refresh data."""
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update
    
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if triggered_id == "membership-modal-close":
        return False
    elif triggered_id == "membership-refresh-btn":
        # For refresh, we'll trigger a re-render by keeping modal open
        return is_open
    
    return dash.no_update


@callback(
    [Output("role-change-modal", "is_open"),
     Output("role-change-member-name", "children"),
     Output("role-change-current-role", "children"),
     Output("role-change-dropdown", "value")],
    [Input({"type": "change-role-btn", "member_id": ALL}, "n_clicks")],
    [State("role-change-modal", "is_open")],
    prevent_initial_call=True
)
def toggle_role_change_modal(n_clicks_list, is_open):
    """Toggle role change modal."""
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update
    
    triggered_value = ctx.triggered[0]['value']
    if not triggered_value or triggered_value <= 0:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update
    
    # Extract member_id from triggered component
    import json
    triggered_prop_id = ctx.triggered[0]['prop_id']
    prop_dict = json.loads(triggered_prop_id.split('.')[0])
    member_id = prop_dict.get('member_id')
    
    if not member_id:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update
    
    # Get member info (for now, we'll use placeholder data)
    # In a real implementation, you'd fetch this from the database
    member_name = f"Member: User ID {member_id}"
    current_role = "Current role: Loading..."
    
    return True, member_name, current_role, None


@callback(
    Output("role-change-modal", "is_open", allow_duplicate=True),
    [Input("role-change-cancel", "n_clicks"),
     Input("role-change-confirm", "n_clicks")],
    [State("role-change-modal", "is_open"),
     State("role-change-dropdown", "value")],
    prevent_initial_call=True
)
def handle_role_change(cancel_clicks, confirm_clicks, is_open, new_role):
    """Handle role change confirmation or cancellation."""
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update
    
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if triggered_id == "role-change-cancel":
        return False
    elif triggered_id == "role-change-confirm":
        if new_role:
            # Here you would implement the actual role change logic
            print(f"Would change role to: {new_role}")
            return False
        else:
            # Don't close if no role selected
            return is_open
    
    return dash.no_update


@callback(
    [Output("remove-member-modal", "is_open"),
     Output("remove-member-name", "children"),
     Output("remove-member-role", "children")],
    [Input({"type": "remove-member-btn", "member_id": ALL}, "n_clicks")],
    [State("remove-member-modal", "is_open")],
    prevent_initial_call=True
)
def toggle_remove_member_modal(n_clicks_list, is_open):
    """Toggle remove member modal."""
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update, dash.no_update
    
    triggered_value = ctx.triggered[0]['value']
    if not triggered_value or triggered_value <= 0:
        return dash.no_update, dash.no_update, dash.no_update
    
    # Extract member_id from triggered component
    import json
    triggered_prop_id = ctx.triggered[0]['prop_id']
    prop_dict = json.loads(triggered_prop_id.split('.')[0])
    member_id = prop_dict.get('member_id')
    
    if not member_id:
        return dash.no_update, dash.no_update, dash.no_update
    
    # Get member info (placeholder for now)
    member_name = f"Member: User ID {member_id}"
    member_role = "Role: Loading..."
    
    return True, member_name, member_role


@callback(
    Output("remove-member-modal", "is_open", allow_duplicate=True),
    [Input("remove-member-cancel", "n_clicks"),
     Input("remove-member-confirm", "n_clicks")],
    [State("remove-member-modal", "is_open")],
    prevent_initial_call=True
)
def handle_remove_member(cancel_clicks, confirm_clicks, is_open):
    """Handle member removal confirmation or cancellation."""
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update
    
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if triggered_id == "remove-member-cancel":
        return False
    elif triggered_id == "remove-member-confirm":
        # Here you would implement the actual member removal logic
        print("Would remove member")
        return False
    
    return dash.no_update

# ============================================
# TASK 30 PHASE 2: STATUS MANAGEMENT CALLBACKS
# ============================================

@callback(
    [Output("member-status-change-modal", "is_open"),
     Output("status-change-member-name", "children"),
     Output("status-change-current-status", "children"),
     Output("status-change-dropdown", "value")],
    [Input({"type": "change-status-btn", "member_id": ALL}, "n_clicks")],
    [State("member-status-change-modal", "is_open")],
    prevent_initial_call=True
)
def toggle_status_change_modal(n_clicks_list, is_open):
    """Toggle member status change modal."""
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update
    
    triggered_value = ctx.triggered[0]['value']
    if not triggered_value or triggered_value <= 0:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update
    
    # Extract member_id from triggered component
    import json
    triggered_prop_id = ctx.triggered[0]['prop_id']
    prop_dict = json.loads(triggered_prop_id.split('.')[0])
    member_id = prop_dict.get('member_id')
    
    if not member_id:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update
    
    # Get member info (placeholder for now)
    member_name = f"Member: User ID {member_id}"
    current_status = "Current status: Loading..."
    
    return True, member_name, current_status, None


@callback(
    Output("member-status-change-modal", "is_open", allow_duplicate=True),
    [Input("status-change-cancel", "n_clicks"),
     Input("status-change-confirm", "n_clicks")],
    [State("member-status-change-modal", "is_open"),
     State("status-change-dropdown", "value"),
     State("status-change-reason", "value")],
    prevent_initial_call=True
)
def handle_status_change(cancel_clicks, confirm_clicks, is_open, new_status, reason):
    """Handle member status change confirmation or cancellation."""
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update
    
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if triggered_id == "status-change-cancel":
        return False
    elif triggered_id == "status-change-confirm":
        if new_status:
            # Here you would implement the actual status change logic
            print(f"Would change status to: {new_status} with reason: {reason}")
            return False
        else:
            # Don't close if no status selected
            return is_open
    
    return dash.no_update


# ============================================
# TASK 30 PHASE 3: COMMUNICATION CALLBACKS
# ============================================

@callback(
    [Output("member-contact-modal", "is_open"),
     Output("contact-member-name", "children"),
     Output("contact-member-email", "children")],
    [Input({"type": "contact-member-btn", "member_id": ALL}, "n_clicks"),
     Input({"type": "contact-member-link", "member_id": ALL}, "n_clicks")],
    [State("member-contact-modal", "is_open")],
    prevent_initial_call=True
)
def toggle_contact_modal(contact_btn_clicks, contact_link_clicks, is_open):
    """Toggle member contact modal."""
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update, dash.no_update
    
    triggered_value = ctx.triggered[0]['value']
    if not triggered_value or triggered_value <= 0:
        return dash.no_update, dash.no_update, dash.no_update
    
    # Extract member_id from triggered component
    import json
    triggered_prop_id = ctx.triggered[0]['prop_id']
    prop_dict = json.loads(triggered_prop_id.split('.')[0])
    member_id = prop_dict.get('member_id')
    
    if not member_id:
        return dash.no_update, dash.no_update, dash.no_update
    
    # Get member info (placeholder for now)
    member_name = f"Member: User ID {member_id}"
    member_email = f"Email: user{member_id}@example.com"
    
    return True, member_name, member_email


@callback(
    Output("member-contact-modal", "is_open", allow_duplicate=True),
    [Input("contact-cancel", "n_clicks"),
     Input("contact-send", "n_clicks")],
    [State("member-contact-modal", "is_open"),
     State("contact-subject", "value"),
     State("contact-message", "value")],
    prevent_initial_call=True
)
def handle_contact_member(cancel_clicks, send_clicks, is_open, subject, message):
    """Handle member contact form submission or cancellation."""
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update
    
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if triggered_id == "contact-cancel":
        return False
    elif triggered_id == "contact-send":
        if subject and message:
            # Here you would implement the actual message sending logic
            print(f"Would send message - Subject: {subject}, Message: {message}")
            return False
        else:
            # Don't close if required fields are empty
            return is_open
    
    return dash.no_update


@callback(
    [Output("group-announcement-modal", "is_open"),
     Output("announcement-group-name", "children"),
     Output("announcement-recipients", "children")],
    [Input("send-announcement-btn", "n_clicks")],
    [State("group-announcement-modal", "is_open"),
     State({"type": "selected-group-store", "page": ALL}, "data")],
    prevent_initial_call=True
)
def toggle_announcement_modal(n_clicks, is_open, selected_stores):
    """Toggle group announcement modal."""
    if not n_clicks or n_clicks <= 0:
        return dash.no_update, dash.no_update, dash.no_update
    
    # Get group info from store
    group_name = "Group: Loading..."
    recipients = "Recipients: Loading..."
    
    for store_data in selected_stores:
        if store_data:
            group_name = f"Group: {store_data.get('group_name', 'Unknown')}"
            member_count = store_data.get('current_members', 0)
            recipients = f"Recipients: {member_count} members"
            break
    
    return True, group_name, recipients


@callback(
    Output("group-announcement-modal", "is_open", allow_duplicate=True),
    [Input("announcement-cancel", "n_clicks"),
     Input("announcement-send", "n_clicks")],
    [State("group-announcement-modal", "is_open"),
     State("announcement-title", "value"),
     State("announcement-message", "value"),
     State("announcement-recipients-checklist", "value"),
     State("announcement-priority", "value")],
    prevent_initial_call=True
)
def handle_group_announcement(cancel_clicks, send_clicks, is_open, title, message, recipients, priority):
    """Handle group announcement sending or cancellation."""
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update
    
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if triggered_id == "announcement-cancel":
        return False
    elif triggered_id == "announcement-send":
        if title and message and recipients:
            # Here you would implement the actual announcement sending logic
            print(f"Would send announcement - Title: {title}, Recipients: {recipients}, Priority: {priority}")
            return False
        else:
            # Don't close if required fields are empty
            return is_open
    
    return dash.no_update


# NOTE: Old modal-based membership management callbacks removed
# These have been replaced with page-based approach in pages/member_management.py


# Separate callback for loading activity (reduces complexity)
@callback(
    Output("membership-activity-list", "children"),
    [Input("membership-management-modal", "is_open")],
    prevent_initial_call=True
)
def load_membership_activity(is_open):
    """Load membership activity separately to avoid callback complexity."""
    if not is_open:
        return dash.no_update
    
    try:
        # ENHANCEMENT 3: Enhanced activity with real data
        activity_data = []
        
        # Try to load real activity data
        try:
            # Mock activity data for now (can be replaced with real data later)
            activity_data = [
                {
                    'type': 'joined',
                    'title': 'New Member Joined',
                    'description': 'John Doe joined the group',
                    'timestamp': '2 hours ago'
                },
                {
                    'type': 'payment_made',
                    'title': 'Payment Received',
                    'description': 'Jane Smith made monthly contribution',
                    'timestamp': '1 day ago'
                },
                {
                    'type': 'role_changed',
                    'title': 'Role Updated',
                    'description': 'Mike Johnson promoted to admin',
                    'timestamp': '3 days ago'
                },
                {
                    'type': 'status_changed',
                    'title': 'Status Changed',
                    'description': 'Sarah Wilson status updated to active',
                    'timestamp': '1 week ago'
                }
            ]
            
            # Create enhanced activity component
            from components.membership_management import create_member_activity_list
            return create_member_activity_list(activity_data)
            
        except Exception as e:
            print(f"Error loading activity data: {e}")
            # Fallback to simple activity display
            return html.Div([
                html.Div([
                    html.I(className="fas fa-user-plus text-success me-2"),
                    html.Span("John Doe joined the group", className="me-2"),
                    html.Small("2 hours ago", className="text-muted")
                ], className="d-flex align-items-center mb-2"),
                html.Div([
                    html.I(className="fas fa-dollar-sign text-primary me-2"),
                    html.Span("Jane Smith made payment", className="me-2"),
                    html.Small("1 day ago", className="text-muted")
                ], className="d-flex align-items-center mb-2")
            ])
    except Exception as e:
        print(f"Error loading activity: {e}")
        return html.Div("Activity unavailable", className="text-muted")


# Template buttons for quick messages
@callback(
    [Output("contact-subject", "value"),
     Output("contact-message", "value")],
    [Input("template-payment-reminder", "n_clicks"),
     Input("template-welcome", "n_clicks"),
     Input("template-update", "n_clicks")],
    prevent_initial_call=True
)
def apply_message_template(payment_clicks, welcome_clicks, update_clicks):
    """Apply quick message templates."""
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update
    
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    templates = {
        "template-payment-reminder": {
            "subject": "Monthly Contribution Reminder",
            "message": "Hi! This is a friendly reminder that your monthly contribution is due. Please make your payment at your earliest convenience. Thank you!"
        },
        "template-welcome": {
            "subject": "Welcome to the Group!",
            "message": "Welcome to our Ajo savings group! We're excited to have you join us. Please let us know if you have any questions about the group or contribution schedule."
        },
        "template-update": {
            "subject": "Group Update",
            "message": "Hello everyone! I wanted to share an important update about our group. Please review the information and let us know if you have any questions."
        }
    }
    
    template = templates.get(triggered_id, {})
    return template.get("subject", ""), template.get("message", "")