# import dash
# from dash import html
# from components.dashboard_cards import create_dashboard_cards
# from components.groups import create_groups_section
# from components.activity import create_activity_section
# from components.modals import create_group_modal, create_success_modal

# # Register the page
# dash.register_page(__name__, path="/", title="Dashboard | Ajo", name="Dashboard")

# # Dashboard Header component
# def create_dashboard_header():
#     return html.Div(
#         className="dashboard-header",
#         children=[
#             html.H1("Welcome back, Abel!", className="dashboard-title"),
#             html.P("Here's an overview of your Ajo activities.", className="dashboard-subtitle"),
#         ]
#     )

# # Layout for this page
# layout = html.Div([
#     # Dashboard Header
#     create_dashboard_header(),
    
#     # Dashboard Cards
#     create_dashboard_cards(),
    
#     # Groups Section
#     create_groups_section(),
    
#     # Activity Section
#     create_activity_section(),
    
#     # Modals
#     create_group_modal(),
#     create_success_modal(),
# ])

import dash
from dash import html, callback_context
from dash.dependencies import Input, Output, State
from components.dashboard_cards import create_dashboard_cards
from components.groups import create_groups_section
from components.activity import create_activity_section
from components.modals import create_group_modal, create_success_modal

# Register the page
dash.register_page(__name__, path="/", title="Dashboard | Ajo", name="Dashboard")

# Dashboard Header component
def create_dashboard_header(name="Abel"):
    return html.Div(
        className="dashboard-header",
        children=[
            html.H1(f"Welcome back, {name}!", className="dashboard-title"),
            html.P("Here's an overview of your Ajo activities.", className="dashboard-subtitle"),
        ]
    )

# Layout for this page
def layout():
    return html.Div([
        # Dashboard Header (we'll update this with the callback below)
        html.Div(id='dashboard-header-container'),
        create_dashboard_header(),
        
        # Dashboard Cards
        create_dashboard_cards(),
        
        # Groups Section
        create_groups_section(),
        
        # Activity Section
        create_activity_section(),
        
        # Modals
        create_group_modal(),
        create_success_modal(),
    ])

# # Callback to update the dashboard header with user's name
# @dash.callback(
#     Output('dashboard-header-container', 'children'),
#     Input('session-store', 'data')
# )
# def update_dashboard_header(session_data):
#     name = "Abel"  # Default name
#     if session_data and session_data.get('user_info'):
#         name = session_data['user_info'].get('name', name)
    
#     return create_dashboard_header(name)