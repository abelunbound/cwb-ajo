import dash_bootstrap_components as dbc
from dash import html

# Create Group Modal component
def create_group_modal():
    return dbc.Modal(
        [
            dbc.ModalHeader(html.H5("Create New Ajo Group", className="modal-title")),
            dbc.ModalBody(
                [
                    # Tabs
                    dbc.Tabs(
                        [
                            dbc.Tab(
                                [
                                    html.Div(
                                        className="form-group mt-3",
                                        children=[
                                            html.Label("Group Name"),
                                            dbc.Input(type="text", placeholder="e.g. Family Savings"),
                                        ]
                                    ),
                                    html.Div(
                                        className="form-group mt-3",
                                        children=[
                                            html.Label("Contribution Amount"),
                                            dbc.InputGroup([
                                                dbc.InputGroupText("£"),
                                                dbc.Input(type="number", placeholder="e.g. 100"),
                                            ]),
                                        ]
                                    ),
                                    html.Div(
                                        className="form-row mt-3",
                                        children=[
                                            html.Div(
                                                className="form-group col",
                                                children=[
                                                    html.Label("Contribution Frequency"),
                                                    dbc.Select(
                                                        options=[
                                                            {"label": "Weekly", "value": "weekly"},
                                                            {"label": "Monthly", "value": "monthly"},
                                                            {"label": "Bi-weekly", "value": "biweekly"},
                                                        ],
                                                        value="monthly",
                                                    ),
                                                ]
                                            ),
                                            html.Div(
                                                className="form-group col",
                                                children=[
                                                    html.Label("Number of Members"),
                                                    dbc.Input(type="number", placeholder="e.g. 6", min=2),
                                                ]
                                            ),
                                        ]
                                    ),
                                    html.Div(
                                        className="form-group mt-3",
                                        children=[
                                            html.Label("Group Description (Optional)"),
                                            dbc.Textarea(placeholder="What's the purpose of this Ajo group?", rows=3),
                                        ]
                                    ),
                                ],
                                label="Details",
                                tab_id="details",
                            ),
                            dbc.Tab(
                                [
                                    html.Div(
                                        className="form-group mt-3",
                                        children=[
                                            html.Label("Invite Members"),
                                            dbc.InputGroup([
                                                dbc.Input(type="email", placeholder="Enter email address"),
                                                dbc.Button("Add", color="primary"),
                                            ]),
                                        ]
                                    ),
                                    html.Div(
                                        className="mt-3",
                                        children=[
                                            html.Label("Added Members"),
                                            html.Div(
                                                className="invited-member",
                                                children=[
                                                    html.Div(
                                                        className="member-info",
                                                        children=[
                                                            html.Div("J", className="avatar", style={"backgroundColor": "#5F2EEA"}),
                                                            html.Div(
                                                                children=[
                                                                    html.Div("John Doe", className="member-name"),
                                                                    html.Div("john.doe@example.com", className="member-email"),
                                                                ]
                                                            ),
                                                        ]
                                                    ),
                                                    html.Button("×", className="remove-btn"),
                                                ]
                                            ),
                                            html.Div(
                                                className="invited-member",
                                                children=[
                                                    html.Div(
                                                        className="member-info",
                                                        children=[
                                                            html.Div("S", className="avatar", style={"backgroundColor": "#2ECC71"}),
                                                            html.Div(
                                                                children=[
                                                                    html.Div("Sarah Smith", className="member-name"),
                                                                    html.Div("sarah.smith@example.com", className="member-email"),
                                                                ]
                                                            ),
                                                        ]
                                                    ),
                                                    html.Button("×", className="remove-btn"),
                                                ]
                                            ),
                                        ]
                                    ),
                                ],
                                label="Members",
                                tab_id="members",
                            ),
                            dbc.Tab(
                                [
                                    html.P("Set the order in which members will receive payouts", className="mt-3"),
                                    html.Div(
                                        className="schedule-list",
                                        children=[
                                            html.Div(
                                                className="schedule-item",
                                                children=[
                                                    html.Div("Month 1", className="schedule-month"),
                                                    html.Div(
                                                        className="schedule-recipient",
                                                        children=[
                                                            html.Div("S", className="avatar", style={"backgroundColor": "#2ECC71"}),
                                                            html.Div("Sarah Smith"),
                                                        ]
                                                    ),
                                                ]
                                            ),
                                            html.Div(
                                                className="schedule-item",
                                                children=[
                                                    html.Div("Month 2", className="schedule-month"),
                                                    html.Div(
                                                        className="schedule-recipient",
                                                        children=[
                                                            html.Div("A", className="avatar", style={"backgroundColor": "#5F2EEA"}),
                                                            html.Div("Ade (You)"),
                                                            html.Span("You", className="badge ms-2"),
                                                        ]
                                                    ),
                                                ]
                                            ),
                                            html.Div(
                                                className="schedule-item",
                                                children=[
                                                    html.Div("Month 3", className="schedule-month"),
                                                    html.Div(
                                                        className="schedule-recipient",
                                                        children=[
                                                            html.Div("J", className="avatar", style={"backgroundColor": "#F7B731"}),
                                                            html.Div("John Doe"),
                                                        ]
                                                    ),
                                                ]
                                            ),
                                        ]
                                    ),
                                    html.Div(
                                        className="form-group mt-3",
                                        children=[
                                            html.Label("Payout Distribution Method"),
                                            dbc.RadioItems(
                                                options=[
                                                    {"label": "Random order", "value": "random"},
                                                    {"label": "Custom order (set manually)", "value": "custom"},
                                                    {"label": "Round-robin (rotating order)", "value": "roundrobin"},
                                                ],
                                                value="custom",
                                                className="mt-2",
                                            ),
                                        ]
                                    ),
                                ],
                                label="Schedule",
                                tab_id="schedule",
                            ),
                        ],
                        id="tabs",
                        active_tab="details",
                    ),
                ]
            ),
            dbc.ModalFooter(
                [
                    dbc.Button("Cancel", id="close-modal", color="secondary", className="me-2"),
                    dbc.Button("Create Group", id="save-group", color="primary"),
                ]
            ),
        ],
        id="create-group-modal",
        size="lg",
    )

# Success Modal component
def create_success_modal():
    return dbc.Modal(
        [
            dbc.ModalBody(
                [
                    html.Div(
                        className="success-container",
                        children=[
                            html.Div(
                                className="success-icon",
                                children=[
                                    html.I(className="fas fa-check-circle", style={"fontSize": "40px", "color": "#2ECC71"}),
                                ]
                            ),
                            html.H3("Group Created Successfully!", className="success-title"),
                            html.P(
                                "Your new Ajo group has been created. Invitations have been sent to all members.",
                                className="success-message"
                            ),
                            dbc.Button("See Group Details", color="primary", className="me-2"),
                            dbc.Button("Close", id="close-success", color="link"),
                        ]
                    ),
                ]
            ),
        ],
        id="success-modal",
        centered=True,
    )