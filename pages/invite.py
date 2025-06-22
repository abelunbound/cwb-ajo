"""
Task 29: Group Invitation Acceptance Page
This page handles invitation acceptance/decline functionality.
"""

import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
from functions.database import get_invitation_by_code, update_invitation_status, add_user_to_group

# Register the page with variable path for invitation codes
dash.register_page(__name__, path_template="/invite/<invitation_code>", title="Group Invitation | Ajo")

def layout(invitation_code=None, **kwargs):
    """Layout for the invitation acceptance page.
    
    Args:
        invitation_code (str): The invitation code from the URL
    """
    if not invitation_code:
        return create_invalid_invitation_layout("No invitation code provided")
    
    return html.Div([
        # Store the invitation code for callbacks
        dcc.Store(id="invitation-code-store", data=invitation_code),
        
        # Main content container
        html.Div(
            className="container mt-5",
            children=[
                html.Div(
                    className="row justify-content-center",
                    children=[
                        html.Div(
                            className="col-md-8 col-lg-6",
                            children=[
                                # Loading state (initial)
                                html.Div(
                                    id="invitation-content",
                                    children=[
                                        dbc.Card([
                                            dbc.CardBody([
                                                html.Div(
                                                    className="text-center py-4",
                                                    children=[
                                                        dbc.Spinner(color="primary", size="lg"),
                                                        html.P("Loading invitation...", className="mt-3 text-muted")
                                                    ]
                                                )
                                            ])
                                        ])
                                    ]
                                )
                            ]
                        )
                    ]
                )
            ]
        )
    ])

def create_invalid_invitation_layout(message):
    """Create layout for invalid/expired invitations."""
    return html.Div(
        className="container mt-5",
        children=[
            html.Div(
                className="row justify-content-center",
                children=[
                    html.Div(
                        className="col-md-6",
                        children=[
                            dbc.Card([
                                dbc.CardBody([
                                    html.Div(
                                        className="text-center py-4",
                                        children=[
                                            html.I(className="fas fa-exclamation-triangle fa-3x text-warning mb-3"),
                                            html.H4("Invalid Invitation", className="text-warning"),
                                            html.P(message, className="text-muted mb-4"),
                                            dbc.Button(
                                                "Go to Homepage",
                                                href="/",
                                                color="primary"
                                            )
                                        ]
                                    )
                                ])
                            ])
                        ]
                    )
                ]
            )
        ]
    )

def create_valid_invitation_layout(invitation_data):
    """Create layout for valid invitations."""
    return dbc.Card([
        dbc.CardHeader([
            html.H4([
                html.I(className="fas fa-envelope me-2 text-primary"),
                "You're Invited to Join an Ajo Group!"
            ], className="mb-0")
        ]),
        dbc.CardBody([
            # Group information
            html.Div(
                className="group-invitation-info mb-4",
                children=[
                    html.H5(invitation_data['group_name'], className="text-primary mb-3"),
                    html.P(invitation_data.get('group_description', 'No description available'), 
                          className="text-muted mb-3"),
                    
                    # Group details grid
                    html.Div(
                        className="row",
                        children=[
                            html.Div(
                                className="col-6 mb-3",
                                children=[
                                    html.Small("Contribution Amount", className="text-muted"),
                                    html.H6(f"£{invitation_data['contribution_amount']}", className="mb-0")
                                ]
                            ),
                            html.Div(
                                className="col-6 mb-3",
                                children=[
                                    html.Small("Frequency", className="text-muted"),
                                    html.H6(invitation_data['frequency'].capitalize(), className="mb-0")
                                ]
                            ),
                            html.Div(
                                className="col-6 mb-3",
                                children=[
                                    html.Small("Duration", className="text-muted"),
                                    html.H6(f"{invitation_data['duration_months']} months", className="mb-0")
                                ]
                            ),
                            html.Div(
                                className="col-6 mb-3",
                                children=[
                                    html.Small("Available Spots", className="text-muted"),
                                    html.H6(f"{invitation_data['max_members'] - invitation_data['current_members']} remaining", 
                                           className="mb-0")
                                ]
                            )
                        ]
                    )
                ]
            ),
            
            # Action buttons
            html.Div(
                className="d-grid gap-2 d-md-flex justify-content-md-center",
                children=[
                    dbc.Button(
                        [html.I(className="fas fa-check me-2"), "Accept Invitation"],
                        id="accept-invitation-btn",
                        color="success",
                        size="lg",
                        className="me-md-2"
                    ),
                    dbc.Button(
                        [html.I(className="fas fa-times me-2"), "Decline"],
                        id="decline-invitation-btn",
                        color="outline-secondary",
                        size="lg"
                    )
                ]
            ),
            
            # Status/feedback area
            html.Div(id="invitation-action-feedback", className="mt-3")
        ])
    ])

def create_expired_invitation_layout():
    """Create layout for expired invitations."""
    return dbc.Card([
        dbc.CardBody([
            html.Div(
                className="text-center py-4",
                children=[
                    html.I(className="fas fa-clock fa-3x text-warning mb-3"),
                    html.H4("Invitation Expired", className="text-warning"),
                    html.P("This invitation has expired and is no longer valid.", className="text-muted mb-4"),
                    html.P("Please contact the group admin for a new invitation.", className="text-muted mb-4"),
                    dbc.Button(
                        "Go to Homepage",
                        href="/",
                        color="primary"
                    )
                ]
            )
        ])
    ])

def create_already_responded_layout(status):
    """Create layout for invitations already responded to."""
    if status == 'accepted':
        icon = "fas fa-check-circle"
        color = "success"
        title = "Invitation Already Accepted"
        message = "You have already accepted this invitation and joined the group."
    else:  # declined
        icon = "fas fa-times-circle"
        color = "danger"
        title = "Invitation Declined"
        message = "You have declined this invitation."
    
    return dbc.Card([
        dbc.CardBody([
            html.Div(
                className="text-center py-4",
                children=[
                    html.I(className=f"{icon} fa-3x text-{color} mb-3"),
                    html.H4(title, className=f"text-{color}"),
                    html.P(message, className="text-muted mb-4"),
                    dbc.Button(
                        "Go to Homepage",
                        href="/",
                        color="primary"
                    )
                ]
            )
        ])
    ]) 