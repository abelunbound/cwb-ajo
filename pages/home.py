# import dash
# from dash import html
# from components.dashboard_cards import create_dashboard_cards
# from components.groups import create_groups_section
# from components.activity import create_activity_section
# from components.modals import create_group_modal, create_success_modal

# # Register the page
# dash.register_page(__name__, path="/", title="Dashboard | Ajo", name="Dashboard")

# # Dashboard Header component
# def create_dashboard_header():
#     return html.Div(
#         className="dashboard-header",
#         children=[
#             html.H1("Welcome back, Abel!", className="dashboard-title"),
#             html.P("Here's an overview of your Ajo activities.", className="dashboard-subtitle"),
#         ]
#     )

# # Layout for this page
# layout = html.Div([
#     # Dashboard Header
#     create_dashboard_header(),
    
#     # Dashboard Cards
#     create_dashboard_cards(),
    
#     # Groups Section
#     create_groups_section(),
    
#     # Activity Section
#     create_activity_section(),
    
#     # Modals
#     create_group_modal(),
#     create_success_modal(),
# ])

import dash
from dash import html, callback, dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from components.dashboard_cards import create_dashboard_cards
from components.activity import create_activity_section

# Register the page
dash.register_page(__name__, path="/", title="Dashboard | Ajo", name="Dashboard")

# Dashboard Header component
def create_dashboard_header(name="Abel"):
    return html.Div(
        className="dashboard-header",
        children=[
            html.H1(f"Welcome back, {name}!", className="dashboard-title"),
            html.P("Here's an overview of your Ajo activities.", className="dashboard-subtitle"),
        ]
    )

def create_group_card(group_data, member_count=0):
    """Create a dynamic group card based on database data."""
    user_icon = html.I(className="fas fa-users", style={"marginRight": "5px"})
    
    # Get max_members from group details (need to fetch separately)
    max_members = get_group_max_members(group_data['group_id'])
    
    # Calculate total pool
    total_pool = float(group_data['contribution_amount']) * max_members
    
    # Format contribution amount
    contribution_text = f"£{group_data['contribution_amount']:.0f} per {group_data['frequency']}"
    
    # Create member avatars (simplified version)
    avatars = []
    colors = ["#5F2EEA", "#2ECC71", "#F7B731", "#E74C3C", "#3498DB", "#9B59B6", "#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4"]
    
    if member_count > 0:
        # Show first few members as letters
        for i in range(min(member_count, 3)):
            letter = chr(65 + i)  # A, B, C, etc.
            avatars.append(
                html.Div(letter, className="avatar", style={"backgroundColor": colors[i % len(colors)]})
            )
        
        # Show +X if more members
        if member_count > 3:
            avatars.append(
                html.Div(f"+{member_count - 3}", className="avatar", style={"backgroundColor": colors[3 % len(colors)]})
            )
    
    return html.Div(
        className="col-lg-4 col-md-6 mb-4",
        children=[
            html.Div(
                className="card group-card",
                children=[
                    html.Div(
                        className="group-card-header",
                        children=[
                            html.Div(
                                className="group-info",
                                children=[
                                    html.H3(group_data['group_name']),
                                    html.Div(
                                        className="members-count",
                                        children=[user_icon, f"{member_count} members"]
                                    ),
                                ]
                            ),
                            html.Span(group_data['group_status'].title(), 
                                    className=f"group-status status-{group_data['group_status'].lower()}"),
                        ]
                    ),
                    html.Div(
                        className="group-details",
                        children=[
                            html.Div(
                                className="detail-item",
                                children=[
                                    html.Div("Contribution", className="detail-label"),
                                    html.Div(contribution_text, className="detail-value"),
                                ]
                            ),
                            html.Div(
                                className="detail-item",
                                children=[
                                    html.Div("Total pool", className="detail-label"),
                                    html.Div(f"£{total_pool:,.0f}", className="detail-value"),
                                ]
                            ),
                            html.Div(
                                className="detail-item",
                                children=[
                                    html.Div("Your turn", className="detail-label"),
                                    html.Div("TBD", className="detail-value"),  # This would need payment order logic
                                ]
                            ),
                            html.Div(
                                className="detail-item",
                                children=[
                                    html.Div("End date", className="detail-label"),
                                    html.Div(group_data['end_date'].strftime("%b %Y") if group_data['end_date'] else "TBD", className="detail-value"),
                                ]
                            ),
                        ]
                    ),
                    html.Div(
                        className="member-avatars",
                        children=avatars
                    ),
                    html.Div(
                        className="text-end",
                        children=[
                            dbc.Button("View Details", outline=True, color="primary", className="me-2"),
                            dbc.Button("Invite Member", color="success", size="sm", 
                                     id={"type": "invite-member-btn", "group_id": group_data['group_id']})
                        ]
                    ),
                ]
            )
        ]
    )

def create_create_group_card():
    """Create the 'Create New Ajo Group' card."""
    plus_icon = html.I(className="fas fa-plus", style={"fontSize": "24px"})
    
    return html.Div(
        className="col-lg-4 col-md-6 mb-4",
        children=[
            html.Div(
                className="create-group",
                id={"type": "create-group-trigger", "location": "groups-card"},
                children=[
                    plus_icon,
                    html.Span("Create New Ajo Group", className="create-group-text mt-2"),
                ]
            )
        ]
    )

def create_discover_groups_card():
    """Create the 'Discover Groups' card."""
    search_icon = html.I(className="fas fa-search", style={"fontSize": "24px"})
    
    return html.Div(
        className="col-lg-4 col-md-6 mb-4",
        children=[
            html.A(
                href="/discover_groups",
                className="create-group",
                style={"textDecoration": "none", "color": "inherit"},
                children=[
                    search_icon,
                    html.Span("Discover Groups", className="create-group-text mt-2"),
                ]
            )
        ]
    )

def get_group_member_count(group_id):
    """Get the current member count for a group."""
    try:
        from functions.group_membership_service import get_group_members
        members = get_group_members(group_id, include_inactive=False)
        return len(members) if members else 0
    except Exception as e:
        print(f"Error getting member count for group {group_id}: {e}")
        return 0

def get_group_max_members(group_id):
    """Get the maximum members allowed for a group."""
    try:
        from services.group_service import get_group_by_id
        group = get_group_by_id(group_id)
        return group['max_members'] if group else 8  # Default fallback
    except Exception as e:
        print(f"Error getting max members for group {group_id}: {e}")
        return 8  # Default fallback

def create_loading_indicator():
    """Create a loading indicator for groups section."""
    return html.Div(
        className="text-center py-4",
        children=[
            dbc.Spinner(
                html.Div(
                    [
                        html.I(className="fas fa-users me-2"),
                        "Loading your Ajo groups..."
                    ],
                    className="text-muted"
                ),
                color="primary"
            )
        ]
    )

def create_dynamic_groups_section(user_groups=None, is_loading=False):
    """Create the groups section with dynamic data."""
    
    # Create group cards based on state
    group_cards = []
    
    if is_loading:
        # Show loading state with fallback cards
        group_cards = [
            create_create_group_card(),
            create_discover_groups_card()
        ]
        loading_section = create_loading_indicator()
    else:
        # Always show create and discover cards first
        group_cards.append(create_create_group_card())
        group_cards.append(create_discover_groups_card())
        
        if user_groups and len(user_groups) > 0:
            # Add user's groups after the fallback cards
            for group in user_groups:
                # Get actual member count
                member_count = get_group_member_count(group['group_id'])
                group_cards.append(create_group_card(group, member_count))
        
        loading_section = None
    
    return html.Section(
        className="mb-5",
        children=[
            # Section header
            html.Div(
                className="section-header",
                children=[
                    html.H2("My Ajo Groups", className="section-title"),
                    dbc.Button("+ New Group", color="primary", id={"type": "create-group-trigger", "location": "groups-section"}),
                ]
            ),
            # Loading indicator (if loading)
            loading_section if loading_section else html.Div(),
            # Group cards
            html.Div(
                className="row",
                children=group_cards
            ),
        ]
    )

# Layout for this page
def layout():
    return html.Div([
        # Store for user groups data
        dcc.Store(id='user-groups-store'),
        dcc.Store(id='groups-loading-store', data=True),  # Track loading state
        
        # Dashboard Header
        html.Div(id='dashboard-header-container'),
        
        # Dashboard Cards
        create_dashboard_cards(),
        
        # Groups Section (will be populated by callback)
        html.Div(
            id='groups-section-container',
            children=create_dynamic_groups_section(user_groups=None, is_loading=True)  # Show loading initially
        ),
        
        # Activity Section
        create_activity_section(),
    ])

# Callback to load user data and groups
@callback(
    [Output('dashboard-header-container', 'children'),
     Output('user-groups-store', 'data'),
     Output('groups-section-container', 'children'),
     Output('groups-loading-store', 'data')],
    Input('session-store', 'data'),
    prevent_initial_call=False
)
def load_user_dashboard_data(session_data):
    """Load user dashboard data including groups."""
    try:
        name = "Abel"  # Default name
        user_groups = []
        
        if session_data and session_data.get('user_info'):
            user_info = session_data['user_info']
            name = user_info.get('name', name)
            user_id = user_info.get('id')
            
            if user_id:
                try:
                    # Import the function to get user groups
                    from functions.group_membership_service import get_user_groups
                    
                    # Get user's groups
                    user_groups = get_user_groups(user_id, include_inactive=False)
                    if user_groups is None:
                        user_groups = []
                    
                    print(f"Loaded {len(user_groups)} groups for user {user_id}")
                        
                except Exception as e:
                    print(f"Error loading user groups: {e}")
                    user_groups = []
        
        # Create dashboard components
        header = create_dashboard_header(name)
        groups_section = create_dynamic_groups_section(user_groups, is_loading=False)  # No longer loading
        
        return header, user_groups, groups_section, False  # Set loading to False
        
    except Exception as e:
        print(f"Error in load_user_dashboard_data callback: {e}")
        # Return safe defaults
        header = create_dashboard_header("User")
        groups_section = create_dynamic_groups_section([], is_loading=False)
        return header, [], groups_section, False