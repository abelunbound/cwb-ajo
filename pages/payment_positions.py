"""
Payment Positions Page

This page provides a dedicated interface for managing payment positions in Ajo groups,
replacing the modal-based approach with a full-page experience.
"""

import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc

# Register the page with URL parameter for group_id
dash.register_page(__name__, path_template="/payment-positions/<group_id>", title="Payment Positions | Ajo")

def create_page_header(group_id):
    """Create page header with breadcrumb navigation."""
    return html.Div(
        className="dashboard-header mb-4",
        children=[
            # Breadcrumb navigation
            dbc.Breadcrumb(
                items=[
                    {"label": "Home", "href": "/"},
                    {"label": "Groups", "href": "/groups"},
                    {"label": "Member Management", "href": f"/member-management/{group_id}"},
                    {"label": "Payment Positions", "active": True},
                ],
                className="mb-3"
            ),
            
            # Page title and actions
            html.Div(
                className="d-flex justify-content-between align-items-center",
                children=[
                    html.Div([
                        html.H1("Payment Position Management", className="dashboard-title mb-1"),
                        html.P(id="payment-positions-subtitle", className="dashboard-subtitle mb-0"),
                    ]),
                    html.Div([
                        dbc.Button(
                            [html.I(className="fas fa-arrow-left me-2"), "Back to Members"],
                            href=f"/member-management/{group_id}",
                            color="outline-secondary",
                            className="me-2"
                        ),
                        dbc.Button(
                            [html.I(className="fas fa-refresh me-2"), "Refresh"],
                            id="page-refresh-positions-btn",
                            color="outline-primary"
                        )
                    ])
                ]
            )
        ]
    )

def create_assignment_options_section():
    """Create the assignment options section."""
    return dbc.Card([
        dbc.CardHeader([
            html.H5([
                html.I(className="fas fa-cogs me-2"),
                "Assignment Options"
            ], className="mb-0")
        ]),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.H6("Quick Assignment", className="mb-3"),
                    dbc.ButtonGroup([
                        dbc.Button(
                            [html.I(className="fas fa-random me-2"), "Random Assignment"],
                            id="page-payment-position-random-btn",
                            color="primary",
                            size="sm"
                        ),
                        dbc.Button(
                            [html.I(className="fas fa-magic me-2"), "Auto-Assign Missing"],
                            id="page-payment-position-auto-btn",
                            color="success",
                            size="sm"
                        ),
                        dbc.Button(
                            [html.I(className="fas fa-check me-2"), "Validate Positions"],
                            id="page-payment-position-validate-btn",
                            color="info",
                            size="sm"
                        )
                    ], className="w-100")
                ], width=12, lg=6),
                dbc.Col([
                    html.H6("Position Swapping", className="mb-3"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("First Member", size="sm"),
                            dcc.Dropdown(
                                id="page-payment-position-swap-member1",
                                placeholder="Select first member...",
                                className="mb-2"
                            )
                        ], width=5),
                        dbc.Col([
                            dbc.Label("Second Member", size="sm"),
                            dcc.Dropdown(
                                id="page-payment-position-swap-member2",
                                placeholder="Select second member...",
                                className="mb-2"
                            )
                        ], width=5),
                        dbc.Col([
                            dbc.Label("Action", size="sm"),
                            dbc.Button(
                                "Swap",
                                id="page-payment-position-swap-btn",
                                color="warning",
                                size="sm",
                                className="w-100"
                            )
                        ], width=2)
                    ])
                ], width=12, lg=6)
            ])
        ])
    ], className="mb-4")

def create_current_positions_section():
    """Create the current positions display section."""
    return dbc.Card([
        dbc.CardHeader([
            html.H5([
                html.I(className="fas fa-list-ol me-2"),
                "Current Payment Positions"
            ], className="mb-0")
        ]),
        dbc.CardBody([
            html.Div(id="page-payment-position-list", children=[
                dbc.Spinner(color="primary", size="lg")
            ])
        ])
    ], className="mb-4")

def create_payment_schedule_section():
    """Create the payment schedule section."""
    return dbc.Card([
        dbc.CardHeader([
            html.H5([
                html.I(className="fas fa-calendar-alt me-2"),
                "Payment Schedule"
            ], className="mb-0")
        ]),
        dbc.CardBody([
            # Next recipient highlight
            html.Div(id="page-payment-schedule-next-recipient", className="mb-4"),
            
            # Complete schedule
            html.H6("Complete Payment Order", className="mb-3"),
            html.Div(id="page-payment-schedule-list", children=[
                dbc.Spinner(color="primary", size="sm")
            ])
        ])
    ])

def layout(group_id=None, **kwargs):
    """Layout for payment positions page."""
    if not group_id:
        return html.Div([
            dbc.Alert(
                [
                    html.H4("Invalid Group", className="alert-heading"),
                    html.P("No group ID provided. Please select a group to manage payment positions."),
                    html.Hr(),
                    dbc.Button("Go to Groups", href="/groups", color="primary")
                ],
                color="warning",
                className="m-4"
            )
        ])
    
    return html.Div([
        # Store for group context
        dcc.Store(id="payment-positions-group-store", data={"group_id": group_id}),
        dcc.Store(id="payment-positions-data-store", data={}),
        
        # Page header with breadcrumb
        create_page_header(group_id),
        
        # Group information card
        html.Div(id="page-payment-position-group-info", className="mb-4"),
        
        # Assignment options section
        create_assignment_options_section(),
        
        # Current positions section
        create_current_positions_section(),
        
        # Payment schedule section
        create_payment_schedule_section(),
        
        # Alert area for feedback
        html.Div(id="page-payment-position-alert", className="mt-4")
    ])

# Callback to load payment position data
@callback(
    [Output("page-payment-position-group-info", "children"),
     Output("payment-positions-subtitle", "children"),
     Output("page-payment-position-list", "children"),
     Output("page-payment-position-swap-member1", "options"),
     Output("page-payment-position-swap-member2", "options"),
     Output("page-payment-schedule-next-recipient", "children"),
     Output("page-payment-schedule-list", "children"),
     Output("payment-positions-data-store", "data")],
    [Input("payment-positions-group-store", "data"),
     Input("page-refresh-positions-btn", "n_clicks")],
    [State("session-store", "data")],
    prevent_initial_call=False
)
def load_payment_positions_data(group_store, refresh_clicks, session_data):
    """Load payment positions and schedule data for the page."""
    if not group_store or not group_store.get("group_id"):
        return [dash.no_update] * 8
    
    group_id = group_store["group_id"]
    
    # Check if user is logged in
    if not session_data or not session_data.get('logged_in'):
        error_alert = dbc.Alert("Please log in to view payment positions.", color="warning")
        return error_alert, "Access Denied", html.Div(), [], [], html.Div(), html.Div(), {}
    
    try:
        # Get payment positions from service
        from services.payment_position_service import get_group_payment_positions, get_payment_schedule
        positions_data = get_group_payment_positions(group_id)
        
        # Get payment schedule
        schedule_result = get_payment_schedule(group_id)
        
        # Create group info card
        if schedule_result.get('success'):
            from components.payment_position_management import create_group_info_for_positions
            group_info = create_group_info_for_positions({
                'group_name': schedule_result['group_name'],
                'contribution_amount': schedule_result['contribution_amount'],
                'frequency': schedule_result['frequency'],
                'current_members': schedule_result['total_members'],
                'group_status': schedule_result['group_status']
            })
            subtitle = f"Managing {schedule_result['group_name']} • {schedule_result['total_members']} members"
        else:
            group_info = dbc.Alert("Could not load group information", color="warning")
            subtitle = "Group information unavailable"
        
        # Create position list
        from components.payment_position_management import create_payment_position_list
        position_list = create_payment_position_list(positions_data)
        
        # Create dropdown options for swapping
        swap_options = []
        for member in positions_data:
            if member.get('payment_position'):
                swap_options.append({
                    'label': f"{member['full_name']} (Position #{member['payment_position']})",
                    'value': member['user_id']
                })
        
        # Create payment schedule components
        if schedule_result.get('success'):
            from components.payment_position_management import (
                create_next_recipient_highlight,
                create_payment_schedule_list
            )
            next_recipient = create_next_recipient_highlight(schedule_result.get('next_recipient'))
            schedule_list = create_payment_schedule_list(schedule_result.get('schedule', []))
        else:
            next_recipient = dbc.Alert("Schedule unavailable", color="warning")
            schedule_list = html.Div()
        
        # Store data for other callbacks
        store_data = {
            'group_id': group_id,
            'positions_data': positions_data,
            'schedule_data': schedule_result if schedule_result.get('success') else {}
        }
        
        return (group_info, subtitle, position_list, swap_options, swap_options, 
                next_recipient, schedule_list, store_data)
        
    except Exception as e:
        print(f"Error loading payment positions data: {e}")
        error_alert = dbc.Alert(f"Error loading data: {str(e)}", color="danger")
        return error_alert, "Error", html.Div(), [], [], html.Div(), html.Div(), {}

# Callback to handle payment position actions
@callback(
    [Output("page-payment-position-alert", "children"),
     Output("page-payment-position-list", "children", allow_duplicate=True),
     Output("page-payment-position-swap-member1", "options", allow_duplicate=True),
     Output("page-payment-position-swap-member2", "options", allow_duplicate=True),
     Output("page-payment-schedule-next-recipient", "children", allow_duplicate=True),
     Output("page-payment-schedule-list", "children", allow_duplicate=True)],
    [Input("page-payment-position-random-btn", "n_clicks"),
     Input("page-payment-position-auto-btn", "n_clicks"),
     Input("page-payment-position-validate-btn", "n_clicks"),
     Input("page-payment-position-swap-btn", "n_clicks")],
    [State("payment-positions-group-store", "data"),
     State("page-payment-position-swap-member1", "value"),
     State("page-payment-position-swap-member2", "value")],
    prevent_initial_call=True
)
def handle_payment_position_actions(random_clicks, auto_clicks, validate_clicks, swap_clicks,
                                   group_store, swap_member1, swap_member2):
    """Handle payment position management actions."""
    ctx = dash.callback_context
    if not ctx.triggered or not group_store:
        return [dash.no_update] * 6
    
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    group_id = group_store.get("group_id")
    
    if not group_id:
        error_alert = dbc.Alert("No group selected", color="danger")
        return error_alert, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
    
    try:
        from services.payment_position_service import (
            assign_random_positions,
            auto_assign_missing_positions,
            validate_payment_positions,
            swap_payment_positions,
            get_group_payment_positions,
            get_payment_schedule
        )
        
        alert_content = None
        
        if triggered_id == "page-payment-position-random-btn":
            result = assign_random_positions(group_id)
            if result['success']:
                alert_content = dbc.Alert(result['message'], color="success", dismissable=True)
            else:
                alert_content = dbc.Alert(result['error'], color="danger", dismissable=True)
                
        elif triggered_id == "page-payment-position-auto-btn":
            result = auto_assign_missing_positions(group_id)
            if result['success']:
                alert_content = dbc.Alert(result['message'], color="success", dismissable=True)
            else:
                alert_content = dbc.Alert(result['error'], color="danger", dismissable=True)
                
        elif triggered_id == "page-payment-position-validate-btn":
            result = validate_payment_positions(group_id)
            if result['success']:
                if result['valid']:
                    alert_content = dbc.Alert(result['message'], color="success", dismissable=True)
                else:
                    issues_list = html.Ul([html.Li(issue) for issue in result['issues']])
                    alert_content = dbc.Alert([
                        html.H6("Validation Issues Found:"),
                        issues_list
                    ], color="warning", dismissable=True)
            else:
                alert_content = dbc.Alert(result['error'], color="danger", dismissable=True)
                
        elif triggered_id == "page-payment-position-swap-btn":
            if not swap_member1 or not swap_member2:
                alert_content = dbc.Alert("Please select both members to swap", color="warning", dismissable=True)
            elif swap_member1 == swap_member2:
                alert_content = dbc.Alert("Please select different members to swap", color="warning", dismissable=True)
            else:
                result = swap_payment_positions(group_id, swap_member1, swap_member2)
                if result['success']:
                    alert_content = dbc.Alert(result['message'], color="success", dismissable=True)
                else:
                    alert_content = dbc.Alert(result['error'], color="danger", dismissable=True)
        
        # Reload data after any action
        positions_data = get_group_payment_positions(group_id)
        schedule_result = get_payment_schedule(group_id)
        
        # Update position list
        from components.payment_position_management import create_payment_position_list
        position_list = create_payment_position_list(positions_data)
        
        # Update swap options
        swap_options = []
        for member in positions_data:
            if member.get('payment_position'):
                swap_options.append({
                    'label': f"{member['full_name']} (Position #{member['payment_position']})",
                    'value': member['user_id']
                })
        
        # Update schedule components
        if schedule_result.get('success'):
            from components.payment_position_management import (
                create_next_recipient_highlight,
                create_payment_schedule_list
            )
            next_recipient = create_next_recipient_highlight(schedule_result.get('next_recipient'))
            schedule_list = create_payment_schedule_list(schedule_result.get('schedule', []))
        else:
            next_recipient = dbc.Alert("Schedule unavailable", color="warning")
            schedule_list = html.Div()
        
        return alert_content, position_list, swap_options, swap_options, next_recipient, schedule_list
        
    except Exception as e:
        print(f"Error handling payment position action: {e}")
        error_alert = dbc.Alert(f"Error: {str(e)}", color="danger", dismissable=True)
        return error_alert, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update 