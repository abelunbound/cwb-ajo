"""
Member Management Page

This page provides a dedicated interface for managing group members,
replacing the modal-based approach with a full-page experience.
"""

import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc

# Register the page with URL parameter for group_id
dash.register_page(__name__, path_template="/member-management/<group_id>", title="Member Management | Ajo")

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
                    {"label": "Member Management", "active": True},
                ],
                className="mb-3"
            ),
            
            # Page title and actions
            html.Div(
                className="d-flex justify-content-between align-items-center",
                children=[
                    html.Div([
                        html.H1("Member Management", className="dashboard-title mb-1"),
                        html.P(id="member-management-subtitle", className="dashboard-subtitle mb-0"),
                    ]),
                    html.Div([
                        dbc.Button(
                            [html.I(className="fas fa-arrow-left me-2"), "Back to Groups"],
                            href="/groups",
                            color="outline-secondary",
                            className="me-2"
                        ),
                        dbc.Button(
                            [html.I(className="fas fa-user-plus me-2"), "Invite Member"],
                            id="page-invite-member-btn",
                            color="primary"
                        )
                    ])
                ]
            )
        ]
    )

def create_member_management_content():
    """Create the main content area for member management."""
    return html.Div([
        # Group information card
        html.Div(
            id="member-management-group-info",
            className="mb-4"
        ),
        
        # Statistics overview
        html.Div(
            id="member-management-stats",
            className="mb-4"
        ),
        
        # Main content with tabs
        dbc.Tabs(
            [
                dbc.Tab(
                    label="Members",
                    tab_id="members-tab",
                    children=[
                        html.Div(
                            className="mt-4",
                            children=[
                                # Member list
                                html.Div(id="member-management-member-list", children=[
                                    dbc.Spinner(color="primary", size="lg")
                                ])
                            ]
                        )
                    ]
                ),
                dbc.Tab(
                    label="Activity",
                    tab_id="activity-tab",
                    children=[
                        html.Div(
                            className="mt-4",
                            children=[
                                html.H5("Recent Member Activity", className="mb-3"),
                                html.Div(id="member-management-activity-list", children=[
                                    dbc.Spinner(color="primary", size="lg")
                                ])
                            ]
                        )
                    ]
                ),
                dbc.Tab(
                    label="Communication",
                    tab_id="communication-tab",
                    children=[
                        html.Div(
                            className="mt-4",
                            children=[
                                html.H5("Group Communication", className="mb-3"),
                                dbc.ButtonGroup(
                                    [
                                        dbc.Button(
                                            [html.I(className="fas fa-bullhorn me-2"), "Send Announcement"],
                                            id="page-send-announcement-btn",
                                            color="primary",
                                            size="sm"
                                        ),
                                        dbc.Button(
                                            [html.I(className="fas fa-envelope me-2"), "Contact All"],
                                            id="page-contact-all-btn",
                                            color="info",
                                            size="sm"
                                        )
                                    ]
                                ),
                                html.Hr(),
                                html.Div(id="member-management-communication-history", className="mt-3")
                            ]
                        )
                    ]
                )
            ],
            id="member-management-tabs",
            active_tab="members-tab"
        ),
        
        # Alert area for feedback
        html.Div(id="member-management-alert", className="mt-4")
    ])

def create_action_buttons():
    """Create action buttons for the page."""
    return html.Div(
        className="border-top pt-4 mt-4",
        children=[
            html.H6("Quick Actions", className="mb-3"),
            dbc.ButtonGroup(
                [
                    dbc.Button(
                        [html.I(className="fas fa-download me-2"), "Export Member List"],
                        id="page-export-members-btn",
                        color="success",
                        size="sm"
                    ),
                    dbc.Button(
                        [html.I(className="fas fa-refresh me-2"), "Refresh Data"],
                        id="page-refresh-data-btn",
                        color="outline-secondary",
                        size="sm"
                    )
                ]
            )
        ]
    )

def layout(group_id=None, **kwargs):
    """Layout for member management page."""
    if not group_id:
        return html.Div([
            dbc.Alert(
                [
                    html.H4("Invalid Group", className="alert-heading"),
                    html.P("No group ID provided. Please select a group to manage members."),
                    html.Hr(),
                    dbc.Button("Go to Groups", href="/groups", color="primary")
                ],
                color="warning",
                className="m-4"
            )
        ])
    
    return html.Div([
        # Store for group context
        dcc.Store(id="member-management-group-store", data={"group_id": group_id}),
        dcc.Store(id="member-management-data-store", data={}),
        
        # Page header with breadcrumb
        create_page_header(group_id),
        
        # Main content
        create_member_management_content(),
        
        # Action buttons
        create_action_buttons(),
        
        # Modals for member actions (still needed for edit/remove actions)
        html.Div(id="member-management-modals")
    ])

# Callback to load group information and member data
@callback(
    [Output("member-management-group-info", "children"),
     Output("member-management-subtitle", "children"),
     Output("member-management-stats", "children"),
     Output("member-management-member-list", "children"),
     Output("member-management-data-store", "data")],
    [Input("member-management-group-store", "data"),
     Input("page-refresh-data-btn", "n_clicks")],
    [State("session-store", "data")],
    prevent_initial_call=False
)
def load_member_management_data(group_store, refresh_clicks, session_data):
    """Load group and member data for the page."""
    if not group_store or not group_store.get("group_id"):
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
    
    group_id = group_store["group_id"]
    
    # Check if user is logged in
    if not session_data or not session_data.get('logged_in'):
        return (
            dbc.Alert("Please log in to view member management.", color="warning"),
            "Access Denied",
            html.Div(),
            html.Div(),
            {}
        )
    
    try:
        # Load group data from user's groups
        from functions.database import get_ajo_db_connection
        import psycopg2
        
        conn = get_ajo_db_connection()
        if not conn:
            return (
                dbc.Alert("Database connection failed.", color="danger"),
                "Error",
                html.Div(),
                html.Div(),
                {}
            )
        
        cursor = conn.cursor()
        
        # Get group information
        cursor.execute("""
            SELECT ag.name, ag.contribution_amount, ag.frequency, ag.status,
                   ag.max_members, 
                   (SELECT COUNT(*) FROM group_members gm WHERE gm.group_id = ag.id AND gm.status = 'active') as current_members,
                   ag.start_date, ag.end_date
            FROM ajo_groups ag
            WHERE ag.id = %s
        """, (group_id,))
        
        group_result = cursor.fetchone()
        if not group_result:
            cursor.close()
            conn.close()
            return (
                dbc.Alert("Group not found.", color="warning"),
                "Group Not Found",
                html.Div(),
                html.Div(),
                {}
            )
        
        group_data = {
            'group_id': group_id,
            'group_name': group_result[0],  # This is 'name' from ajo_groups
            'contribution_amount': group_result[1],
            'frequency': group_result[2],
            'group_status': group_result[3],  # This is 'status' from ajo_groups
            'max_members': group_result[4],
            'current_members': group_result[5],  # This is calculated count
            'start_date': group_result[6],
            'end_date': group_result[7]
        }
        
        # Load member data
        try:
            from functions.group_membership_service import get_group_members
            members = get_group_members(group_id, include_inactive=True)
            
            # Format member data
            formatted_members = []
            if members:
                for member in members:
                    formatted_members.append({
                        'id': member.get('user_id'),
                        'full_name': member.get('full_name', 'Unknown'),
                        'email': member.get('email', ''),
                        'role': member.get('role', 'member'),
                        'status': member.get('status', 'active'),
                        'payment_position': member.get('payment_position'),
                        'join_date': member.get('join_date', 'Unknown')
                    })
            
        except ImportError:
            # Fallback to mock data if service not available
            formatted_members = [
                {
                    'id': 1,
                    'full_name': 'John Doe',
                    'email': 'john@example.com',
                    'role': 'admin',
                    'status': 'active',
                    'payment_position': 1,
                    'join_date': 'Jan 2024'
                },
                {
                    'id': 2,
                    'full_name': 'Jane Smith',
                    'email': 'jane@example.com',
                    'role': 'member',
                    'status': 'active',
                    'payment_position': 2,
                    'join_date': 'Feb 2024'
                }
            ]
        
        cursor.close()
        conn.close()
        
        # Create group info card
        group_info = create_group_info_card(group_data)
        
        # Create subtitle
        subtitle = f"Managing {group_data['group_name']} • {group_data['current_members']} members"
        
        # Create stats overview
        stats_data = {
            'total_members': len(formatted_members),
            'active_members': len([m for m in formatted_members if m.get('status') == 'active']),
            'pending_members': len([m for m in formatted_members if m.get('status') == 'pending']),
            'suspended_members': len([m for m in formatted_members if m.get('status') == 'suspended']),
            'admin_count': len([m for m in formatted_members if m.get('role') == 'admin']),
            'recent_activity': 1  # Placeholder
        }
        
        from components.membership_management import create_member_stats_overview, create_member_list
        stats_component = create_member_stats_overview(stats_data)
        
        # Create member list
        member_list_component = create_member_list(formatted_members)
        
        # Store data for other callbacks
        store_data = {
            'group_data': group_data,
            'members': formatted_members,
            'stats': stats_data
        }
        
        return group_info, subtitle, stats_component, member_list_component, store_data
        
    except Exception as e:
        return (
            dbc.Alert(f"Error loading data: {str(e)}", color="danger"),
            "Error",
            html.Div(),
            html.Div(),
            {}
        )

def create_group_info_card(group_data):
    """Create a card displaying group information."""
    return dbc.Card(
        [
            dbc.CardHeader(
                html.H5(f"Group: {group_data['group_name']}", className="mb-0")
            ),
            dbc.CardBody(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    html.Strong("Contribution Amount:"),
                                    html.P(f"£{group_data['contribution_amount']}", className="mb-2")
                                ],
                                md=3
                            ),
                            dbc.Col(
                                [
                                    html.Strong("Frequency:"),
                                    html.P(group_data['frequency'].title(), className="mb-2")
                                ],
                                md=3
                            ),
                            dbc.Col(
                                [
                                    html.Strong("Status:"),
                                    html.P(
                                        dbc.Badge(
                                            group_data['group_status'].title(),
                                            color="success" if group_data['group_status'] == 'active' else "warning"
                                        ),
                                        className="mb-2"
                                    )
                                ],
                                md=3
                            ),
                            dbc.Col(
                                [
                                    html.Strong("Members:"),
                                    html.P(f"{group_data['current_members']}/{group_data['max_members']}", className="mb-2")
                                ],
                                md=3
                            )
                        ]
                    )
                ]
            )
        ],
        className="mb-4"
    )

# Callback to load activity data
@callback(
    Output("member-management-activity-list", "children"),
    [Input("member-management-tabs", "active_tab"),
     Input("member-management-data-store", "data")],
    prevent_initial_call=True
)
def load_activity_data(active_tab, store_data):
    """Load member activity data when activity tab is selected."""
    if active_tab != "activity-tab" or not store_data:
        return dash.no_update
    
    # Mock activity data for now
    from components.membership_management import create_member_activity_list
    
    mock_activities = [
        {
            'id': 1,
            'member_name': 'John Doe',
            'action': 'joined_group',
            'timestamp': '2024-01-15 10:30:00',
            'details': 'Joined the group as admin'
        },
        {
            'id': 2,
            'member_name': 'Jane Smith',
            'action': 'made_payment',
            'timestamp': '2024-01-14 14:20:00',
            'details': 'Made monthly contribution of £100'
        }
    ]
    
    return create_member_activity_list(mock_activities) 