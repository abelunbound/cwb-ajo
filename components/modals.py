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
                                            html.Label("Group Name *", className="form-label"),
                                            dbc.Input(
                                                id="group-name-input",
                                                type="text", 
                                                placeholder="e.g. Family Savings Circle",
                                                required=True
                                            ),
                                            html.Div(id="group-name-feedback", className="invalid-feedback")
                                        ]
                                    ),
                                    html.Div(
                                        className="form-group mt-3",
                                        children=[
                                            html.Label("Group Description", className="form-label"),
                                            dbc.Textarea(
                                                id="group-description-input",
                                                placeholder="What's the purpose of this Ajo group?", 
                                                rows=3
                                            ),
                                            html.Div(id="group-description-feedback", className="invalid-feedback")
                                        ]
                                    ),
                                    html.Div(
                                        className="form-group mt-3",
                                        children=[
                                            html.Label("Contribution Amount *", className="form-label"),
                                            dbc.InputGroup([
                                                dbc.InputGroupText("£"),
                                                dbc.Select(
                                                    id="contribution-amount-input",
                                                    options=[
                                                        {"label": "£50", "value": 50},
                                                        {"label": "£100", "value": 100},
                                                        {"label": "£500", "value": 500},
                                                        {"label": "£800", "value": 800},
                                                    ],
                                                    placeholder="Select amount",
                                                    required=True
                                                ),
                                            ]),
                                            html.Div(id="contribution-amount-feedback", className="invalid-feedback")
                                        ]
                                    ),
                                    html.Div(
                                        className="form-row mt-3",
                                        children=[
                                            html.Div(
                                                className="form-group col",
                                                children=[
                                                    html.Label("Contribution Frequency *", className="form-label"),
                                                    dbc.Select(
                                                        id="frequency-input",
                                                        options=[
                                                            {"label": "Weekly", "value": "weekly"},
                                                            {"label": "Monthly", "value": "monthly"},
                                                        ],
                                                        placeholder="Select frequency",
                                                        required=True
                                                    ),
                                                    html.Div(id="frequency-feedback", className="invalid-feedback")
                                                ]
                                            ),
                                            html.Div(
                                                className="form-group col",
                                                children=[
                                                    html.Label("Duration (Months) *", className="form-label"),
                                                    dbc.Input(
                                                        id="duration-input",
                                                        type="number", 
                                                        placeholder="e.g. 12",
                                                        min=3,
                                                        max=24,
                                                        required=True
                                                    ),
                                                    html.Small("Minimum 3 months, maximum 24 months", className="form-text text-muted"),
                                                    html.Div(id="duration-feedback", className="invalid-feedback")
                                                ]
                                            ),
                                        ]
                                    ),
                                    html.Div(
                                        className="form-row mt-3",
                                        children=[
                                            html.Div(
                                                className="form-group col",
                                                children=[
                                                    html.Label("Maximum Members *", className="form-label"),
                                                    dbc.Select(
                                                        id="max-members-input",
                                                        options=[
                                                            {"label": "5 members", "value": 5},
                                                            {"label": "6 members", "value": 6},
                                                            {"label": "7 members", "value": 7},
                                                            {"label": "8 members", "value": 8},
                                                            {"label": "9 members", "value": 9},
                                                            {"label": "10 members", "value": 10},
                                                        ],
                                                        placeholder="Select max members",
                                                        required=True
                                                    ),
                                                    html.Div(id="max-members-feedback", className="invalid-feedback")
                                                ]
                                            ),
                                            html.Div(
                                                className="form-group col",
                                                children=[
                                                    html.Label("Start Date *", className="form-label"),
                                                    dbc.Input(
                                                        id="start-date-input",
                                                        type="date",
                                                        required=True
                                                    ),
                                                    html.Small("Groups typically start within 1-2 weeks", className="form-text text-muted"),
                                                    html.Div(id="start-date-feedback", className="invalid-feedback")
                                                ]
                                            ),
                                        ]
                                    ),
                                    # Form validation alerts
                                    html.Div(id="form-validation-alert", className="mt-3"),
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
                    dbc.Button(
                        "Cancel", 
                        id="cancel-group-btn", 
                        color="secondary", 
                        className="me-2"
                    ),
                    dbc.Button(
                        "Create Group", 
                        id="create-group-btn", 
                        color="primary",
                        disabled=False
                    ),
                ]
            ),
        ],
        id="create-group-modal",
        is_open=False,
        size="lg",
        backdrop="static",
        keyboard=False,
    )

# Create Success Modal component
def create_success_modal():
    return dbc.Modal(
        [
            dbc.ModalHeader(
                html.H5("Group Created Successfully!", className="modal-title text-success")
            ),
            dbc.ModalBody(
                [
                    html.Div(
                        className="text-center",
                        children=[
                            html.I(className="fas fa-check-circle fa-3x text-success mb-3"),
                            html.H6("Your Ajo group has been created!", className="mb-3"),
                            html.P(
                                id="success-message-text",
                                className="text-muted",
                                children="You can now invite members to join your group."
                            ),
                        ]
                    )
                ]
            ),
            dbc.ModalFooter(
                [
                    dbc.Button(
                        "View Group", 
                        id="view-group-btn", 
                        color="primary",
                        className="me-2"
                    ),
                    dbc.Button(
                        "Close", 
                        id="close-success-btn", 
                        color="secondary"
                    ),
                ]
            ),
        ],
        id="success-modal",
        is_open=False,
        size="md",
    )