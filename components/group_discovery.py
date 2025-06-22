"""
Group Discovery Component for Ajo Platform

This module provides UI components for group discovery including:
- Group cards with discovery information
- Request to join functionality
- Group details display
- Loading states and error handling

Task 28: Build Group Discovery Interface
"""

import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from datetime import datetime, date
from typing import List, Dict, Any, Optional


def create_group_discovery_card(group: Dict[str, Any]) -> dbc.Card:
    """Create a discovery card for a group.
    
    Args:
        group (dict): Group information dictionary
        
    Returns:
        dbc.Card: Bootstrap card component for the group
    """
    # Format contribution amount
    amount_text = f"£{group['contribution_amount']}"
    
    # Format frequency
    frequency_text = group['frequency'].capitalize()
    
    # Calculate spots available
    spots_available = group.get('spots_available', 0)
    is_full = group.get('is_full', False)
    
    # Format dates
    start_date_str = ""
    if group.get('start_date'):
        if isinstance(group['start_date'], str):
            start_date_str = group['start_date']
        else:
            start_date_str = group['start_date'].strftime('%d %b %Y')
    
    # Status badge
    status_badge = dbc.Badge(
        "Full" if is_full else f"{spots_available} spots left",
        color="danger" if is_full else "success",
        className="mb-2"
    )
    
    # Create buttons - always show View Details, conditionally show Join
    view_details_button = dbc.Button(
        "View Details",
        id={"type": "view-details-btn", "index": group['id']},
        color="outline-primary",
        size="sm",
        className="w-100 mb-2"
    )
    
    # Join button - always show but disable for full groups
    join_button = dbc.Button(
        "Request to Join" if not is_full else "Group Full",
        id={"type": "join-group-btn", "index": group['id']},
        color="primary" if not is_full else "secondary",
        size="sm",
        className="w-100",
        disabled=is_full
    )
    
    # Create button container - always include both buttons
    button_container = [view_details_button, join_button]
    
    card_body = dbc.CardBody([
        html.Div([
            html.H5(group['name'], className="card-title mb-2"),
            status_badge,
        ]),
        
        html.P(
            group.get('description', 'No description available'),
            className="card-text text-muted small",
            style={"height": "60px", "overflow": "hidden"}
        ),
        
        html.Hr(),
        
        # Group details
        html.Div([
            html.Div([
                html.I(className="fas fa-pound-sign me-2 text-primary"),
                html.Span(f"{amount_text} {frequency_text.lower()}", className="small")
            ], className="mb-2"),
            
            html.Div([
                html.I(className="fas fa-users me-2 text-primary"),
                html.Span(f"{group['current_members']}/{group['max_members']} members", className="small")
            ], className="mb-2"),
            
            html.Div([
                html.I(className="fas fa-calendar me-2 text-primary"),
                html.Span(f"{group['duration_months']} months", className="small")
            ], className="mb-2"),
            
            html.Div([
                html.I(className="fas fa-user me-2 text-primary"),
                html.Span(f"Created by {group.get('creator_name', 'Unknown')}", className="small")
            ], className="mb-3"),
        ]),
        
        # Button container
        html.Div(button_container),
    ])
    
    return dbc.Card(
        card_body,
        className="h-100 shadow-sm group-discovery-card",
        style={"transition": "transform 0.2s"}
    )


def create_empty_state() -> html.Div:
    """Create empty state when no groups are found.
    
    Returns:
        html.Div: Empty state component
    """
    return html.Div(
        className="text-center py-5",
        children=[
            html.I(className="fas fa-search fa-3x text-muted mb-3"),
            html.H4("No Groups Found", className="text-muted"),
            html.P(
                "Try adjusting your search criteria or filters to find more groups.",
                className="text-muted"
            ),
            dbc.Button(
                "Clear All Filters",
                id="empty-state-clear-btn",
                color="outline-primary",
                n_clicks=0
            ),
        ]
    )


def create_loading_state() -> html.Div:
    """Create loading state for group discovery.
    
    Returns:
        html.Div: Loading state component
    """
    return html.Div(
        className="text-center py-5",
        children=[
            dbc.Spinner(color="primary", size="lg"),
            html.P("Loading groups...", className="text-muted mt-3"),
        ]
    )


def create_error_state(error_message: str = "Failed to load groups") -> html.Div:
    """Create error state for group discovery.
    
    Args:
        error_message (str): Error message to display
        
    Returns:
        html.Div: Error state component
    """
    return html.Div(
        className="text-center py-5",
        children=[
            html.I(className="fas fa-exclamation-triangle fa-3x text-warning mb-3"),
            html.H4("Oops! Something went wrong", className="text-muted"),
            html.P(error_message, className="text-muted"),
            dbc.Button(
                "Try Again",
                id="error-retry-btn",
                color="outline-primary",
                n_clicks=0
            ),
        ]
    )


def create_discovery_section() -> html.Div:
    """Create the main discovery section container with modals.
    
    Returns:
        html.Div: Discovery section container with modals
    """
    return html.Div([
        html.Div(
            id="discovery-content",
            className="discovery-content",
            children=[
                create_loading_state()
            ]
        ),
        
        # Modals
        create_group_detail_modal(),
        create_join_request_modal(),
    ])


def create_group_grid(groups: List[Dict[str, Any]]) -> html.Div:
    """Create a grid of group discovery cards.
    
    Args:
        groups (list): List of group dictionaries
        
    Returns:
        html.Div: Grid container with group cards
    """
    if not groups:
        return create_empty_state()
    
    # Create rows of cards (3 cards per row on desktop, responsive)
    cards = []
    for group in groups:
        card_col = html.Div(
            className="col-lg-4 col-md-6 mb-4",
            children=[create_group_discovery_card(group)]
        )
        cards.append(card_col)
    
    return html.Div(
        className="row",
        children=cards
    )


def create_group_detail_modal() -> dbc.Modal:
    """Create modal for displaying detailed group information.
    
    Returns:
        dbc.Modal: Group detail modal component
    """
    return dbc.Modal(
        [
            dbc.ModalHeader(
                dbc.ModalTitle(id="group-detail-modal-title"),
                close_button=True,
            ),
            dbc.ModalBody(
                id="group-detail-modal-body",
                children=[
                    html.P("Loading group details...", className="text-center text-muted")
                ]
            ),
            dbc.ModalFooter([
                dbc.Button(
                    "Close",
                    id="group-detail-modal-close",
                    color="secondary"
                ),
                dbc.Button(
                    "Request to Join",
                    id="group-detail-join-btn",
                    color="primary",
                    style={"display": "none"}
                ),
            ]),
        ],
        id="group-detail-modal",
        size="lg",
        is_open=False,
    )


def create_group_detail_content(group: Dict[str, Any]) -> html.Div:
    """Create detailed content for group modal.
    
    Args:
        group (dict): Detailed group information
        
    Returns:
        html.Div: Group detail content
    """
    # Format dates
    start_date_str = "Not set"
    if group.get('start_date'):
        if isinstance(group['start_date'], str):
            start_date_str = group['start_date']
        else:
            start_date_str = group['start_date'].strftime('%d %B %Y')
    
    end_date_str = "Not set"
    if group.get('end_date'):
        if isinstance(group['end_date'], str):
            end_date_str = group['end_date']
        else:
            end_date_str = group['end_date'].strftime('%d %B %Y')
    
    # Member list
    members_content = []
    if group.get('members'):
        for i, member in enumerate(group['members'], 1):
            role_badge = dbc.Badge(
                member['role'].capitalize(),
                color="primary" if member['role'] == 'admin' else "secondary",
                className="me-2"
            )
            members_content.append(
                html.Li([
                    f"Position {member['payment_position']}: {member['name']} ",
                    role_badge
                ], className="mb-1")
            )
    else:
        members_content = [html.Li("No members yet", className="text-muted")]
    
    return html.Div([
        # Group description
        html.Div([
            html.H6("Description", className="fw-bold"),
            html.P(group.get('description', 'No description provided'), className="text-muted"),
        ], className="mb-4"),
        
        # Group details in two columns
        html.Div([
            html.Div([
                html.H6("Group Details", className="fw-bold mb-3"),
                
                html.Div([
                    html.Strong("Contribution: "),
                    f"£{group['contribution_amount']} {group['frequency']}"
                ], className="mb-2"),
                
                html.Div([
                    html.Strong("Duration: "),
                    f"{group['duration_months']} months"
                ], className="mb-2"),
                
                html.Div([
                    html.Strong("Members: "),
                    f"{group['current_members']}/{group['max_members']}"
                ], className="mb-2"),
                
                html.Div([
                    html.Strong("Available Spots: "),
                    html.Span(
                        f"{group['spots_available']}",
                        className="text-success" if group['spots_available'] > 0 else "text-danger"
                    )
                ], className="mb-2"),
                
                html.Div([
                    html.Strong("Start Date: "),
                    start_date_str
                ], className="mb-2"),
                
                html.Div([
                    html.Strong("End Date: "),
                    end_date_str
                ], className="mb-2"),
                
                html.Div([
                    html.Strong("Created by: "),
                    group.get('creator_name', 'Unknown')
                ], className="mb-2"),
                
            ], className="col-md-6"),
            
            html.Div([
                html.H6("Current Members", className="fw-bold mb-3"),
                html.Ul(members_content, className="list-unstyled"),
            ], className="col-md-6"),
            
        ], className="row"),
        
        # Status information
        html.Hr(),
        html.Div([
            html.H6("Status", className="fw-bold"),
            dbc.Badge(
                "Full - No spots available" if group.get('is_full') else f"{group['spots_available']} spots available",
                color="danger" if group.get('is_full') else "success",
                className="me-2"
            ),
            dbc.Badge(
                group['status'].capitalize(),
                color="success" if group['status'] == 'active' else "secondary"
            ),
        ], className="mb-3"),
    ])


def create_join_request_modal() -> dbc.Modal:
    """Create modal for joining a group.
    
    Returns:
        dbc.Modal: Join request modal component
    """
    return dbc.Modal(
        [
            dbc.ModalHeader(
                dbc.ModalTitle("Request to Join Group"),
                close_button=True,
            ),
            dbc.ModalBody([
                html.Div(id="join-request-content"),
                dbc.Alert(
                    id="join-request-alert",
                    is_open=False,
                    dismissable=True,
                ),
            ]),
            dbc.ModalFooter([
                dbc.Button(
                    "Cancel",
                    id="join-request-cancel",
                    color="secondary"
                ),
                dbc.Button(
                    "Send Request",
                    id="join-request-confirm",
                    color="primary"
                ),
            ]),
        ],
        id="join-request-modal",
        is_open=False,
    )