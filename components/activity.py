from dash import html

# Activity Section component
def create_activity_section():
    # Icons using Font Awesome 
    check_icon = html.I(className="fas fa-check", style={"fontSize": "20px"})
    
    # Chart icon
    chart_icon = html.I(className="fas fa-chart-line", style={"fontSize": "20px"})
    
    # Warning icon
    warning_icon = html.I(className="fas fa-exclamation-triangle", style={"fontSize": "20px"})
    
    # Money icon
    money_icon = html.I(className="fas fa-money-bill", style={"fontSize": "20px"})
    
    return html.Section(
        className="mb-5",
        children=[
            html.Div(
                className="section-header",
                children=[
                    html.H2("Recent Activity", className="section-title"),
                ]
            ),
            html.Div(
                className="activity-list",
                children=[
                    html.Div(
                        className="activity-item",
                        children=[
                            html.Div(className="activity-icon", children=[check_icon]),
                            html.Div(
                                className="activity-content",
                                children=[
                                    html.Div(
                                        className="activity-text",
                                        children=[
                                            html.Strong("Mary received the payout"),
                                            " for Family Savings Group"
                                        ]
                                    ),
                                    html.Div("Yesterday, 4:15 PM", className="activity-time"),
                                ]
                            ),
                            html.Div("£600", className="activity-amount"),
                        ]
                    ),
                    html.Div(
                        className="activity-item",
                        children=[
                            html.Div(className="activity-icon", children=[chart_icon]),
                            html.Div(
                                className="activity-content",
                                children=[
                                    html.Div(
                                        className="activity-text",
                                        children=[
                                            html.Strong("John joined"),
                                            " your Family Savings Group"
                                        ]
                                    ),
                                    html.Div("03 Feb, 2:30 PM", className="activity-time"),
                                ]
                            ),
                        ]
                    ),
                    html.Div(
                        className="activity-item",
                        children=[
                            html.Div(className="activity-icon", children=[warning_icon]),
                            html.Div(
                                className="activity-content",
                                children=[
                                    html.Div(
                                        className="activity-text",
                                        children=[
                                            html.Strong("You paid your contribution"),
                                            " for Office Colleagues Group"
                                        ]
                                    ),
                                    html.Div("Today, 10:25 AM", className="activity-time"),
                                ]
                            ),
                            html.Div("£100", className="activity-amount"),
                        ]
                    ),
                    html.Div(
                        className="activity-item",
                        children=[
                            html.Div(className="activity-icon", children=[money_icon]),
                            html.Div(
                                className="activity-content",
                                children=[
                                    html.Div(
                                        className="activity-text",
                                        children=[
                                            html.Strong("You created"),
                                            " a new Ajo group"
                                        ]
                                    ),
                                    html.Div("01 Feb, 9:15 AM", className="activity-time"),
                                ]
                            ),
                        ]
                    ),
                ]
            ),
        ]
    )