import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

# Initialize the Dash app
app = dash.Dash(__name__, 
                external_stylesheets=[dbc.themes.BOOTSTRAP, 'https://use.fontawesome.com/releases/v5.15.1/css/all.css'], 
                suppress_callback_exceptions=True,
                meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}])

# Define colors from the CSS
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

# Custom CSS
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
                            html.A("CWB", className="logo", href="#"),
                            html.Nav(
                                className="d-none d-md-block",
                                children=[
                                    html.Ul(
                                        className="nav",
                                        children=[
                                            html.Li(html.A("Dashboard", href="#", className="nav-link active")),
                                            html.Li(html.A("My Groups", href="#", className="nav-link")),
                                            html.Li(html.A("Payments", href="#", className="nav-link")),
                                            html.Li(html.A("Support", href="#", className="nav-link")),
                                        ]
                                    )
                                ]
                            ),
                            html.Div(
                                className="d-flex",
                                children=[
                                    dbc.Button("Profile", color="", className="btn-outline-primary me-2"),
                                    dbc.Button("+ Create Group", color="primary", className="d-none", id="create-group-btn"),
                                    dbc.Button("Logout", color="primary", className="", id="logout-test"),
                                    
                                ]
                            )
                        ]
                    )
                ]
            )
        ]
    )

# Dashboard Header component
def create_dashboard_header():
    return html.Div(
        className="dashboard-header",
        children=[
            html.H1("Welcome back, Abel!", className="dashboard-title"),
            html.P("Here's an overview of your Ajo activities.", className="dashboard-subtitle"),
        ]
    )

# Dashboard Stats Cards component
def create_dashboard_cards():
    return html.Div(
        className="row mb-4",
        children=[
            # Active Groups Card
            html.Div(
                className="col-md-3 col-sm-6 mb-4",
                children=[
                    html.Div(
                        className="card",
                        children=[
                            html.H3("Active Groups", className="card-title"),
                            html.Div("3", className="card-value"),
                            html.Div("You're participating in 3 Ajo groups", className="card-subtitle"),
                        ]
                    )
                ]
            ),
            # Total Contributions Card
            html.Div(
                className="col-md-3 col-sm-6 mb-4",
                children=[
                    html.Div(
                        className="card",
                        children=[
                            html.H3("Total Contributions", className="card-title"),
                            html.Div("£12,500", className="card-value"),
                            html.Div("Across all groups", className="card-subtitle"),
                        ]
                    )
                ]
            ),
            # Next Payout Card
            html.Div(
                className="col-md-3 col-sm-6 mb-4",
                children=[
                    html.Div(
                        className="card",
                        children=[
                            html.H3("Next Collection", className="card-title"),
                            html.Div("£5,000", className="card-value"),
                            html.Div("Scotland Ajo by March 2025", className="card-subtitle"),
                            html.Div(
                                className="progress-container",
                                children=[
                                    html.Div(
                                        className="progress-details",
                                        children=[
                                            html.Span("Collection due in:"),
                                            html.Span("60 days"),
                                        ]
                                    ),
                                    html.Div(
                                        className="progress-bar-container",
                                        children=[
                                            html.Div(className="progress-value", style={"width": "45%"}),
                                        ]
                                    ),
                                ]
                            ),
                        ]
                    )
                ]
            ),
            # Payment Due Card
            html.Div(
                className="col-md-3 col-sm-6 mb-4",
                children=[
                    html.Div(
                        className="card",
                        children=[
                            html.H3("Contribution Due", className="card-title"),
                            html.Div("£750", className="card-value"),
                            html.Div("For Office Colleagues Group", className="card-subtitle"),
                            html.Div(
                                className="progress-container",
                                children=[
                                    html.Div(
                                        className="progress-details",
                                        children=[
                                            html.Span("Due in"),
                                            html.Span("3 days"),
                                        ]
                                    ),
                                    html.Div(
                                        className="progress-bar-container",
                                        children=[
                                            html.Div(className="progress-value", style={"width": "75%"}),
                                        ]
                                    ),
                                ]
                            ),
                        ]
                    )
                ]
            ),
        ]
    )

# Groups Section component
def create_groups_section():
    # User icon SVG as HTML 
    user_icon = html.I(className="fas fa-users", style={"marginRight": "5px"})
    
    # Plus icon SVG as HTML
    plus_icon = html.I(className="fas fa-plus", style={"fontSize": "24px"})
    
    return html.Section(
        className="mb-5",
        children=[
            # Section header
            html.Div(
                className="section-header",
                children=[
                    html.H2("My Ajo Groups", className="section-title"),
                    dbc.Button("+ New Group", color="primary", id="new-group-btn"),
                ]
            ),
            # Group cards
            html.Div(
                className="row",
                children=[
                    # Family Savings Group Card
                    html.Div(
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
                                                    html.H3("Ogo Ajo Savings"),
                                                    html.Div(
                                                        className="members-count",
                                                        children=[user_icon, "8 members"]
                                                    ),
                                                ]
                                            ),
                                            html.Span("Active", className="group-status status-active"),
                                        ]
                                    ),
                                    html.Div(
                                        className="group-details",
                                        children=[
                                            html.Div(
                                                className="detail-item",
                                                children=[
                                                    html.Div("Contribution", className="detail-label"),
                                                    html.Div("£750 per month", className="detail-value"),
                                                ]
                                            ),
                                            html.Div(
                                                className="detail-item",
                                                children=[
                                                    html.Div("Total pool", className="detail-label"),
                                                    html.Div("£6,000", className="detail-value"),
                                                ]
                                            ),
                                            html.Div(
                                                className="detail-item",
                                                children=[
                                                    html.Div("Your turn (67%)", className="detail-label"),
                                                    html.Div("April 2025", className="detail-value"),
                                                ]
                                            ),
                                            html.Div(
                                                className="detail-item",
                                                children=[
                                                    html.Div("End date", className="detail-label"),
                                                    html.Div("Sept 2025", className="detail-value"),
                                                ]
                                            ),
                                        ]
                                    ),
                                    html.Div(
                                        className="member-avatars",
                                        children=[
                                            html.Div("A", className="avatar", style={"backgroundColor": "#5F2EEA"}),
                                            html.Div("B", className="avatar", style={"backgroundColor": "#2ECC71"}),
                                            html.Div("C", className="avatar", style={"backgroundColor": "#F7B731"}),
                                            html.Div("D", className="avatar", style={"backgroundColor": "#E74C3C"}),
                                            html.Div("E", className="avatar", style={"backgroundColor": "#3498DB"}),
                                            html.Div("F", className="avatar", style={"backgroundColor": "#9B59B6"}),
                                        ]
                                    ),
                                    html.Div(
                                        className="text-end",
                                        children=[
                                            dbc.Button("View Details", outline=True, color="primary"),
                                        ]
                                    ),
                                ]
                            )
                        ]
                    ),
                    
                    # Yettie Group Card
                    html.Div(
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
                                                    html.H3("Yettie Ajo"),
                                                    html.Div(
                                                        className="members-count",
                                                        children=[user_icon, "6 members"]
                                                    ),
                                                ]
                                            ),
                                            html.Span("Active", className="group-status status-active"),
                                        ]
                                    ),
                                    html.Div(
                                        className="group-details",
                                        children=[
                                            html.Div(
                                                className="detail-item",
                                                children=[
                                                    html.Div("Contribution", className="detail-label"),
                                                    html.Div("£250 / month", className="detail-value"),
                                                ]
                                            ),
                                            html.Div(
                                                className="detail-item",
                                                children=[
                                                    html.Div("Total pool", className="detail-label"),
                                                    html.Div("£1,500", className="detail-value"),
                                                ]
                                            ),
                                            html.Div(
                                                className="detail-item",
                                                children=[
                                                    html.Div("Your turn", className="detail-label"),
                                                    html.Div("June 2025", className="detail-value"),
                                                ]
                                            ),
                                            html.Div(
                                                className="detail-item",
                                                children=[
                                                    html.Div("End date", className="detail-label"),
                                                    html.Div("July 2025", className="detail-value"),
                                                ]
                                            ),
                                        ]
                                    ),
                                    html.Div(
                                        className="member-avatars",
                                        children=[
                                            html.Div("A", className="avatar", style={"backgroundColor": "#5F2EEA"}),
                                            html.Div("B", className="avatar", style={"backgroundColor": "#2ECC71"}),
                                            html.Div("C", className="avatar", style={"backgroundColor": "#F7B731"}),
                                            html.Div("+5", className="avatar", style={"backgroundColor": "#E74C3C"}),
                                        ]
                                    ),
                                    html.Div(
                                        className="text-end",
                                        children=[
                                            dbc.Button("View Details", outline=True, color="primary"),
                                        ]
                                    ),
                                ]
                            )
                        ]
                    ),
                    # Scotland Ajo Group Card
                    html.Div(
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
                                                    html.H3("Scotland Ajo"),
                                                    html.Div(
                                                        className="members-count",
                                                        children=[user_icon, "10 members"]
                                                    ),
                                                ]
                                            ),
                                            html.Span("Active", className="group-status status-active"),
                                        ]
                                    ),
                                    html.Div(
                                        className="group-details",
                                        children=[
                                            html.Div(
                                                className="detail-item",
                                                children=[
                                                    html.Div("Contribution", className="detail-label"),
                                                    html.Div("£500 per month", className="detail-value"),
                                                ]
                                            ),
                                            html.Div(
                                                className="detail-item",
                                                children=[
                                                    html.Div("Total pool", className="detail-label"),
                                                    html.Div("£5,000", className="detail-value"),
                                                ]
                                            ),
                                            html.Div(
                                                className="detail-item",
                                                children=[
                                                    html.Div("Your turn", className="detail-label"),
                                                    html.Div("April 2025", className="detail-value"),
                                                ]
                                            ),
                                            html.Div(
                                                className="detail-item",
                                                children=[
                                                    html.Div("End date", className="detail-label"),
                                                    html.Div("Oct 2025", className="detail-value"),
                                                ]
                                            ),
                                        ]
                                    ),
                                    html.Div(
                                        className="member-avatars",
                                        children=[
                                            html.Div("A", className="avatar", style={"backgroundColor": "#5F2EEA"}),
                                            html.Div("B", className="avatar", style={"backgroundColor": "#2ECC71"}),
                                            html.Div("C", className="avatar", style={"backgroundColor": "#F7B731"}),
                                            html.Div("+5", className="avatar", style={"backgroundColor": "#E74C3C"}),
                                        ]
                                    ),
                                    html.Div(
                                        className="text-end",
                                        children=[
                                            dbc.Button("View Details", outline=True, color="primary"),
                                        ]
                                    ),
                                ]
                            )
                        ]
                    ),

                    # Create New Group Card
                    html.Div(
                        className="col-lg-4 col-md-6 mb-4",
                        children=[
                            html.Div(
                                className="create-group",
                                id="create-group-card",
                                children=[
                                    plus_icon,
                                    html.Span("Create New Ajo Group", className="create-group-text mt-2"),
                                ]
                            )
                        ]
                    ),
                ]
            ),
        ]
    )

# Activity Section component
def create_activity_section():
    # Icons using Font Awesome 
    check_icon = html.I(className="fas fa-check", style={"fontSize": "20px"})
    
    # Chart icon
    chart_icon = html.I(className="fas fa-chart-line", style={"fontSize": "20px"})
    
    # Warning icon
    warning_icon = html.I(className="fas fa-exclamation-triangle", style={"fontSize": "20px"})
    
    # Money icon
    money_icon = html.I(className="fas fa-money-bill", style={"fontSize": "20px"})
    
    return html.Section(
        className="mb-5",
        children=[
            html.Div(
                className="section-header",
                children=[
                    html.H2("Recent Activity", className="section-title"),
                ]
            ),
            html.Div(
                className="activity-list",
                children=[
                    html.Div(
                        className="activity-item",
                        children=[
                            html.Div(className="activity-icon", children=[check_icon]),
                            html.Div(
                                className="activity-content",
                                children=[
                                    html.Div(
                                        className="activity-text",
                                        children=[
                                            html.Strong("Mary received the payout"),
                                            " for Family Savings Group"
                                        ]
                                    ),
                                    html.Div("Yesterday, 4:15 PM", className="activity-time"),
                                ]
                            ),
                            html.Div("£600", className="activity-amount"),
                        ]
                    ),
                    html.Div(
                        className="activity-item",
                        children=[
                            html.Div(className="activity-icon", children=[chart_icon]),
                            html.Div(
                                className="activity-content",
                                children=[
                                    html.Div(
                                        className="activity-text",
                                        children=[
                                            html.Strong("John joined"),
                                            " your Family Savings Group"
                                        ]
                                    ),
                                    html.Div("03 Feb, 2:30 PM", className="activity-time"),
                                ]
                            ),
                        ]
                    ),
                    html.Div(
                        className="activity-item",
                        children=[
                            html.Div(className="activity-icon", children=[warning_icon]),
                            html.Div(
                                className="activity-content",
                                children=[
                                    html.Div(
                                        className="activity-text",
                                        children=[
                                            html.Strong("You paid your contribution"),
                                            " for Office Colleagues Group"
                                        ]
                                    ),
                                    html.Div("Today, 10:25 AM", className="activity-time"),
                                ]
                            ),
                            html.Div("£100", className="activity-amount"),
                        ]
                    ),
                    html.Div(
                        className="activity-item",
                        children=[
                            html.Div(className="activity-icon", children=[money_icon]),
                            html.Div(
                                className="activity-content",
                                children=[
                                    html.Div(
                                        className="activity-text",
                                        children=[
                                            html.Strong("You created"),
                                            " a new Ajo group"
                                        ]
                                    ),
                                    html.Div("01 Feb, 9:15 AM", className="activity-time"),
                                ]
                            ),
                        ]
                    ),
                ]
            ),
        ]
    )

# Create Group Modal component
def create_group_modal():
    return dbc.Modal(
        [
            dbc.ModalHeader(html.H5("Create New Ajo Group", className="modal-title")),
            dbc.ModalBody(
                [
                    # Tabs
                    dbc.Tabs(
                        [
                            dbc.Tab(
                                [
                                    html.Div(
                                        className="form-group mt-3",
                                        children=[
                                            html.Label("Group Name"),
                                            dbc.Input(type="text", placeholder="e.g. Family Savings"),
                                        ]
                                    ),
                                    html.Div(
                                        className="form-group mt-3",
                                        children=[
                                            html.Label("Contribution Amount"),
                                            dbc.InputGroup([
                                                dbc.InputGroupText("£"),
                                                dbc.Input(type="number", placeholder="e.g. 100"),
                                            ]),
                                        ]
                                    ),
                                    html.Div(
                                        className="form-row mt-3",
                                        children=[
                                            html.Div(
                                                className="form-group col",
                                                children=[
                                                    html.Label("Contribution Frequency"),
                                                    dbc.Select(
                                                        options=[
                                                            {"label": "Weekly", "value": "weekly"},
                                                            {"label": "Monthly", "value": "monthly"},
                                                            {"label": "Bi-weekly", "value": "biweekly"},
                                                        ],
                                                        value="monthly",
                                                    ),
                                                ]
                                            ),
                                            html.Div(
                                                className="form-group col",
                                                children=[
                                                    html.Label("Number of Members"),
                                                    dbc.Input(type="number", placeholder="e.g. 6", min=2),
                                                ]
                                            ),
                                        ]
                                    ),
                                    html.Div(
                                        className="form-group mt-3",
                                        children=[
                                            html.Label("Group Description (Optional)"),
                                            dbc.Textarea(placeholder="What's the purpose of this Ajo group?", rows=3),
                                        ]
                                    ),
                                ],
                                label="Details",
                                tab_id="details",
                            ),
                            dbc.Tab(
                                [
                                    html.Div(
                                        className="form-group mt-3",
                                        children=[
                                            html.Label("Invite Members"),
                                            dbc.InputGroup([
                                                dbc.Input(type="email", placeholder="Enter email address"),
                                                dbc.Button("Add", color="primary"),
                                            ]),
                                        ]
                                    ),
                                    html.Div(
                                        className="mt-3",
                                        children=[
                                            html.Label("Added Members"),
                                            html.Div(
                                                className="invited-member",
                                                children=[
                                                    html.Div(
                                                        className="member-info",
                                                        children=[
                                                            html.Div("J", className="avatar", style={"backgroundColor": "#5F2EEA"}),
                                                            html.Div(
                                                                children=[
                                                                    html.Div("John Doe", className="member-name"),
                                                                    html.Div("john.doe@example.com", className="member-email"),
                                                                ]
                                                            ),
                                                        ]
                                                    ),
                                                    html.Button("×", className="remove-btn"),
                                                ]
                                            ),
                                            html.Div(
                                                className="invited-member",
                                                children=[
                                                    html.Div(
                                                        className="member-info",
                                                        children=[
                                                            html.Div("S", className="avatar", style={"backgroundColor": "#2ECC71"}),
                                                            html.Div(
                                                                children=[
                                                                    html.Div("Sarah Smith", className="member-name"),
                                                                    html.Div("sarah.smith@example.com", className="member-email"),
                                                                ]
                                                            ),
                                                        ]
                                                    ),
                                                    html.Button("×", className="remove-btn"),
                                                ]
                                            ),
                                        ]
                                    ),
                                ],
                                label="Members",
                                tab_id="members",
                            ),
                            dbc.Tab(
                                [
                                    html.P("Set the order in which members will receive payouts", className="mt-3"),
                                    html.Div(
                                        className="schedule-list",
                                        children=[
                                            html.Div(
                                                className="schedule-item",
                                                children=[
                                                    html.Div("Month 1", className="schedule-month"),
                                                    html.Div(
                                                        className="schedule-recipient",
                                                        children=[
                                                            html.Div("S", className="avatar", style={"backgroundColor": "#2ECC71"}),
                                                            html.Div("Sarah Smith"),
                                                        ]
                                                    ),
                                                ]
                                            ),
                                            html.Div(
                                                className="schedule-item",
                                                children=[
                                                    html.Div("Month 2", className="schedule-month"),
                                                    html.Div(
                                                        className="schedule-recipient",
                                                        children=[
                                                            html.Div("A", className="avatar", style={"backgroundColor": "#5F2EEA"}),
                                                            html.Div("Ade (You)"),
                                                            html.Span("You", className="badge ms-2"),
                                                        ]
                                                    ),
                                                ]
                                            ),
                                            html.Div(
                                                className="schedule-item",
                                                children=[
                                                    html.Div("Month 3", className="schedule-month"),
                                                    html.Div(
                                                        className="schedule-recipient",
                                                        children=[
                                                            html.Div("J", className="avatar", style={"backgroundColor": "#F7B731"}),
                                                            html.Div("John Doe"),
                                                        ]
                                                    ),
                                                ]
                                            ),
                                        ]
                                    ),
                                    html.Div(
                                        className="form-group mt-3",
                                        children=[
                                            html.Label("Payout Distribution Method"),
                                            dbc.RadioItems(
                                                options=[
                                                    {"label": "Random order", "value": "random"},
                                                    {"label": "Custom order (set manually)", "value": "custom"},
                                                    {"label": "Round-robin (rotating order)", "value": "roundrobin"},
                                                ],
                                                value="custom",
                                                className="mt-2",
                                            ),
                                        ]
                                    ),
                                ],
                                label="Schedule",
                                tab_id="schedule",
                            ),
                        ],
                        id="tabs",
                        active_tab="details",
                    ),
                ]
            ),
            dbc.ModalFooter(
                [
                    dbc.Button("Cancel", id="close-modal", color="secondary", className="me-2"),
                    dbc.Button("Create Group", id="save-group", color="primary"),
                ]
            ),
        ],
        id="create-group-modal",
        size="lg",
    )

# Success Modal component
def create_success_modal():
    return dbc.Modal(
        [
            dbc.ModalBody(
                [
                    html.Div(
                        className="success-container",
                        children=[
                            html.Div(
                                className="success-icon",
                                children=[
                                    html.I(className="fas fa-check-circle", style={"fontSize": "40px", "color": colors['success']}),
                                ]
                            ),
                            html.H3("Group Created Successfully!", className="success-title"),
                            html.P(
                                "Your new Ajo group has been created. Invitations have been sent to all members.",
                                className="success-message"
                            ),
                            dbc.Button("See Group Details", color="primary", className="me-2"),
                            dbc.Button("Close", id="close-success", color="link"),
                        ]
                    ),
                ]
            ),
        ],
        id="success-modal",
        centered=True,
    )

# Main layout
app.layout = html.Div(
    children=[
        # Header
        create_header(),
        
        # Main content
        html.Main(
            className="dashboard",
            children=[
                html.Div(
                    className="container",
                    children=[
                        # Dashboard Header
                        create_dashboard_header(),
                        
                        # Dashboard Cards
                        create_dashboard_cards(),
                        
                        # Groups Section
                        create_groups_section(),
                        
                        # Activity Section
                        create_activity_section(),
                    ]
                )
            ]
        ),
        
        # Modals
        create_group_modal(),
        create_success_modal(),
    ]
)

# Callbacks for modal functionality
@app.callback(
    Output("create-group-modal", "is_open"),
    [Input("create-group-btn", "n_clicks"), 
     Input("new-group-btn", "n_clicks"),
     Input("create-group-card", "n_clicks"),
     Input("close-modal", "n_clicks"),
     Input("save-group", "n_clicks")],
    [State("create-group-modal", "is_open")],
)
def toggle_modal(n1, n2, n3, n4, n5, is_open):
    if n1 or n2 or n3 or n4 or n5:
        return not is_open
    return is_open

@app.callback(
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

@app.callback(
    Output("success-modal", "is_open", allow_duplicate=True),
    [Input("close-success", "n_clicks")],
    [State("success-modal", "is_open")],
    prevent_initial_call=True,
)
def close_success_modal(n, is_open):
    if n:
        return False
    return is_open

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=True)