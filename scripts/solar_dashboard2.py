
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State, no_update
import pandas as pd
import plotly.graph_objects as go

# ==============================================================================
# IMPORT CUSTOM PROJECT MODULES
# ==============================================================================
from SystemConfig import SystemConfig
from run_pvlib import run_pvlib_model


# ==============================================================================
# DASH APPLICATION LAYOUT
# ==============================================================================
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])

# --- Reusable styles ---
input_style = {"marginBottom": "15px"}

# --- Define the app layout ---
app.layout = dbc.Container([
    dbc.Row(dbc.Col(html.H1("Solar Power Production Dashboard"), width=12), className="my-4"),
    dbc.Row([
        # --- Input Column ---
        dbc.Col(
            dbc.Card([
                dbc.CardHeader("System Configuration"),
                dbc.CardBody([
                    html.Label("ZIP Code:"),
                    dbc.Input(id="zip-input", value="83333", type="text", style=input_style),

                    html.Label("System Capacity (kW):"),
                    dbc.Input(id="capacity-input", value=7.5, type="number", min=1, max=100, step=0.5,
                              style=input_style),

                    html.Label("Tracking Type:"),
                    dcc.Dropdown(
                        id="tracking-input",
                        options=[{'label': 'Fixed Tilt', 'value': 'fixed'},
                                 {'label': 'Single-Axis', 'value': 'single-axis'}],
                        value='fixed', clearable=False, style=input_style
                    ),

                    # --- Conditional Inputs ---
                    html.Div(id='fixed-tilt-inputs', children=[
                        html.Label("Tilt (degrees):"),
                        dbc.Input(id="tilt-input", value=20, type="number", min=0, max=90, step=1, style=input_style),
                        html.Label("Azimuth (degrees, 180=South):"),
                        dbc.Input(id="azimuth-input", value=180, type="number", min=0, max=360, step=1,
                                  style=input_style),
                    ]),
                    html.Div(id='single-axis-inputs', children=[
                        html.Label("Tracker Axis Tilt (degrees):"),
                        dbc.Input(id="axis-tilt-input", value=20, type="number", min=0, max=90, step=1,
                                  style=input_style),
                        html.Label("Max Tracker Rotation Angle:"),
                        dbc.Input(id="max-angle-input", value=60, type="number", min=45, max=90, step=1,
                                  style=input_style),
                    ]),

                    html.Label("System Losses (%):"),
                    dbc.Input(id="losses-input", value=14, type="number", min=0, max=50, step=1, style=input_style),

                    # --- ADDED: Date picker for daily profile ---
                    html.Label("Select Day for Hourly Profile:"),
                    dcc.DatePickerSingle(
                        id='day-picker',
                        min_date_allowed=pd.to_datetime('2023-01-01'),
                        max_date_allowed=pd.to_datetime('2023-12-31'),
                        initial_visible_month=pd.to_datetime('2023-06-21'),
                        date=pd.to_datetime('2023-06-21').date(),
                        style={"width": "100%"}
                    ),

                    dbc.Button("Calculate Production", id="submit-button", color="primary", className="w-100 mt-3")
                ])
            ]),
            md=4
        ),

        # --- Output Column ---
        dbc.Col(
            dbc.Card([
                dbc.CardHeader("Predicted Results"),
                dbc.CardBody([
                    dcc.Loading(
                        id="loading-spinner",
                        type="circle",
                        children=[
                            html.H3(id="total-kwh-output", className="text-center"),
                            html.Div(id="error-output", className="text-danger text-center"),
                            dcc.Graph(id="monthly-graph"),
                            # --- ADDED: Daily graph and data store ---
                            dcc.Graph(id="daily-graph"),
                            dcc.Store(id='results-store')
                        ]
                    )
                ])
            ]),
            md=8
        )
    ])
], fluid=True)


# ==============================================================================
# DASH CALLBACKS FOR INTERACTIVITY
# ==============================================================================

# --- Callback to show/hide conditional input fields ---
@app.callback(
    Output('fixed-tilt-inputs', 'style'),
    Output('single-axis-inputs', 'style'),
    Input('tracking-input', 'value')
)
def toggle_conditional_inputs(tracking_type):
    if tracking_type == 'fixed':
        return {'display': 'block'}, {'display': 'none'}
    elif tracking_type == 'single-axis':
        return {'display': 'none'}, {'display': 'block'}
    return {'display': 'none'}, {'display': 'none'}


# --- Main callback to run the model and update the outputs ---
@app.callback(
    Output('total-kwh-output', 'children'),
    Output('monthly-graph', 'figure'),
    Output('error-output', 'children'),
    # --- ADDED: Output to data store ---
    Output('results-store', 'data'),
    Input('submit-button', 'n_clicks'),
    [State('zip-input', 'value'),
     State('capacity-input', 'value'),
     State('tracking-input', 'value'),
     State('tilt-input', 'value'), # ADDED this missing State
     State('azimuth-input', 'value'),
     State('axis-tilt-input', 'value'),
     State('max-angle-input', 'value'),
     State('losses-input', 'value')]
)
def update_results(n_clicks, zip_code, capacity, tracking, tilt, azimuth, axis_tilt, max_angle, losses):
    # Don't run the model when the app first loads
    if n_clicks is None or n_clicks == 0:
        # --- MODIFIED: Return value for the new data store output ---
        return "", {}, "", None

    try:
        # 1. Create the SystemConfig object from the form inputs
        config = SystemConfig(
            zip_code=str(zip_code),
            system_capacity_kw=float(capacity),
            module_efficiency=0.20,
            system_losses=float(losses) / 100,
            # --- MODIFIED: Use correct tilt value based on tracking type ---
            tilt_deg=float(axis_tilt) if tracking == 'single-axis' else float(tilt),
            azimuth_deg=float(azimuth),
            tracking_type=tracking,
            max_angle=float(max_angle)
        )

        # 2. Run the pvlib model
        ac_power = run_pvlib_model(config)

        # 3. Process the results for display
        total_kwh = ac_power.sum() / 1000
        monthly_kwh = ac_power.resample('ME').sum() / 1000

        # 4. Create the Plotly figure (bar chart)
        fig_monthly = go.Figure()
        fig_monthly.add_trace(go.Bar(
            x=monthly_kwh.index.strftime('%b'),
            y=monthly_kwh.values,
            name='Monthly Production'
        ))
        fig_monthly.update_layout(
            title_text='Average Monthly Energy Production',
            yaxis_title='Energy (kWh)',
            xaxis_title='Month'
        )

        # 5. Return the results to the output components
        output_text = f"Predicted Annual Generation: {total_kwh:,.0f} kWh"
        # --- MODIFIED: Serialize full results to JSON for the data store ---
        json_results = ac_power.to_json(date_format='iso', orient='split')
        return output_text, fig_monthly, "", json_results

    except Exception as e:
        # If anything goes wrong, return an error message
        error_message = f"An error occurred: {e}"
        # --- MODIFIED: Return value for the new data store output ---
        return "", {}, error_message, None

# --- ADDED: New callback to update the daily graph from stored data ---
@app.callback(
    Output('daily-graph', 'figure'),
    Input('results-store', 'data'),
    Input('day-picker', 'date')
)
def update_daily_graph(json_data, selected_date):
    # Only run if there is data in the store
    if json_data is None:
        return go.Figure().update_layout(title_text='Select a day to view its hourly profile')

    # Convert the stored JSON back to a pandas Series
    ac_power = pd.read_json(json_data, orient='split', typ='series')
    # The index is now a datetime object, so convert it to timezone-aware
    ac_power.index = pd.to_datetime(ac_power.index, utc=True)

    # Filter for the selected day
    selected_dt = pd.to_datetime(selected_date)
    daily_data = ac_power[ac_power.index.date == selected_dt.date()]

    # Create the line chart figure
    fig_daily = go.Figure()
    if daily_data.empty:
        fig_daily.update_layout(title_text=f'No production data for {selected_dt.strftime("%b %d")}')
        return fig_daily

    fig_daily.add_trace(go.Scatter(
        x=daily_data.index.hour,
        y=daily_data.values,
        mode='lines+markers',
        name='Hourly Production'
    ))
    fig_daily.update_layout(
        title_text=f'Hourly Power Production on {selected_dt.strftime("%b %d")}',
        yaxis_title='Power (W)',
        xaxis_title='Hour of the Day',
        xaxis=dict(tickmode='linear', dtick=2) # Show a tick every 2 hours
    )
    return fig_daily


# --- Run the application ---
if __name__ == '__main__':
    app.run(debug=True)