import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

# Register the page
dash.register_page(__name__, path="/payments", title="Payments | Ajo", name="Payments")

# Page header component
def create_page_header():
    return html.Div(
        className="dashboard-header",
        children=[
            html.H1("Payments & Transactions", className="dashboard-title"),
            html.P("Manage your contributions and track all your Ajo transactions.", className="dashboard-subtitle"),
        ]
    )

# Upcoming payments component
def create_upcoming_payments():
    return html.Div(
        className="mb-5",
        children=[
            html.Div(
                className="section-header",
                children=[
                    html.H2("Upcoming Payments", className="section-title"),
                ]
            ),
            html.Div(
                className="row",
                children=[
                    # Upcoming payment card 1
                    html.Div(
                        className="col-lg-4 col-md-6 mb-4",
                        children=[
                            html.Div(
                                className="card",
                                children=[
                                    html.Div(
                                        className="card-header d-flex justify-content-between align-items-center",
                                        children=[
                                            html.H3("Ogo Ajo ", className="mb-0"),
                                            html.Span("Due in 3 days", className="badge bg-warning text-dark"),
                                        ]
                                    ),
                                    html.Div(
                                        className="card-body",
                                        children=[
                                            html.Div(
                                                className="payment-details",
                                                children=[
                                                    html.Div(
                                                        className="detail-item",
                                                        children=[
                                                            html.Div("Amount Due", className="detail-label"),
                                                            html.Div("£750", className="detail-value"),
                                                        ]
                                                    ),
                                                    html.Div(
                                                        className="detail-item",
                                                        children=[
                                                            html.Div("Due Date", className="detail-label"),
                                                            html.Div("03 March 2025", className="detail-value"),
                                                        ]
                                                    ),
                                                ]
                                            ),
                                            dbc.Button("Pay Now", color="primary", className="w-100 mt-3"),
                                        ]
                                    ),
                                ]
                            )
                        ]
                    ),
                    # Upcoming payment card 2
                    html.Div(
                        className="col-lg-4 col-md-6 mb-4",
                        children=[
                            html.Div(
                                className="card",
                                children=[
                                    html.Div(
                                        className="card-header d-flex justify-content-between align-items-center",
                                        children=[
                                            html.H3("Scotland Ajo", className="mb-0"),
                                            html.Span("Due in 12 days", className="badge bg-info text-white"),
                                        ]
                                    ),
                                    html.Div(
                                        className="card-body",
                                        children=[
                                            html.Div(
                                                className="payment-details",
                                                children=[
                                                    html.Div(
                                                        className="detail-item",
                                                        children=[
                                                            html.Div("Amount Due", className="detail-label"),
                                                            html.Div("£500", className="detail-value"),
                                                        ]
                                                    ),
                                                    html.Div(
                                                        className="detail-item",
                                                        children=[
                                                            html.Div("Due Date", className="detail-label"),
                                                            html.Div("12 March 2025", className="detail-value"),
                                                        ]
                                                    ),
                                                ]
                                            ),
                                            dbc.Button("Pay Now", color="primary", className="w-100 mt-3"),
                                        ]
                                    ),
                                ]
                            )
                        ]
                    ),
                ]
            ),
        ]
    )

# Transaction history component
def create_transaction_history():
    return html.Div(
        className="mb-5",
        children=[
            html.Div(
                className="section-header d-flex justify-content-between align-items-center",
                children=[
                    html.H2("Transaction History", className="section-title"),
                    dbc.ButtonGroup(
                        [
                            dbc.Button("All", color="primary", outline=True, active=True),
                            dbc.Button("Payments", color="primary", outline=True),
                            dbc.Button("Payouts", color="primary", outline=True),
                        ],
                        size="sm",
                    ),
                ]
            ),
            html.Div(
                className="transaction-list card",
                children=[
                    html.Div(
                        className="transaction-list-header bg-light p-3",
                        children=[
                            html.Div(
                                className="row",
                                children=[
                                    html.Div("Date", className="col-md-2 fw-bold"),
                                    html.Div("Description", className="col-md-4 fw-bold"),
                                    html.Div("Group", className="col-md-2 fw-bold"),
                                    html.Div("Amount", className="col-md-2 fw-bold"),
                                    html.Div("Status", className="col-md-2 fw-bold"),
                                ]
                            ),
                        ]
                    ),
                    html.Div(
                        className="transaction-item p-3 border-bottom",
                        children=[
                            html.Div(
                                className="row align-items-center",
                                children=[
                                    html.Div("28 Feb 2025", className="col-md-2"),
                                    html.Div("Monthly Contribution", className="col-md-4"),
                                    html.Div("Ogo Ajo Savings", className="col-md-2"),
                                    html.Div("- £750", className="col-md-2 text-danger"),
                                    html.Div(html.Span("Completed", className="badge bg-success"), className="col-md-2"),
                                ]
                            ),
                        ]
                    ),
                    html.Div(
                        className="transaction-item p-3 border-bottom",
                        children=[
                            html.Div(
                                className="row align-items-center",
                                children=[
                                    html.Div("15 Feb 2025", className="col-md-2"),
                                    html.Div("Payout Received", className="col-md-4"),
                                    html.Div("Yettie Ajo", className="col-md-2"),
                                    html.Div("+ £1,500", className="col-md-2 text-success"),
                                    html.Div(html.Span("Completed", className="badge bg-success"), className="col-md-2"),
                                ]
                            ),
                        ]
                    ),
                    html.Div(
                        className="transaction-item p-3 border-bottom",
                        children=[
                            html.Div(
                                className="row align-items-center",
                                children=[
                                    html.Div("31 Jan 2025", className="col-md-2"),
                                    html.Div("Monthly Contribution", className="col-md-4"),
                                    html.Div("Scotland Ajo", className="col-md-2"),
                                    html.Div("- £500", className="col-md-2 text-danger"),
                                    html.Div(html.Span("Completed", className="badge bg-success"), className="col-md-2"),
                                ]
                            ),
                        ]
                    ),
                    html.Div(
                        className="transaction-item p-3",
                        children=[
                            html.Div(
                                className="row align-items-center",
                                children=[
                                    html.Div("15 Jan 2025", className="col-md-2"),
                                    html.Div("Monthly Contribution", className="col-md-4"),
                                    html.Div("Yettie Ajo", className="col-md-2"),
                                    html.Div("- £250", className="col-md-2 text-danger"),
                                    html.Div(html.Span("Completed", className="badge bg-success"), className="col-md-2"),
                                ]
                            ),
                        ]
                    ),
                ]
            ),
            html.Div(
                className="d-flex justify-content-center mt-4",
                children=[
                    dbc.Pagination(
                        max_value=5,
                        fully_expanded=False,
                        first_last=True,
                        previous_next=True,
                        active_page=1,
                    ),
                ]
            ),
        ]
    )

# Layout for this page
layout = html.Div([
    # Page Header
    create_page_header(),
    
    # Upcoming Payments Section
    create_upcoming_payments(),
    
    # Transaction History Section
    create_transaction_history(),
])