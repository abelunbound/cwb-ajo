import dash
from dash.dependencies import Input, Output, State
from app import app

# Callbacks for modal functionality
@app.callback(
    Output("create-group-modal", "is_open"),
    [Input("create-group-btn", "n_clicks"), 
     Input("new-group-btn", "n_clicks"),
     Input("create-group-card", "n_clicks"),
     Input("close-modal", "n_clicks"),
     Input("save-group", "n_clicks")],
    [State("create-group-modal", "is_open")],
)
def toggle_modal(n1, n2, n3, n4, n5, is_open):
    if n1 or n2 or n3 or n4 or n5:
        return not is_open
    return is_open

@app.callback(
    [Output("success-modal", "is_open"),
     Output("create-group-modal", "is_open", allow_duplicate=True)],
    [Input("save-group", "n_clicks")],
    [State("success-modal", "is_open"),
     State("create-group-modal", "is_open")],
    prevent_initial_call=True,
)
def show_success_modal(n, success_open, group_open):
    if n:
        return True, False
    return success_open, group_open

@app.callback(
    Output("success-modal", "is_open", allow_duplicate=True),
    [Input("close-success", "n_clicks")],
    [State("success-modal", "is_open")],
    prevent_initial_call=True,
)
def close_success_modal(n, is_open):
    if n:
        return False
    return is_open


# Add this to your existing callbacks
@app.callback(
    Output("url", "pathname"),
    Input("session-store", "clear_data"),
    prevent_initial_call=True
)
def redirect_after_logout(clear_data):
    if clear_data:
        return "/"
    return dash.no_update