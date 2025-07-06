"""
Task 30: Group Membership Management Components

This module provides UI components for managing group membership,
including member lists, role management, and member actions.
"""

import dash
from dash import html, dcc
import dash_bootstrap_components as dbc


def create_membership_management_modal():
    """Create modal for managing group membership."""
    return dbc.Modal(
        [
            dbc.ModalHeader(
                html.H5("Manage Group Members", className="modal-title")
            ),
            dbc.ModalBody(
                [
                    # Group info section
                    html.Div(
                        id="membership-group-info",
                        className="mb-3 p-3 bg-light rounded",
                        children=[
                            html.H6("Group: Loading...", id="membership-group-name"),
                            html.P("Loading group details...", id="membership-group-details", className="text-muted mb-0")
                        ]
                    ),
                    
                    # Member list section
                    html.Div(
                        className="mb-3",
                        children=[
                            html.H6("Group Members", className="mb-2"),
                            html.Div(id="membership-member-list", children=[
                                dbc.Spinner(color="primary", size="sm")
                            ])
                        ]
                    ),
                    
                    # Actions section
                    html.Div(
                        className="border-top pt-3",
                        children=[
                            html.H6("Actions", className="mb-2"),
                            dbc.ButtonGroup(
                                [
                                    dbc.Button(
                                        [html.I(className="fas fa-user-plus me-2"), "Invite Member"],
                                        id="membership-invite-btn",
                                        color="primary",
                                        size="sm"
                                    ),
                                    dbc.Button(
                                        [html.I(className="fas fa-refresh me-2"), "Refresh"],
                                        id="membership-refresh-btn",
                                        color="outline-secondary",
                                        size="sm"
                                    )
                                ]
                            )
                        ]
                    ),
                    
                    # Alerts/feedback
                    html.Div(id="membership-alert", className="mt-3")
                ]
            ),
            dbc.ModalFooter(
                dbc.Button(
                    "Close",
                    id="membership-modal-close",
                    color="secondary"
                )
            )
        ],
        id="basic-membership-management-modal",  # Changed ID to avoid conflict
        is_open=False,
        size="lg",
        backdrop="static",
        keyboard=False
    )


def create_member_card(member_data):
    """Create a card component for displaying member information.
    
    Args:
        member_data (dict): Member information including name, role, status, etc.
        
    Returns:
        dbc.Card: Member card component
    """
    # Role badge styling
    role_color = "primary" if member_data.get('role') == 'admin' else "secondary"
    
    # Status badge styling
    status = member_data.get('status', 'active')
    status_color = {
        'active': 'success',
        'pending': 'warning', 
        'removed': 'danger'
    }.get(status, 'secondary')
    
    # Payment position display
    payment_pos = member_data.get('payment_position', 'N/A')
    
    return dbc.Card(
        [
            dbc.CardBody(
                [
                    html.Div(
                        className="d-flex justify-content-between align-items-start",
                        children=[
                            # Member info
                            html.Div(
                                [
                                    html.H6(
                                        member_data.get('full_name', 'Unknown Member'),
                                        className="mb-1"
                                    ),
                                    html.Small(
                                        member_data.get('email', ''),
                                        className="text-muted"
                                    )
                                ]
                            ),
                            
                            # Badges
                            html.Div(
                                [
                                    dbc.Badge(
                                        member_data.get('role', 'member').title(),
                                        color=role_color,
                                        className="me-1"
                                    ),
                                    dbc.Badge(
                                        status.title(),
                                        color=status_color
                                    )
                                ]
                            )
                        ]
                    ),
                    
                    # Member details
                    html.Div(
                        className="mt-2",
                        children=[
                            html.Small(
                                [
                                    html.Strong("Payment Position: "),
                                    f"#{payment_pos}"
                                ],
                                className="text-muted d-block"
                            ),
                            html.Small(
                                [
                                    html.Strong("Joined: "),
                                    member_data.get('join_date', 'Unknown')
                                ],
                                className="text-muted d-block"
                            )
                        ]
                    ),
                    
                    # Action buttons (only show for active members)
                    html.Div(
                        className="mt-3",
                        children=[
                            dbc.ButtonGroup(
                                [
                                    dbc.Button(
                                        "Change Role",
                                        id={"type": "change-role-btn", "member_id": member_data.get('id')},
                                        color="outline-primary",
                                        size="sm"
                                    ),
                                    dbc.Button(
                                        "Remove",
                                        id={"type": "remove-member-btn", "member_id": member_data.get('id')},
                                        color="outline-danger",
                                        size="sm"
                                    )
                                ],
                                size="sm"
                            )
                        ]
                    ) if status == 'active' else html.Div()
                ]
            )
        ],
        className="mb-2"
    )


def create_member_list(members_data):
    """Create a list of member cards.
    
    Args:
        members_data (list): List of member dictionaries
        
    Returns:
        html.Div: Container with member cards
    """
    if not members_data:
        return html.Div(
            [
                html.I(className="fas fa-users fa-2x text-muted mb-2"),
                html.P("No members found", className="text-muted")
            ],
            className="text-center py-4"
        )
    
    member_cards = [create_member_card(member) for member in members_data]
    
    return html.Div(
        member_cards,
        className="member-list-container",
        style={"maxHeight": "400px", "overflowY": "auto"}
    )


def create_role_change_modal():
    """Create modal for changing member roles."""
    return dbc.Modal(
        [
            dbc.ModalHeader(html.H5("Change Member Role")),
            dbc.ModalBody(
                [
                    html.Div(
                        id="role-change-member-info",
                        className="mb-3 p-3 bg-light rounded",
                        children=[
                            html.H6("Member: Loading...", id="role-change-member-name"),
                            html.P("Current role: Loading...", id="role-change-current-role", className="text-muted mb-0")
                        ]
                    ),
                    
                    html.Div(
                        className="form-group",
                        children=[
                            html.Label("New Role", className="form-label"),
                            dcc.Dropdown(
                                id="role-change-dropdown",
                                options=[
                                    {"label": "Admin", "value": "admin"},
                                    {"label": "Member", "value": "member"}
                                ],
                                placeholder="Select new role...",
                                className="mb-2"
                            ),
                            html.Small(
                                "Admins can manage group settings and members. Members can view group info and make contributions.",
                                className="form-text text-muted"
                            )
                        ]
                    ),
                    
                    # Alert area
                    html.Div(id="role-change-alert", className="mt-3")
                ]
            ),
            dbc.ModalFooter(
                [
                    dbc.Button(
                        "Cancel",
                        id="role-change-cancel",
                        color="secondary",
                        className="me-2"
                    ),
                    dbc.Button(
                        "Update Role",
                        id="role-change-confirm",
                        color="primary"
                    )
                ]
            )
        ],
        id="role-change-modal",
        is_open=False,
        size="md"
    )


def create_remove_member_modal():
    """Create modal for removing members."""
    return dbc.Modal(
        [
            dbc.ModalHeader(html.H5("Remove Member", className="text-danger")),
            dbc.ModalBody(
                [
                    html.Div(
                        className="text-center mb-3",
                        children=[
                            html.I(className="fas fa-exclamation-triangle fa-3x text-warning mb-3"),
                            html.H6("Are you sure you want to remove this member?")
                        ]
                    ),
                    
                    html.Div(
                        id="remove-member-info",
                        className="mb-3 p-3 bg-light rounded",
                        children=[
                            html.H6("Member: Loading...", id="remove-member-name"),
                            html.P("Role: Loading...", id="remove-member-role", className="text-muted mb-0")
                        ]
                    ),
                    
                    dbc.Alert(
                        [
                            html.Strong("Warning: "),
                            "This action cannot be undone. The member will be removed from the group and lose access to all group features."
                        ],
                        color="warning",
                        className="mb-3"
                    ),
                    
                    # Alert area
                    html.Div(id="remove-member-alert", className="mt-3")
                ]
            ),
            dbc.ModalFooter(
                [
                    dbc.Button(
                        "Cancel",
                        id="remove-member-cancel",
                        color="secondary",
                        className="me-2"
                    ),
                    dbc.Button(
                        "Remove Member",
                        id="remove-member-confirm",
                        color="danger"
                    )
                ]
            )
        ],
        id="remove-member-modal",
        is_open=False,
        size="md"
    )


def create_membership_stats_card(stats_data):
    """Create a card showing membership statistics.
    
    Args:
        stats_data (dict): Statistics including total members, admins, etc.
        
    Returns:
        dbc.Card: Statistics card component
    """
    total_members = stats_data.get('total_members', 0)
    admin_count = stats_data.get('admin_count', 0)
    active_members = stats_data.get('active_members', 0)
    max_members = stats_data.get('max_members', 8)
    
    return dbc.Card(
        [
            dbc.CardHeader(html.H6("Membership Overview", className="mb-0")),
            dbc.CardBody(
                [
                    html.Div(
                        className="row text-center",
                        children=[
                            html.Div(
                                className="col-3",
                                children=[
                                    html.H4(str(active_members), className="mb-0 text-primary"),
                                    html.Small("Active", className="text-muted")
                                ]
                            ),
                            html.Div(
                                className="col-3",
                                children=[
                                    html.H4(str(admin_count), className="mb-0 text-success"),
                                    html.Small("Admins", className="text-muted")
                                ]
                            ),
                            html.Div(
                                className="col-3",
                                children=[
                                    html.H4(str(total_members), className="mb-0 text-info"),
                                    html.Small("Total", className="text-muted")
                                ]
                            ),
                            html.Div(
                                className="col-3",
                                children=[
                                    html.H4(str(max_members - active_members), className="mb-0 text-warning"),
                                    html.Small("Available", className="text-muted")
                                ]
                            )
                        ]
                    )
                ]
            )
        ],
        className="mb-3"
    )


def create_member_status_change_modal():
    """Create modal for changing member status."""
    return dbc.Modal(
        [
            dbc.ModalHeader(html.H5("Change Member Status")),
            dbc.ModalBody(
                [
                    html.Div(
                        id="status-change-member-info",
                        className="mb-3 p-3 bg-light rounded",
                        children=[
                            html.H6("Member: Loading...", id="status-change-member-name"),
                            html.P("Current status: Loading...", id="status-change-current-status", className="text-muted mb-0")
                        ]
                    ),
                    
                    html.Div(
                        className="form-group",
                        children=[
                            html.Label("New Status", className="form-label"),
                            dcc.Dropdown(
                                id="status-change-dropdown",
                                options=[
                                    {"label": "Active", "value": "active"},
                                    {"label": "Pending", "value": "pending"},
                                    {"label": "Suspended", "value": "suspended"},
                                    {"label": "Removed", "value": "removed"}
                                ],
                                placeholder="Select new status...",
                                className="mb-2"
                            ),
                            html.Small(
                                "Active: Full access. Pending: Limited access. Suspended: Temporary restriction. Removed: No access.",
                                className="form-text text-muted"
                            )
                        ]
                    ),
                    
                    # Reason for status change
                    html.Div(
                        className="form-group mt-3",
                        children=[
                            html.Label("Reason (Optional)", className="form-label"),
                            dcc.Textarea(
                                id="status-change-reason",
                                placeholder="Enter reason for status change...",
                                className="form-control",
                                style={"height": "80px"}
                            )
                        ]
                    ),
                    
                    # Alert area
                    html.Div(id="status-change-alert", className="mt-3")
                ]
            ),
            dbc.ModalFooter(
                [
                    dbc.Button(
                        "Cancel",
                        id="status-change-cancel",
                        color="secondary",
                        className="me-2"
                    ),
                    dbc.Button(
                        "Update Status",
                        id="status-change-confirm",
                        color="primary"
                    )
                ]
            )
        ],
        id="member-status-change-modal",
        is_open=False,
        size="md"
    )


def create_member_activity_card(activity_data):
    """Create a card showing member activity/history.
    
    Args:
        activity_data (dict): Activity information
        
    Returns:
        dbc.Card: Activity card component
    """
    activity_type = activity_data.get('type', 'unknown')
    activity_icons = {
        'joined': 'fas fa-user-plus text-success',
        'role_changed': 'fas fa-user-cog text-primary',
        'status_changed': 'fas fa-toggle-on text-warning',
        'payment_made': 'fas fa-credit-card text-success',
        'payment_missed': 'fas fa-exclamation-triangle text-danger',
        'invited_member': 'fas fa-envelope text-info',
        'left_group': 'fas fa-user-minus text-danger'
    }
    
    icon_class = activity_icons.get(activity_type, 'fas fa-circle text-secondary')
    
    return dbc.Card(
        [
            dbc.CardBody(
                [
                    html.Div(
                        className="d-flex align-items-start",
                        children=[
                            html.I(className=f"{icon_class} me-3 mt-1"),
                            html.Div(
                                [
                                    html.H6(
                                        activity_data.get('title', 'Activity'),
                                        className="mb-1"
                                    ),
                                    html.P(
                                        activity_data.get('description', ''),
                                        className="text-muted mb-1"
                                    ),
                                    html.Small(
                                        activity_data.get('timestamp', ''),
                                        className="text-muted"
                                    )
                                ],
                                className="flex-grow-1"
                            )
                        ]
                    )
                ]
            )
        ],
        className="mb-2 border-start border-3",
        style={"borderLeftColor": "#007bff !important"}
    )


def create_member_activity_list(activities_data):
    """Create a list of member activities.
    
    Args:
        activities_data (list): List of activity dictionaries
        
    Returns:
        html.Div: Container with activity cards
    """
    if not activities_data:
        return html.Div(
            [
                html.I(className="fas fa-history fa-2x text-muted mb-2"),
                html.P("No recent activity", className="text-muted")
            ],
            className="text-center py-4"
        )
    
    activity_cards = [create_member_activity_card(activity) for activity in activities_data]
    
    return html.Div(
        activity_cards,
        className="activity-list-container",
        style={"maxHeight": "300px", "overflowY": "auto"}
    )


def create_enhanced_member_card(member_data):
    """Create an enhanced member card with status management and activity.
    
    Args:
        member_data (dict): Member information including status and activity
        
    Returns:
        dbc.Card: Enhanced member card component
    """
    # Role badge styling
    role_color = "primary" if member_data.get('role') == 'admin' else "secondary"
    
    # Enhanced status badge styling
    status = member_data.get('status', 'active')
    status_colors = {
        'active': 'success',
        'pending': 'warning', 
        'suspended': 'danger',
        'removed': 'dark'
    }
    status_color = status_colors.get(status, 'secondary')
    
    # Activity indicator
    last_activity = member_data.get('last_activity', 'No recent activity')
    activity_color = 'success' if 'today' in last_activity.lower() else 'muted'
    
    # Payment position display
    payment_pos = member_data.get('payment_position', 'N/A')
    
    return dbc.Card(
        [
            dbc.CardBody(
                [
                    html.Div(
                        className="d-flex justify-content-between align-items-start",
                        children=[
                            # Member info
                            html.Div(
                                [
                                    html.H6(
                                        member_data.get('full_name', 'Unknown Member'),
                                        className="mb-1"
                                    ),
                                    html.Small(
                                        member_data.get('email', ''),
                                        className="text-muted"
                                    )
                                ]
                            ),
                            
                            # Badges
                            html.Div(
                                [
                                    dbc.Badge(
                                        member_data.get('role', 'member').title(),
                                        color=role_color,
                                        className="me-1"
                                    ),
                                    dbc.Badge(
                                        status.title(),
                                        color=status_color
                                    )
                                ]
                            )
                        ]
                    ),
                    
                    # Member details with activity
                    html.Div(
                        className="mt-2",
                        children=[
                            html.Small(
                                [
                                    html.Strong("Payment Position: "),
                                    f"#{payment_pos}"
                                ],
                                className="text-muted d-block"
                            ),
                            html.Small(
                                [
                                    html.Strong("Joined: "),
                                    member_data.get('join_date', 'Unknown')
                                ],
                                className="text-muted d-block"
                            ),
                            html.Small(
                                [
                                    html.Strong("Last Activity: "),
                                    html.Span(last_activity, className=f"text-{activity_color}")
                                ],
                                className="text-muted d-block"
                            )
                        ]
                    ),
                    
                    # Enhanced action buttons
                    html.Div(
                        className="mt-3",
                        children=[
                            dbc.ButtonGroup(
                                [
                                    dbc.Button(
                                        "Change Role",
                                        id={"type": "change-role-btn", "member_id": member_data.get('id')},
                                        color="outline-primary",
                                        size="sm"
                                    ),
                                    dbc.Button(
                                        "Change Status",
                                        id={"type": "change-status-btn", "member_id": member_data.get('id')},
                                        color="outline-warning",
                                        size="sm"
                                    ),
                                    dbc.Button(
                                        "Remove",
                                        id={"type": "remove-member-btn", "member_id": member_data.get('id')},
                                        color="outline-danger",
                                        size="sm"
                                    )
                                ],
                                size="sm"
                            )
                        ]
                    ) if status in ['active', 'pending', 'suspended'] else html.Div(
                        dbc.Badge("Member Removed", color="dark", className="mt-2")
                    )
                ]
            )
        ],
        className="mb-2"
    )


def create_member_stats_overview(stats_data):
    """Create a comprehensive member statistics overview.
    
    Args:
        stats_data (dict): Statistics data
        
    Returns:
        dbc.Card: Statistics overview card
    """
    total_members = stats_data.get('total_members', 0)
    active_members = stats_data.get('active_members', 0)
    pending_members = stats_data.get('pending_members', 0)
    suspended_members = stats_data.get('suspended_members', 0)
    admin_count = stats_data.get('admin_count', 0)
    recent_activity = stats_data.get('recent_activity', 0)
    
    return dbc.Card(
        [
            dbc.CardHeader(html.H6("Member Statistics", className="mb-0")),
            dbc.CardBody(
                [
                    html.Div(
                        className="row text-center mb-3",
                        children=[
                            html.Div(
                                className="col-4",
                                children=[
                                    html.H4(str(active_members), className="mb-0 text-success"),
                                    html.Small("Active", className="text-muted")
                                ]
                            ),
                            html.Div(
                                className="col-4",
                                children=[
                                    html.H4(str(pending_members), className="mb-0 text-warning"),
                                    html.Small("Pending", className="text-muted")
                                ]
                            ),
                            html.Div(
                                className="col-4",
                                children=[
                                    html.H4(str(suspended_members), className="mb-0 text-danger"),
                                    html.Small("Suspended", className="text-muted")
                                ]
                            )
                        ]
                    ),
                    html.Div(
                        className="row text-center",
                        children=[
                            html.Div(
                                className="col-4",
                                children=[
                                    html.H5(str(admin_count), className="mb-0 text-primary"),
                                    html.Small("Admins", className="text-muted")
                                ]
                            ),
                            html.Div(
                                className="col-4",
                                children=[
                                    html.H5(str(total_members), className="mb-0 text-info"),
                                    html.Small("Total", className="text-muted")
                                ]
                            ),
                            html.Div(
                                className="col-4",
                                children=[
                                    html.H5(str(recent_activity), className="mb-0 text-success"),
                                    html.Small("Recent Activity", className="text-muted")
                                ]
                            )
                        ]
                    )
                ]
            )
        ],
        className="mb-3"
    )


def create_member_contact_modal():
    """Create modal for contacting members."""
    return dbc.Modal(
        [
            dbc.ModalHeader(html.H5("Contact Member")),
            dbc.ModalBody(
                [
                    html.Div(
                        id="contact-member-info",
                        className="mb-3 p-3 bg-light rounded",
                        children=[
                            html.H6("Member: Loading...", id="contact-member-name"),
                            html.P("Email: Loading...", id="contact-member-email", className="text-muted mb-0")
                        ]
                    ),
                    
                    html.Div(
                        className="form-group",
                        children=[
                            html.Label("Subject", className="form-label"),
                            dcc.Input(
                                id="contact-subject",
                                type="text",
                                placeholder="Enter message subject...",
                                className="form-control mb-2"
                            )
                        ]
                    ),
                    
                    html.Div(
                        className="form-group",
                        children=[
                            html.Label("Message", className="form-label"),
                            dcc.Textarea(
                                id="contact-message",
                                placeholder="Type your message here...",
                                className="form-control",
                                style={"height": "120px"}
                            )
                        ]
                    ),
                    
                    # Quick message templates
                    html.Div(
                        className="form-group mt-3",
                        children=[
                            html.Label("Quick Templates", className="form-label"),
                            dbc.ButtonGroup(
                                [
                                    dbc.Button(
                                        "Payment Reminder",
                                        id="template-payment-reminder",
                                        color="outline-primary",
                                        size="sm"
                                    ),
                                    dbc.Button(
                                        "Welcome Message",
                                        id="template-welcome",
                                        color="outline-success",
                                        size="sm"
                                    ),
                                    dbc.Button(
                                        "Group Update",
                                        id="template-update",
                                        color="outline-info",
                                        size="sm"
                                    )
                                ],
                                size="sm"
                            )
                        ]
                    ),
                    
                    # Alert area
                    html.Div(id="contact-alert", className="mt-3")
                ]
            ),
            dbc.ModalFooter(
                [
                    dbc.Button(
                        "Cancel",
                        id="contact-cancel",
                        color="secondary",
                        className="me-2"
                    ),
                    dbc.Button(
                        "Send Message",
                        id="contact-send",
                        color="primary"
                    )
                ]
            )
        ],
        id="member-contact-modal",
        is_open=False,
        size="lg"
    )


def create_group_announcement_modal():
    """Create modal for sending group announcements."""
    return dbc.Modal(
        [
            dbc.ModalHeader(html.H5("Send Group Announcement")),
            dbc.ModalBody(
                [
                    html.Div(
                        id="announcement-group-info",
                        className="mb-3 p-3 bg-light rounded",
                        children=[
                            html.H6("Group: Loading...", id="announcement-group-name"),
                            html.P("Recipients: Loading...", id="announcement-recipients", className="text-muted mb-0")
                        ]
                    ),
                    
                    # Recipient selection
                    html.Div(
                        className="form-group mb-3",
                        children=[
                            html.Label("Send To", className="form-label"),
                            dcc.Checklist(
                                id="announcement-recipients-checklist",
                                options=[
                                    {"label": "All Active Members", "value": "active"},
                                    {"label": "Admins Only", "value": "admins"},
                                    {"label": "Pending Members", "value": "pending"}
                                ],
                                value=["active"],
                                className="form-check"
                            )
                        ]
                    ),
                    
                    html.Div(
                        className="form-group",
                        children=[
                            html.Label("Announcement Title", className="form-label"),
                            dcc.Input(
                                id="announcement-title",
                                type="text",
                                placeholder="Enter announcement title...",
                                className="form-control mb-2"
                            )
                        ]
                    ),
                    
                    html.Div(
                        className="form-group",
                        children=[
                            html.Label("Message", className="form-label"),
                            dcc.Textarea(
                                id="announcement-message",
                                placeholder="Type your announcement here...",
                                className="form-control",
                                style={"height": "120px"}
                            )
                        ]
                    ),
                    
                    # Priority level
                    html.Div(
                        className="form-group mt-3",
                        children=[
                            html.Label("Priority", className="form-label"),
                            dcc.Dropdown(
                                id="announcement-priority",
                                options=[
                                    {"label": "Low", "value": "low"},
                                    {"label": "Normal", "value": "normal"},
                                    {"label": "High", "value": "high"},
                                    {"label": "Urgent", "value": "urgent"}
                                ],
                                value="normal",
                                className="mb-2"
                            )
                        ]
                    ),
                    
                    # Alert area
                    html.Div(id="announcement-alert", className="mt-3")
                ]
            ),
            dbc.ModalFooter(
                [
                    dbc.Button(
                        "Cancel",
                        id="announcement-cancel",
                        color="secondary",
                        className="me-2"
                    ),
                    dbc.Button(
                        "Send Announcement",
                        id="announcement-send",
                        color="primary"
                    )
                ]
            )
        ],
        id="group-announcement-modal",
        is_open=False,
        size="lg"
    )


def create_enhanced_membership_management_modal():
    """Create enhanced membership management modal with all Phase 2 & 3 features."""
    return dbc.Modal(
        [
            dbc.ModalHeader(
                html.H5("Manage Group Members", className="modal-title")
            ),
            dbc.ModalBody(
                [
                    # Group info section
                    html.Div(
                        id="membership-group-info",
                        className="mb-3 p-3 bg-light rounded",
                        children=[
                            html.H6("Group: Loading...", id="membership-group-name"),
                            html.P("Loading group details...", id="membership-group-details", className="text-muted mb-0")
                        ]
                    ),
                    
                    # Enhanced statistics section
                    html.Div(id="membership-stats-overview", className="mb-3"),
                    
                    # Tabs for different views
                    dbc.Tabs(
                        [
                            dbc.Tab(
                                label="Members",
                                tab_id="members-tab",
                                children=[
                                    html.Div(
                                        className="mt-3",
                                        children=[
                                            html.Div(id="membership-member-list", children=[
                                                dbc.Spinner(color="primary", size="sm")
                                            ])
                                        ]
                                    )
                                ]
                            ),
                            dbc.Tab(
                                label="Activity",
                                tab_id="activity-tab",
                                children=[
                                    html.Div(
                                        className="mt-3",
                                        children=[
                                            html.H6("Recent Member Activity", className="mb-3"),
                                            html.Div(id="membership-activity-list", children=[
                                                dbc.Spinner(color="primary", size="sm")
                                            ])
                                        ]
                                    )
                                ]
                            ),
                            dbc.Tab(
                                label="Communication",
                                tab_id="communication-tab",
                                children=[
                                    html.Div(
                                        className="mt-3",
                                        children=[
                                            html.H6("Group Communication", className="mb-3"),
                                            dbc.ButtonGroup(
                                                [
                                                    dbc.Button(
                                                        [html.I(className="fas fa-bullhorn me-2"), "Send Announcement"],
                                                        id="send-announcement-btn",
                                                        color="primary",
                                                        size="sm"
                                                    ),
                                                    dbc.Button(
                                                        [html.I(className="fas fa-envelope me-2"), "Contact All"],
                                                        id="contact-all-btn",
                                                        color="info",
                                                        size="sm"
                                                    )
                                                ]
                                            ),
                                            html.Hr(),
                                            html.Div(id="communication-history", className="mt-3")
                                        ]
                                    )
                                ]
                            )
                        ],
                        id="membership-tabs",
                        active_tab="members-tab"
                    ),
                    
                    # Actions section
                    html.Div(
                        className="border-top pt-3 mt-3",
                        children=[
                            html.H6("Quick Actions", className="mb-2"),
                            dbc.ButtonGroup(
                                [
                                    dbc.Button(
                                        [html.I(className="fas fa-user-plus me-2"), "Invite Member"],
                                        id="membership-invite-btn",
                                        color="primary",
                                        size="sm"
                                    ),
                                    dbc.Button(
                                        [html.I(className="fas fa-download me-2"), "Export List"],
                                        id="membership-export-btn",
                                        color="success",
                                        size="sm"
                                    ),
                                    dbc.Button(
                                        [html.I(className="fas fa-refresh me-2"), "Refresh"],
                                        id="membership-refresh-btn",
                                        color="outline-secondary",
                                        size="sm"
                                    )
                                ]
                            )
                        ]
                    ),
                    
                    # Alerts/feedback
                    html.Div(id="membership-alert", className="mt-3")
                ]
            ),
            dbc.ModalFooter(
                dbc.Button(
                    "Close",
                    id="membership-modal-close",
                    color="secondary"
                )
            )
        ],
        id="membership-management-modal",
        is_open=False,
        size="xl",  # Extra large for all features
        backdrop="static",
        keyboard=False
    )


def create_enhanced_member_list(members_data, show_activity=True):
    """Create an enhanced member list with activity and communication options.
    
    Args:
        members_data (list): List of member dictionaries
        show_activity (bool): Whether to show activity information
        
    Returns:
        html.Div: Container with enhanced member cards
    """
    if not members_data:
        return html.Div(
            [
                html.I(className="fas fa-users fa-2x text-muted mb-2"),
                html.P("No members found", className="text-muted")
            ],
            className="text-center py-4"
        )
    
    # Use enhanced member cards if activity is enabled
    if show_activity:
        member_cards = [create_enhanced_member_card(member) for member in members_data]
    else:
        member_cards = [create_member_card(member) for member in members_data]
    
    return html.Div(
        member_cards,
        className="member-list-container",
        style={"maxHeight": "500px", "overflowY": "auto"}
    )


def create_final_member_card_with_communication(member_data):
    """Create the final enhanced member card with all features including communication.
    
    Args:
        member_data (dict): Complete member information
        
    Returns:
        dbc.Card: Final enhanced member card
    """
    # All previous styling logic
    role_color = "primary" if member_data.get('role') == 'admin' else "secondary"
    status = member_data.get('status', 'active')
    status_colors = {
        'active': 'success',
        'pending': 'warning', 
        'suspended': 'danger',
        'removed': 'dark'
    }
    status_color = status_colors.get(status, 'secondary')
    
    last_activity = member_data.get('last_activity', 'No recent activity')
    activity_color = 'success' if 'today' in last_activity.lower() else 'muted'
    payment_pos = member_data.get('payment_position', 'N/A')
    
    return dbc.Card(
        [
            dbc.CardBody(
                [
                    html.Div(
                        className="d-flex justify-content-between align-items-start",
                        children=[
                            # Member info with contact link
                            html.Div(
                                [
                                    html.H6(
                                        member_data.get('full_name', 'Unknown Member'),
                                        className="mb-1"
                                    ),
                                    html.Small(
                                        [
                                            html.A(
                                                member_data.get('email', ''),
                                                id={"type": "contact-member-link", "member_id": member_data.get('id')},
                                                className="text-decoration-none"
                                            )
                                        ],
                                        className="text-muted"
                                    )
                                ]
                            ),
                            
                            # Badges with online status
                            html.Div(
                                [
                                    dbc.Badge(
                                        member_data.get('role', 'member').title(),
                                        color=role_color,
                                        className="me-1"
                                    ),
                                    dbc.Badge(
                                        status.title(),
                                        color=status_color,
                                        className="me-1"
                                    ),
                                    dbc.Badge(
                                        "●",
                                        color="success" if member_data.get('online', False) else "secondary",
                                        className="border-0",
                                        title="Online status"
                                    )
                                ]
                            )
                        ]
                    ),
                    
                    # Enhanced member details
                    html.Div(
                        className="mt-2",
                        children=[
                            html.Small(
                                [
                                    html.Strong("Payment Position: "),
                                    f"#{payment_pos}"
                                ],
                                className="text-muted d-block"
                            ),
                            html.Small(
                                [
                                    html.Strong("Joined: "),
                                    member_data.get('join_date', 'Unknown')
                                ],
                                className="text-muted d-block"
                            ),
                            html.Small(
                                [
                                    html.Strong("Last Activity: "),
                                    html.Span(last_activity, className=f"text-{activity_color}")
                                ],
                                className="text-muted d-block"
                            ),
                            html.Small(
                                [
                                    html.Strong("Messages: "),
                                    f"{member_data.get('message_count', 0)} sent"
                                ],
                                className="text-muted d-block"
                            )
                        ]
                    ),
                    
                    # Complete action buttons with communication
                    html.Div(
                        className="mt-3",
                        children=[
                            dbc.ButtonGroup(
                                [
                                    dbc.Button(
                                        "Contact",
                                        id={"type": "contact-member-btn", "member_id": member_data.get('id')},
                                        color="outline-info",
                                        size="sm"
                                    ),
                                    dbc.Button(
                                        "Change Role",
                                        id={"type": "change-role-btn", "member_id": member_data.get('id')},
                                        color="outline-primary",
                                        size="sm"
                                    ),
                                    dbc.Button(
                                        "Change Status",
                                        id={"type": "change-status-btn", "member_id": member_data.get('id')},
                                        color="outline-warning",
                                        size="sm"
                                    ),
                                    dbc.Button(
                                        "Remove",
                                        id={"type": "remove-member-btn", "member_id": member_data.get('id')},
                                        color="outline-danger",
                                        size="sm"
                                    )
                                ],
                                size="sm"
                            )
                        ]
                    ) if status in ['active', 'pending', 'suspended'] else html.Div(
                        [
                            dbc.Badge("Member Removed", color="dark", className="me-2"),
                            html.Small(
                                f"Removed on {member_data.get('removed_date', 'Unknown')}",
                                className="text-muted"
                            )
                        ],
                        className="mt-2"
                    )
                ]
            )
        ],
        className="mb-2"
    ) 