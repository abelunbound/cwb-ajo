from dash import html

def create_footer():
    return html.Footer(
        className="footer mt-5 py-4",
        children=[
            html.Div(
                className="container",
                children=[
                    html.Div(
                        className="row",
                        children=[
                            html.Div(
                                className="col-md-6",
                                children=[
                                    html.Div("© 2025 Ajo - Community Savings Platform. All rights reserved.")
                                ]
                            ),
                            html.Div(
                                className="col-md-6 text-md-end",
                                children=[
                                    html.A("Privacy Policy", href="#", className="me-3"),
                                    html.A("Terms of Service", href="#", className="me-3"),
                                    html.A("Contact Us", href="#")
                                ]
                            )
                        ]
                    )
                ]
            )
        ]
    )