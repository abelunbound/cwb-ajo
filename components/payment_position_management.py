"""
Payment Position Management Components

This module provides UI components for managing payment positions in Ajo groups,
including position assignment interfaces and payment schedule displays.

Task 31: Implement Payment Position Assignment
"""

import dash
from dash import html, dcc
import dash_bootstrap_components as dbc


def create_payment_position_modal():
    """Create modal for managing payment positions."""
    return dbc.Modal(
        [
            dbc.ModalHeader(
                html.H5("Manage Payment Positions", className="modal-title")
            ),
            dbc.ModalBody(
                [
                    # Group info section
                    html.Div(
                        id="payment-position-group-info",
                        className="mb-3 p-3 bg-light rounded",
                        children=[
                            html.H6("Group: Loading...", id="payment-position-group-name"),
                            html.P("Loading group details...", id="payment-position-group-details", className="text-muted mb-0")
                        ]
                    ),
                    
                    # Position assignment options
                    html.Div(
                        className="mb-4",
                        children=[
                            html.H6("Assignment Options", className="mb-3"),
                            dbc.ButtonGroup(
                                [
                                    dbc.Button(
                                        [html.I(className="fas fa-random me-2"), "Random Assignment"],
                                        id="payment-position-random-btn",
                                        color="primary",
                                        size="sm"
                                    ),
                                    dbc.Button(
                                        [html.I(className="fas fa-magic me-2"), "Auto-Assign Missing"],
                                        id="payment-position-auto-btn",
                                        color="success",
                                        size="sm"
                                    ),
                                    dbc.Button(
                                        [html.I(className="fas fa-check me-2"), "Validate Positions"],
                                        id="payment-position-validate-btn",
                                        color="info",
                                        size="sm"
                                    )
                                ]
                            )
                        ]
                    ),
                    
                    # Current positions display
                    html.Div(
                        className="mb-4",
                        children=[
                            html.H6("Current Payment Positions", className="mb-2"),
                            html.Div(id="payment-position-list", children=[
                                dbc.Spinner(color="primary", size="sm")
                            ])
                        ]
                    ),
                    
                    # Position swapping section
                    html.Div(
                        className="mb-3",
                        children=[
                            html.H6("Swap Positions", className="mb-2"),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("First Member"),
                                    dcc.Dropdown(
                                        id="payment-position-swap-member1",
                                        placeholder="Select first member..."
                                    )
                                ], width=5),
                                dbc.Col([
                                    dbc.Label("Second Member"),
                                    dcc.Dropdown(
                                        id="payment-position-swap-member2",
                                        placeholder="Select second member..."
                                    )
                                ], width=5),
                                dbc.Col([
                                    dbc.Label("Action"),
                                    dbc.Button(
                                        "Swap",
                                        id="payment-position-swap-btn",
                                        color="warning",
                                        size="sm",
                                        className="w-100"
                                    )
                                ], width=2)
                            ])
                        ]
                    ),
                    
                    # Alerts/feedback
                    html.Div(id="payment-position-alert", className="mt-3")
                ]
            ),
            dbc.ModalFooter([
                dbc.Button(
                    "View Payment Schedule",
                    id="payment-position-schedule-btn",
                    color="info",
                    className="me-2"
                ),
                dbc.Button(
                    "Close",
                    id="payment-position-modal-close",
                    color="secondary"
                )
            ])
        ],
        id="payment-position-modal",
        is_open=False,
        size="xl",
        backdrop="static",
        keyboard=False
    )


def create_payment_position_card(member_data, position):
    """Create a card for displaying member payment position.
    
    Args:
        member_data (dict): Member information
        position (int): Payment position number
        
    Returns:
        dbc.Card: Payment position card
    """
    # Position badge color based on position
    if position == 1:
        position_color = "success"
        position_text = "Next"
    elif position <= 3:
        position_color = "warning"
        position_text = "Soon"
    else:
        position_color = "secondary"
        position_text = "Later"
    
    # Role badge
    role_color = "primary" if member_data.get('role') == 'admin' else "secondary"
    
    return dbc.Card(
        [
            dbc.CardBody(
                [
                    html.Div(
                        className="d-flex justify-content-between align-items-start",
                        children=[
                            html.Div([
                                html.H6(
                                    member_data.get('full_name', 'Unknown'),
                                    className="card-title mb-1"
                                ),
                                html.Small(
                                    member_data.get('email', ''),
                                    className="text-muted"
                                )
                            ]),
                            html.Div([
                                dbc.Badge(
                                    f"Position #{position}",
                                    color=position_color,
                                    className="me-2"
                                ),
                                dbc.Badge(
                                    position_text,
                                    color=position_color,
                                    pill=True
                                )
                            ])
                        ]
                    ),
                    
                    html.Hr(className="my-2"),
                    
                    html.Div(
                        className="d-flex justify-content-between align-items-center",
                        children=[
                            html.Div([
                                dbc.Badge(
                                    member_data.get('role', 'member').title(),
                                    color=role_color,
                                    className="me-2"
                                ),
                                html.Small(
                                    f"Joined: {member_data.get('join_date', 'Unknown')}",
                                    className="text-muted"
                                )
                            ]),
                            html.Div([
                                dbc.Button(
                                    [html.I(className="fas fa-arrow-up"), ""],
                                    id={"type": "position-up-btn", "user_id": member_data.get('user_id')},
                                    color="outline-success",
                                    size="sm",
                                    className="me-1",
                                    disabled=position == 1
                                ),
                                dbc.Button(
                                    [html.I(className="fas fa-arrow-down"), ""],
                                    id={"type": "position-down-btn", "user_id": member_data.get('user_id')},
                                    color="outline-danger",
                                    size="sm",
                                    disabled=False  # Will be set based on if it's the last position
                                )
                            ])
                        ]
                    )
                ]
            )
        ],
        className="mb-2"
    )


def create_payment_position_list(members_data):
    """Create a list of payment position cards.
    
    Args:
        members_data (list): List of member dictionaries with positions
        
    Returns:
        html.Div: Container with position cards
    """
    if not members_data:
        return html.Div(
            [
                html.I(className="fas fa-list-ol fa-2x text-muted mb-2"),
                html.P("No payment positions assigned", className="text-muted")
            ],
            className="text-center py-4"
        )
    
    # Sort by payment position (handle None values)
    sorted_members = sorted(members_data, key=lambda x: x.get('payment_position') or 999)
    
    position_cards = []
    for member in sorted_members:
        position = member.get('payment_position')
        if position:
            position_cards.append(create_payment_position_card(member, position))
    
    return html.Div(
        position_cards,
        className="position-list-container",
        style={"maxHeight": "400px", "overflowY": "auto"}
    )


def create_payment_schedule_modal():
    """Create modal for displaying payment schedule."""
    return dbc.Modal(
        [
            dbc.ModalHeader(
                html.H5("Payment Schedule", className="modal-title")
            ),
            dbc.ModalBody(
                [
                    # Group info
                    html.Div(
                        id="payment-schedule-group-info",
                        className="mb-4"
                    ),
                    
                    # Next recipient highlight
                    html.Div(
                        id="payment-schedule-next-recipient",
                        className="mb-4"
                    ),
                    
                    # Full schedule
                    html.Div(
                        className="mb-3",
                        children=[
                            html.H6("Complete Payment Order", className="mb-3"),
                            html.Div(id="payment-schedule-list", children=[
                                dbc.Spinner(color="primary", size="sm")
                            ])
                        ]
                    )
                ]
            ),
            dbc.ModalFooter([
                dbc.Button(
                    "Close",
                    id="payment-schedule-modal-close",
                    color="secondary"
                )
            ])
        ],
        id="payment-schedule-modal",
        is_open=False,
        size="lg",
        backdrop="static"
    )


def create_payment_schedule_card(member_data, is_next=False):
    """Create a card for payment schedule display.
    
    Args:
        member_data (dict): Member information with position
        is_next (bool): Whether this member is next to receive payment
        
    Returns:
        dbc.Card: Schedule card
    """
    position = member_data.get('position', 0)
    
    # Card styling based on position
    if is_next:
        card_color = "success"
        card_outline = True
        badge_color = "success"
        badge_text = "Next Recipient"
    elif position <= 3:
        card_color = "light"
        card_outline = False
        badge_color = "warning"
        badge_text = "Coming Soon"
    else:
        card_color = "light"
        card_outline = False
        badge_color = "secondary"
        badge_text = "In Queue"
    
    return dbc.Card(
        [
            dbc.CardBody(
                [
                    html.Div(
                        className="d-flex justify-content-between align-items-center",
                        children=[
                            html.Div([
                                html.H6(
                                    f"{position}. {member_data.get('full_name', 'Unknown')}",
                                    className="mb-1"
                                ),
                                html.Small(
                                    f"Role: {member_data.get('role', 'member').title()}",
                                    className="text-muted"
                                )
                            ]),
                            dbc.Badge(
                                badge_text,
                                color=badge_color,
                                pill=True
                            )
                        ]
                    )
                ]
            )
        ],
        color=card_color,
        outline=card_outline,
        className="mb-2"
    )


def create_payment_schedule_list(schedule_data):
    """Create payment schedule list from schedule data.
    
    Args:
        schedule_data (list): List of members with positions
        
    Returns:
        html.Div: Schedule list container
    """
    if not schedule_data:
        return html.Div(
            [
                html.I(className="fas fa-calendar-alt fa-2x text-muted mb-2"),
                html.P("No payment schedule available", className="text-muted")
            ],
            className="text-center py-4"
        )
    
    schedule_cards = []
    for member in schedule_data:
        is_next = member.get('is_next', False)
        schedule_cards.append(create_payment_schedule_card(member, is_next))
    
    return html.Div(
        schedule_cards,
        className="schedule-list-container",
        style={"maxHeight": "500px", "overflowY": "auto"}
    )


def create_next_recipient_highlight(next_recipient):
    """Create highlighted card for next payment recipient.
    
    Args:
        next_recipient (dict): Next recipient member data
        
    Returns:
        dbc.Card: Highlighted recipient card
    """
    if not next_recipient:
        return dbc.Alert(
            "No payment recipient assigned yet.",
            color="warning",
            className="text-center"
        )
    
    return dbc.Card(
        [
            dbc.CardBody(
                [
                    html.Div(
                        className="text-center",
                        children=[
                            html.I(className="fas fa-trophy fa-2x text-success mb-2"),
                            html.H5(
                                "Next Payment Recipient",
                                className="text-success mb-2"
                            ),
                            html.H4(
                                next_recipient.get('full_name', 'Unknown'),
                                className="mb-1"
                            ),
                            html.P(
                                f"Position #{next_recipient.get('position', 1)}",
                                className="text-muted mb-0"
                            )
                        ]
                    )
                ]
            )
        ],
        color="success",
        outline=True,
        className="text-center"
    )


def create_group_info_for_positions(group_data):
    """Create group information card for position management.
    
    Args:
        group_data (dict): Group information
        
    Returns:
        dbc.Card: Group info card
    """
    return dbc.Card(
        [
            dbc.CardBody(
                [
                    html.Div(
                        className="d-flex justify-content-between align-items-start",
                        children=[
                            html.Div([
                                html.H6(
                                    group_data.get('group_name', 'Unknown Group'),
                                    className="mb-1"
                                ),
                                html.P(
                                    f"Contribution: £{group_data.get('contribution_amount', 0)} {group_data.get('frequency', 'monthly')}",
                                    className="text-muted mb-0"
                                )
                            ]),
                            html.Div([
                                dbc.Badge(
                                    f"{group_data.get('current_members', 0)} members",
                                    color="info",
                                    className="me-2"
                                ),
                                dbc.Badge(
                                    group_data.get('group_status', 'unknown').title(),
                                    color="success" if group_data.get('group_status') == 'active' else "secondary"
                                )
                            ])
                        ]
                    )
                ]
            )
        ],
        color="light",
        className="mb-3"
    ) 