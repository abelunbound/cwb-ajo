import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from components.groups import create_groups_section
from components.modals import create_group_modal, create_success_modal

# Register the page
dash.register_page(__name__, path="/groups", title="My Groups | Ajo", name="My Groups")

# Page header component
def create_page_header():
    return html.Div(
        className="dashboard-header",
        children=[
            html.H1("My Ajo Groups", className="dashboard-title"),
            html.P("View and manage all your Ajo groups.", className="dashboard-subtitle"),
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

# Layout for this page
layout = html.Div([
    # Page Header
    create_page_header(),
    
    # Groups Filter
    create_groups_filter(),
    
    # Groups Section (reused from components)
    create_groups_section(),
    
    # Modals
    create_group_modal(),
    create_success_modal(),
])