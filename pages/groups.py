import dash
from dash import html, dcc, callback
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

# Register the page
dash.register_page(__name__, path="/groups", title="My Groups | Ajo", name="My Groups")

# Page header component
def create_page_header():
    return html.Div(
        className="dashboard-header",
        children=[
            html.Div(
                className="d-flex justify-content-between align-items-center mb-3",
                children=[
                    html.Div([
                        html.H1("My Ajo Groups", className="dashboard-title mb-1"),
                        html.P("View and manage all your Ajo groups.", className="dashboard-subtitle mb-0"),
                    ]),
                    html.Div([
                        dbc.Button(
                            [html.I(className="fas fa-search me-2"), "Discover Groups"],
                            href="/discover-groups",
                            color="outline-primary",
                            className="me-2"
                        ),
                        dbc.Button(
                            [html.I(className="fas fa-plus me-2"), "New Group"],
                            color="primary",
                            id={"type": "create-group-trigger", "location": "groups-page-header"}
                        ),
                    ])
                ]
            ),
        ]
    )

# Groups filter component
def create_groups_filter():
    return html.Div(
        className="filters-section mb-4",
        children=[
            html.Div(
                className="row align-items-center",
                children=[
                    html.Div(
                        className="col-md-6 mb-3 mb-md-0",
                        children=[
                            html.Label("Filter Groups:", className="me-2"),
                            dbc.Select(
                                id="group-filter",
                                options=[
                                    {"label": "All Groups", "value": "all"},
                                    {"label": "Active Groups", "value": "active"},
                                    {"label": "Completed Groups", "value": "completed"},
                                    {"label": "Groups I Manage", "value": "managed"},
                                ],
                                value="all",
                                className="d-inline-block w-auto",
                            ),
                        ]
                    ),
                    html.Div(
                        className="col-md-6 d-flex justify-content-md-end",
                        children=[
                            dbc.Input(
                                type="text",
                                placeholder="Search groups...",
                                className="me-2",
                                style={"width": "200px"}
                            ),
                            dbc.Button("Search", color="primary"),
                        ]
                    ),
                ]
            )
        ]
    )

def create_group_card(group_data, member_count=0):
    """Create a dynamic group card based on database data."""
    user_icon = html.I(className="fas fa-users", style={"marginRight": "5px"})
    
    # Get max_members from group details
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
                                        children=[user_icon, f"{member_count} members • ID: {group_data['group_id']}"]
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
                                    html.Div("Your role", className="detail-label"),
                                    html.Div(group_data['role'].title(), className="detail-value"),
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
                            dbc.ButtonGroup([
                                dbc.Button("Invite Member", color="success", size="sm", 
                                         id={"type": "invite-member-btn", "group_id": group_data['group_id']}),
                                dbc.Button("Manage Members", color="info", size="sm",
                                         id={"type": "manage-members-btn", "group_id": group_data['group_id']})
                            ], size="sm")
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
                id={"type": "create-group-trigger", "location": "groups-page-card"},
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
                href="/discover-groups",
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
        if user_groups and len(user_groups) > 0:
            # Add user's groups FIRST
            for group in user_groups:
                # Get actual member count
                member_count = get_group_member_count(group['group_id'])
                group_cards.append(create_group_card(group, member_count))
        
        # Then add create and discover cards AFTER the user's groups
        group_cards.append(create_create_group_card())
        group_cards.append(create_discover_groups_card())
        
        loading_section = None
    
    return html.Section(
        className="mb-5",
        children=[
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
        # Enhanced store for complete user groups data with pattern-matching ID
        dcc.Store(id={"type": "user-groups-store", "page": "groups"}),
        dcc.Store(id='groups-page-loading-store', data=True),
        dcc.Store(id={"type": "selected-group-store", "page": "groups"}, data={}),  # Pattern-matching store for invitation context
        
        # Page Header
        create_page_header(),
        
        # Groups Filter
        create_groups_filter(),
        
        # Groups Section (will be populated by callback)
        html.Div(
            id='groups-page-section-container',
            children=create_dynamic_groups_section_from_store(user_groups=None, is_loading=True)  # Show loading initially
        ),
    ])

def fetch_complete_groups_data(user_id):
    """Fetch complete groups data with member counts in one operation."""
    try:
        from functions.group_membership_service import get_user_groups, get_group_members
        from services.group_service import get_group_by_id
        
        # Get user's groups
        user_groups = get_user_groups(user_id, include_inactive=False)
        if not user_groups:
            return []
        
        complete_groups_data = []
        
        for group in user_groups:
            try:
                # Get additional group details
                group_details = get_group_by_id(group['group_id'])
                
                # Get current members
                members = get_group_members(group['group_id'], include_inactive=False)
                member_count = len(members) if members else 0
                
                # Combine all data
                complete_group = {
                    # From group membership
                    'group_id': group['group_id'],
                    'group_name': group['group_name'],
                    'group_description': group['group_description'],
                    'contribution_amount': group['contribution_amount'],
                    'frequency': group['frequency'],
                    'role': group['role'],
                    'payment_position': group['payment_position'],
                    'join_date': group['join_date'],
                    'membership_status': group['membership_status'],
                    'start_date': group['start_date'],
                    'end_date': group['end_date'],
                    'group_status': group['group_status'],
                    
                    # From group details
                    'max_members': group_details['max_members'] if group_details else 8,
                    'duration_months': group_details['duration_months'] if group_details else 12,
                    'created_by': group_details['created_by'] if group_details else None,
                    'invitation_code': group_details['invitation_code'] if group_details else None,
                    
                    # From members
                    'current_members': member_count,
                    'spots_available': (group_details['max_members'] if group_details else 8) - member_count,
                    'is_full': member_count >= (group_details['max_members'] if group_details else 8),
                    'member_details': members[:10] if members else [],  # Limit to first 10 for performance
                }
                
                complete_groups_data.append(complete_group)
                
            except Exception as e:
                print(f"Error processing group {group['group_id']}: {e}")
                # Add basic group data even if details fail
                complete_groups_data.append({
                    **group,
                    'max_members': 8,
                    'current_members': 0,
                    'spots_available': 8,
                    'is_full': False,
                    'member_details': []
                })
        
        return complete_groups_data
        
    except Exception as e:
        print(f"Error fetching complete groups data: {e}")
        return []

def get_group_from_store(groups_data, group_id):
    """Get group data from store instead of database."""
    if not groups_data:
        return None
    for group in groups_data:
        if group['group_id'] == group_id:
            return group
    return None

def create_group_card_from_store(group_data):
    """Create a dynamic group card using data from store."""
    user_icon = html.I(className="fas fa-users", style={"marginRight": "5px"})
    
    # All data is already in the store
    member_count = group_data['current_members']
    max_members = group_data['max_members']
    total_pool = float(group_data['contribution_amount']) * max_members
    contribution_text = f"£{group_data['contribution_amount']:.0f} per {group_data['frequency']}"
    
    # Create member avatars
    avatars = []
    colors = ["#5F2EEA", "#2ECC71", "#F7B731", "#E74C3C", "#3498DB", "#9B59B6", "#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4"]
    
    if member_count > 0:
        for i in range(min(member_count, 3)):
            letter = chr(65 + i)  # A, B, C, etc.
            avatars.append(
                html.Div(letter, className="avatar", style={"backgroundColor": colors[i % len(colors)]})
            )
        
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
                                        children=[user_icon, f"{member_count} members • ID: {group_data['group_id']}"]
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
                                    html.Div("Your role", className="detail-label"),
                                    html.Div(group_data['role'].title(), className="detail-value"),
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
                            dbc.ButtonGroup([
                                dbc.Button("Invite Member", color="success", size="sm", 
                                         id={"type": "invite-member-btn", "group_id": group_data['group_id']}),
                                dbc.Button("Manage Members", color="info", size="sm",
                                         id={"type": "manage-members-btn", "group_id": group_data['group_id']})
                            ], size="sm")
                        ]
                    ),
                ]
            )
        ]
    )

def create_dynamic_groups_section_from_store(user_groups=None, is_loading=False):
    """Create the groups section using data from store."""
    
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
        if user_groups and len(user_groups) > 0:
            # Add user's groups FIRST using store data
            for group in user_groups:
                group_cards.append(create_group_card_from_store(group))
        
        # Then add create and discover cards AFTER the user's groups
        group_cards.append(create_create_group_card())
        group_cards.append(create_discover_groups_card())
        
        loading_section = None
    
    return html.Section(
        className="mb-5",
        children=[
            # Loading indicator (if loading)
            loading_section if loading_section else html.Div(),
            # Group cards
            html.Div(
                className="row",
                children=group_cards
            ),
        ]
    )

# Callback to load user groups for this page using store-based approach
@callback(
    [Output({"type": "user-groups-store", "page": "groups"}, 'data'),
     Output('groups-page-section-container', 'children'),
     Output('groups-page-loading-store', 'data')],
    Input('session-store', 'data'),
    prevent_initial_call=False
)
def load_groups_page_data(session_data):
    """Load user groups data for the groups page using complete store approach."""
    try:
        user_groups = []
        
        if session_data and session_data.get('user_info'):
            user_info = session_data['user_info']
            user_id = user_info.get('id')
            
            if user_id:
                try:
                    # Fetch complete groups data in one operation
                    user_groups = fetch_complete_groups_data(user_id)
                    print(f"Groups page: Loaded complete data for {len(user_groups)} groups for user {user_id}")
                        
                except Exception as e:
                    print(f"Error loading complete groups data on groups page: {e}")
                    user_groups = []
        
        # Create groups section using store data
        groups_section = create_dynamic_groups_section_from_store(user_groups, is_loading=False)
        
        return user_groups, groups_section, False
        
    except Exception as e:
        print(f"Error in load_groups_page_data callback: {e}")
        # Return safe defaults
        groups_section = create_dynamic_groups_section_from_store([], is_loading=False)
        return [], groups_section, False