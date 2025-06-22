import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from components.group_discovery import create_discovery_section

# Register the page
dash.register_page(__name__, path="/discover-groups", title="Discover Groups | Ajo", name="Discover Groups")

# Page header component
def create_page_header():
    return html.Div(
        className="dashboard-header",
        children=[
            html.H1("Discover Ajo Groups", className="dashboard-title"),
            html.P("Find and join Ajo groups that match your savings goals.", className="dashboard-subtitle"),
        ]
    )

# Search and filter component
def create_search_and_filters():
    return html.Div(
        className="search-filters-section mb-4",
        children=[
            # Search bar
            html.Div(
                className="row mb-3",
                children=[
                    html.Div(
                        className="col-md-8 mb-3 mb-md-0",
                        children=[
                            dbc.InputGroup([
                                dbc.Input(
                                    id="discovery-search-input",
                                    type="text",
                                    placeholder="Search groups by name or description...",
                                    value=""
                                ),
                                dbc.Button(
                                    "Search",
                                    id="discovery-search-btn",
                                    color="primary",
                                    n_clicks=0
                                ),
                            ]),
                        ]
                    ),
                    html.Div(
                        className="col-md-4 d-flex justify-content-md-end",
                        children=[
                            dbc.Button(
                                "Clear Filters",
                                id="clear-filters-btn",
                                color="outline-secondary",
                                n_clicks=0
                            ),
                        ]
                    ),
                ]
            ),
            
            # Filter row
            html.Div(
                className="row",
                children=[
                    # Contribution amount filter
                    html.Div(
                        className="col-md-3 mb-3",
                        children=[
                            html.Label("Contribution Amount:", className="form-label"),
                            dcc.Dropdown(
                                id="amount-filter",
                                options=[
                                    {"label": "£50", "value": 50},
                                    {"label": "£100", "value": 100},
                                    {"label": "£500", "value": 500},
                                    {"label": "£800", "value": 800},
                                ],
                                placeholder="Any amount",
                                multi=True,
                                value=[]
                            ),
                        ]
                    ),
                    
                    # Frequency filter
                    html.Div(
                        className="col-md-3 mb-3",
                        children=[
                            html.Label("Frequency:", className="form-label"),
                            dcc.Dropdown(
                                id="frequency-filter",
                                options=[
                                    {"label": "Weekly", "value": "weekly"},
                                    {"label": "Monthly", "value": "monthly"},
                                ],
                                placeholder="Any frequency",
                                multi=True,
                                value=[]
                            ),
                        ]
                    ),
                    
                    # Available spots filter
                    html.Div(
                        className="col-md-3 mb-3",
                        children=[
                            html.Label("Minimum Available Spots:", className="form-label"),
                            dcc.Dropdown(
                                id="spots-filter",
                                options=[
                                    {"label": "1+ spots", "value": 1},
                                    {"label": "2+ spots", "value": 2},
                                    {"label": "3+ spots", "value": 3},
                                    {"label": "5+ spots", "value": 5},
                                ],
                                placeholder="Any spots",
                                value=None
                            ),
                        ]
                    ),
                    
                    # Results per page
                    html.Div(
                        className="col-md-3 mb-3",
                        children=[
                            html.Label("Groups per page:", className="form-label"),
                            dcc.Dropdown(
                                id="per-page-filter",
                                options=[
                                    {"label": "6", "value": 6},
                                    {"label": "12", "value": 12},
                                    {"label": "24", "value": 24},
                                ],
                                value=12
                            ),
                        ]
                    ),
                ]
            ),
        ]
    )

# Results summary component
def create_results_summary():
    return html.Div(
        id="results-summary",
        className="results-summary mb-3",
        children=[
            html.P("Loading groups...", className="text-muted")
        ]
    )

# Pagination component
def create_pagination():
    return html.Div(
        className="d-flex justify-content-center mt-4",
        children=[
            dbc.Pagination(
                id="discovery-pagination",
                max_value=1,
                first_last=True,
                previous_next=True,
                active_page=1,
                size="md",
            ),
        ]
    )

# Navigation component
def create_navigation():
    return html.Div(
        className="navigation-section mb-4",
        children=[
            dbc.Breadcrumb(
                items=[
                    {"label": "Groups", "href": "/groups"},
                    {"label": "Discover Groups", "active": True},
                ],
            ),
        ]
    )

# Layout for this page
layout = html.Div([
    # Navigation breadcrumb
    create_navigation(),
    
    # Page Header
    create_page_header(),
    
    # Search and Filters
    create_search_and_filters(),
    
    # Results Summary
    create_results_summary(),
    
    # Groups Discovery Section
    create_discovery_section(),
    
    # Pagination
    create_pagination(),
    
    # Hidden div to store current search state
    html.Div(id="discovery-state", style={"display": "none"}),
    
    # Hidden buttons for callback compatibility (shown dynamically in components)
    html.Div([
        dbc.Button(
            "Clear All Filters",
            id="empty-state-clear-btn",
            color="outline-primary",
            n_clicks=0,
            style={"display": "none"}
        ),
        dbc.Button(
            "Try Again",
            id="error-retry-btn",
            color="outline-primary",
            n_clicks=0,
            style={"display": "none"}
        ),
    ], style={"display": "none"}),
]) 