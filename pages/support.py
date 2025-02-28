import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

# Register the page
dash.register_page(__name__, path="/support", title="Support | Ajo", name="Support")

# Page header component
def create_page_header():
    return html.Div(
        className="dashboard-header",
        children=[
            html.H1("Support Center", className="dashboard-title"),
            html.P("Get help with your Ajo account and groups.", className="dashboard-subtitle"),
        ]
    )

# FAQ component
def create_faq_section():
    return html.Div(
        className="mb-5",
        children=[
            html.Div(
                className="section-header",
                children=[
                    html.H2("Frequently Asked Questions", className="section-title"),
                ]
            ),
            html.Div(
                className="faq-container",
                children=[
                    dbc.Accordion(
                        [
                            dbc.AccordionItem(
                                [
                                    html.P("Ajo is a community savings platform that helps you save money with friends, family, or colleagues in a structured and trusted way. It's based on the traditional rotating savings system popular in various cultures."),
                                    html.P("Each member contributes a fixed amount regularly, and one member takes the entire pool on a rotating basis. This continues until all members have received the pool once."),
                                ],
                                title="What is Ajo and how does it work?",
                            ),
                            dbc.AccordionItem(
                                [
                                    html.P("To create a new Ajo group:"),
                                    html.Ol([
                                        html.Li("Click on the '+ New Group' button on your dashboard"),
                                        html.Li("Fill in the group details (name, contribution amount, frequency)"),
                                        html.Li("Invite members via email"),
                                        html.Li("Set the rotation schedule"),
                                        html.Li("Confirm and create the group")
                                    ]),
                                    html.P("Once created, all invited members will receive an invitation to join."),
                                ],
                                title="How do I create a new Ajo group?",
                            ),
                            dbc.AccordionItem(
                                [
                                    html.P("You can contribute to your Ajo groups through several payment methods:"),
                                    html.Ul([
                                        html.Li("Debit/Credit card"),
                                        html.Li("Bank transfer"),
                                        html.Li("Standing order/Direct debit")
                                    ]),
                                    html.P("Set up automatic payments to ensure you never miss a contribution."),
                                ],
                                title="How do I make contributions to my group?",
                            ),
                            dbc.AccordionItem(
                                [
                                    html.P("When it's your turn to receive the pool:"),
                                    html.Ol([
                                        html.Li("You'll receive a notification"),
                                        html.Li("The full amount will be transferred to your linked bank account within 1-2 business days"),
                                        html.Li("You can track the payment in your transaction history")
                                    ]),
                                ],
                                title="How do I receive my payout?",
                            ),
                            dbc.AccordionItem(
                                [
                                    html.P("We take security seriously. Your money and data are protected by:"),
                                    html.Ul([
                                        html.Li("Bank-level encryption"),
                                        html.Li("Secure payment processing"),
                                        html.Li("Identity verification for all members"),
                                        html.Li("Member reputation system"),
                                        html.Li("Escrow protection for contributions")
                                    ]),
                                ],
                                title="Is my money safe on the platform?",
                            ),
                        ],
                        start_collapsed=True,
                        id="faq-accordion",
                    )
                ]
            )
        ]
    )

# Contact form component
def create_contact_form():
    return html.Div(
        className="mb-5",
        children=[
            html.Div(
                className="section-header",
                children=[
                    html.H2("Contact Support", className="section-title"),
                ]
            ),
            dbc.Card(
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Div(
                                className="mb-4",
                                children=[
                                    html.Label("Topic", className="form-label"),
                                    dbc.Select(
                                        options=[
                                            {"label": "Account Issues", "value": "account"},
                                            {"label": "Payment Problems", "value": "payment"},
                                            {"label": "Group Management", "value": "group"},
                                            {"label": "Technical Support", "value": "tech"},
                                            {"label": "Other", "value": "other"},
                                        ],
                                        id="support-topic",
                                    ),
                                ]
                            ),
                            html.Div(
                                className="mb-4",
                                children=[
                                    html.Label("Subject", className="form-label"),
                                    dbc.Input(type="text", placeholder="Brief description of your issue"),
                                ]
                            ),
                            html.Div(
                                className="mb-4",
                                children=[
                                    html.Label("Message", className="form-label"),
                                    dbc.Textarea(
                                        placeholder="Please provide details about your issue or question...",
                                        style={"height": "150px"},
                                    ),
                                ]
                            ),
                            html.Div(
                                className="mb-3",
                                children=[
                                    dbc.Checkbox(
                                        id="attach-screenshots",
                                        label="Attach screenshots or documents",
                                        value=False,
                                    ),
                                ]
                            ),
                            dbc.Button("Submit", color="primary"),
                        ], width=8),
                        dbc.Col([
                            html.Div(
                                className="contact-info p-4 bg-light rounded",
                                children=[
                                    html.H4("Other Ways to Reach Us", className="mb-3"),
                                    html.Div([
                                        html.I(className="fas fa-envelope me-2"),
                                        html.Span("Email: support@ajo-platform.com")
                                    ], className="mb-3"),
                                    html.Div([
                                        html.I(className="fas fa-phone me-2"),
                                        html.Span("Phone: +44 123 456 7890")
                                    ], className="mb-3"),
                                    html.Div([
                                        html.I(className="fas fa-clock me-2"),
                                        html.Span("Hours: 9am-5pm, Monday-Friday")
                                    ], className="mb-3"),
                                    html.Hr(),
                                    html.P("Typical response time: 1-2 business days", className="mb-0 small"),
                                ]
                            )
                        ], width=4),
                    ]),
                ]),
                className="shadow-sm",
            ),
        ]
    )

# Layout for this page
layout = html.Div([
    # Page Header
    create_page_header(),
    
    # FAQ Section
    create_faq_section(),
    
    # Contact Form Section
    create_contact_form(),
])