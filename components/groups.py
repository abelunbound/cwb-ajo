from dash import html
import dash_bootstrap_components as dbc

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