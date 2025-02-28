from dash import html
import dash_bootstrap_components as dbc

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
                            html.A("CWB", className="logo", href="/"),
                            html.Nav(
                                className="d-none d-md-block",
                                children=[
                                    html.Ul(
                                        className="nav",
                                        children=[
                                            html.Li(html.A("Dashboard", href="/", className="nav-link active")),
                                            html.Li(html.A("My Groups", href="/groups", className="nav-link")),
                                            html.Li(html.A("Payments", href="/payments", className="nav-link")),
                                            html.Li(html.A("Support", href="/support", className="nav-link")),
                                        ]
                                    )
                                ]
                            ),
                            html.Div(
                                className="d-flex",
                                children=[
                                    dbc.Button("Profile", color="", className="btn-outline-primary me-2", href="/profile"),
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