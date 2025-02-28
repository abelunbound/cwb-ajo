from dash import html

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