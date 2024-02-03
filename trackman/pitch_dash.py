import dash
from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.express as px
import pandas as pd
import base64
import io

app = dash.Dash('Pitch Dash', external_stylesheets=[dbc.themes.BOOTSTRAP])

# Function to parse the uploaded data
def parse_contents(contents, filename):
    content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            df = df.round(decimals=1)
            return df
        else:
            return None
    except Exception as e:
        print(e)
        return None

# Create the command plot
def create_command_plot(df, pitch_type):
    if pitch_type and pitch_type != 'All':
        df = df[df['TaggedPitchType'] == pitch_type]

    fig = px.scatter(df, x='PlateLocSide', y='PlateLocHeight', width=400, height=500)
    fig.update_xaxes(range=[-2,2])
    fig.update_yaxes(range=[-0.5,5.5])
    fig.add_shape(type='rect', x0=-0.708, y0=1.5, x1=0.708, y1=3.6, line=dict(color="black", width=1))
    fig.add_shape(type='line', x0=-0.708, y0=0.1, x1=-0.608, y1=0.21, line=dict(color="black", width=1))
    fig.add_shape(type='line', x0=-0.608, y0=0.21, x1=0, y1=0.41, line=dict(color="black", width=1))
    fig.add_shape(type='line', x0=-0, y0=0.41, x1=0.608, y1=0.21, line=dict(color="black", width=1))
    fig.add_shape(type='line', x0=0.608, y0=0.21, x1=0.708, y1=0.1, line=dict(color="black", width=1))
    fig.add_shape(type='line', x0=0.708, y0=0.1, x1=-0.708, y1=0.1, line=dict(color="black", width=1))
    return fig

# Create the break plot
def create_break_plot(df):
    fig = px.scatter(df, x='HorzBreak', y='InducedVertBreak', color='TaggedPitchType')
    fig.update_xaxes(range=[-25,25])
    fig.update_yaxes(range=[-25,25])
    fig.add_shape(type='line', x0=-25, y0=0, x1=25, y1=0, line=dict(color="black", width=2))
    fig.add_shape(type='line', x0=0, y0=-25, x1=0, y1=25, line=dict(color="black", width=2))
    return fig

# Callback for updating the dropdown options and the plots
@app.callback(
    [Output('command_plot', 'figure'),
     Output('break_plot', 'figure'),
     Output('pitch-type-dropdown', 'options')],
    [Input('upload-data', 'contents'),
     State('upload-data', 'filename'),
     Input('pitch-type-dropdown', 'value')])
def update_output(contents, filename, pitch_type):
    if contents:
        df = parse_contents(contents[0], filename[0])
        if df is not None:
            # Create dropdown options for pitch types
            pitch_types = [{'label': 'All', 'value': 'All'}] + \
                          [{'label': p, 'value': p} for p in df['TaggedPitchType'].unique()]
            command_fig = create_command_plot(df, pitch_type)
            break_fig = create_break_plot(df)
            return command_fig, break_fig, pitch_types
    else:
        return px.scatter(), px.scatter(), []

# App layout
app.layout = dbc.Container([
    dbc.Row(
        dbc.Col(html.H1("Pitch Analysis Dashboard", className="text-center text-white"), className="mb-4 mt-4", style={'backgroundColor': 'black'}),
        style={'backgroundColor': 'black'}
    ),
    dbc.Row([
        dbc.Col(dcc.Upload(
            id='upload-data',
            children=html.Div(['Drag and Drop', html.A(' a CSV File')]),
            style={'width': '40%', 'height': '40px', 'lineHeight': '40px', 'borderWidth': '1px', 'borderStyle': 'dashed', 'borderRadius': '5px', 'textAlign': 'center', 'margin': '10px auto'},
            multiple=False
        ), className="mb-4"),
        dbc.Col(dcc.Dropdown(id='pitch-type-dropdown', value='All', clearable=False, style={'width': '50%', 'margin': '0 auto'}), className="mb-4")
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='command_plot', config={'displayModeBar': False}), width=6),
        dbc.Col(dcc.Graph(id='break_plot', config={'displayModeBar': False}), width=6)
    ])
], fluid=True)

if __name__ == '__main__':
    app.run_server(debug=True)
