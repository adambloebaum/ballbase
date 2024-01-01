import base64
import datetime
import io
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Initialize the Dash app with Bootstrap
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# App layout
app.layout = dbc.Container([
    # Row for Title and Upload
    dbc.Row([
        # Column for the Title (H1)
        dbc.Col(html.H1("Pitch Data Visualization App"), 
                width={'size': 6, 'order': 1}, 
                align='start'),  # Aligns the content to the left (start) of the column
        
        # Column for the Upload Button
        dbc.Col(dcc.Upload(
            id='upload-data',
            children=html.Button('Upload File'),
            multiple=False
        ), width={'size': 6, 'order': 2}, align='end')  # Aligns the content to the right (end) of the column
    ], justify="between"),  # Justify "between" to separate the columns

    # Row for Graphs
    dbc.Row([
        dbc.Col(dcc.Graph(id='movement-plot', config={'displayModeBar': False}), width=6),
        dbc.Col(dcc.Graph(id='location-plot', config={'displayModeBar': False}), width=6),
    ])
])




# function to parse uploaded data
def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        else:
            return html.Div([
                'Unsupported file type.'
            ])
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return df

def create_command_plot(df):
    fig = px.scatter(df, x='PlateLocSide', y='PlateLocHeight', color='TaggedPitchType', width=400, height=500)
    fig.update_xaxes(range=[-2,2])
    fig.update_yaxes(range=[-0.5,5.5])
    fig.add_shape(type='rect', x0=-0.708, y0=1.5, x1=0.708, y1=3.6, line=dict(color="black", width=1))
    fig.add_shape(type='line', x0=-0.708, y0=0.1, x1=-0.608, y1=0.21, line=dict(color="black", width=1))
    fig.add_shape(type='line', x0=-0.608, y0=0.21, x1=0, y1=0.41, line=dict(color="black", width=1))
    fig.add_shape(type='line', x0=-0, y0=0.41, x1=0.608, y1=0.21, line=dict(color="black", width=1))
    fig.add_shape(type='line', x0=0.608, y0=0.21, x1=0.708, y1=0.1, line=dict(color="black", width=1))
    fig.add_shape(type='line', x0=0.708, y0=0.1, x1=-0.708, y1=0.1, line=dict(color="black", width=1))

    fig.update_layout(
        paper_bgcolor='white',
        plot_bgcolor='white',
        width=400,
        height=500,
        showlegend=False
    )
    return fig



def create_movement_plot(df):
    fig = px.scatter(df, x='HorzBreak', y='InducedVertBreak', color='TaggedPitchType')
    fig.update_xaxes(range=[-25,25])
    fig.update_yaxes(range=[-25,25])
    fig.add_shape(type='line', x0=-25, y0=0, x1=25, y1=0, line=dict(color="black", width=2))
    fig.add_shape(type='line', x0=0, y0=-25, x1=0, y1=25, line=dict(color="black", width=2))

    fig.update_layout(
        paper_bgcolor='white',
        plot_bgcolor='white',
        width=700,
        height=500
    )

    return fig

# Callback for uploading and processing the file, then updating graphs
@app.callback(
    [Output('movement-plot', 'figure'),
     Output('location-plot', 'figure')],
    [Input('upload-data', 'contents')],
    [State('upload-data', 'filename')]
)
def update_graph(contents, filename):
    if contents:
        df = parse_contents(contents, filename)
        if df is not None:
            fig1 = create_movement_plot(df)
            fig2 = create_command_plot(df)
            
            return fig1, fig2

    # if no file has been uploaded, display empty graphs
    return {}, {}

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
