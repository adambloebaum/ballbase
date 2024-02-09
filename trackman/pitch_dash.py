import base64
import io
import dash
from dash.dependencies import Input, Output, State
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Initialize the Dash app with Bootstrap
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Initialize default figures with no data
default_fig = go.Figure()
default_fig.update_layout(
    title="",
    xaxis={'visible': False, 'showgrid': False},
    yaxis={'visible': False, 'showgrid': False},
    annotations=[{'text': "Upload data to view plot", 'x': 0.5, 'y': 0.5, 'showarrow': False, 'font': {'size': 28}}],
    paper_bgcolor='white',
    plot_bgcolor='white'
)

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Pitching Dashboard"), width=12)
    ]),
    # Row for Upload Button, Dropdown, and Filename
    dbc.Row([
        dbc.Col(dcc.Upload(
            id='upload-data',
            children=html.Button(
                'Upload File',
                id='upload-button',
                style={
                    'backgroundColor': 'blue',
                    'color': 'white',
                    'borderRadius': '5px',
                    'padding': '10px 20px',
                    'border': 'none',
                    'cursor': 'pointer',
                    'fontSize': '16px',
                    'fontWeight': 'bold',
                    'outline': 'none',
                    'boxShadow': 'none',
                    'height': '38px',
                    'lineHeight': '19px'
                }
            ),
            multiple=False,
            style={
                'textAlign': 'left',
                'display': 'inline-block',
                'marginRight': 0,
                'marginLeft': 5,
            }
        ), width={'size': 2, 'offset': 0},  style={'paddingRight': '5px', 'paddingLeft': '5px'}),

        dbc.Col(dcc.Dropdown(
            id='pitch-type-dropdown',
            options=[],
            placeholder="Select a pitch type",
            disabled=True,
            clearable=False,
            style={
                'height': '38px',
                'width': '100%',
            }
        ), width=2, style={'paddingRight': 30, 'paddingLeft': 0, 'display': 'flex', 'justifyContent': 'flex-start'}),

        dbc.Col(html.Div(
            id='file-upload-name',
            children="No file uploaded",
            style={
                'textAlign': 'left',
                'fontSize': '16px',
                'display': 'inline-block',
                'whiteSpace': 'nowrap',
                'height': '38px',  
                'lineHeight': '38px',
                'marginLeft': '15px',
            }
        ), width=7, style={'paddingLeft': 0}),
    ], align='center', style={'marginTop': '5px', 'marginBottom': '5px'}),
    
    # Row for the graphs
    dbc.Row([
        dbc.Col(dcc.Graph(id='command-plot', figure=default_fig, config={'displayModeBar': False}), width=6),
        dbc.Col(dcc.Graph(id='movement-plot', figure=default_fig, config={'displayModeBar': False}), width=6),
    ]),
], fluid=False)

# Function to parse uploaded data
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
    fig.update_traces(marker=dict(size=12))
    fig.update_xaxes(range=[-2,2], showticklabels=False, title=None)
    fig.update_yaxes(range=[-0.5,5.5], showticklabels=False, title=None)
    fig.add_shape(type='rect', x0=-0.708, y0=1.5, x1=0.708, y1=3.6, line=dict(color="black", width=1))
    fig.add_shape(type='line', x0=-0.708, y0=0.1, x1=-0.608, y1=0.21, line=dict(color="black", width=1))
    fig.add_shape(type='line', x0=-0.608, y0=0.21, x1=0, y1=0.41, line=dict(color="black", width=1))
    fig.add_shape(type='line', x0=-0, y0=0.41, x1=0.608, y1=0.21, line=dict(color="black", width=1))
    fig.add_shape(type='line', x0=0.608, y0=0.21, x1=0.708, y1=0.1, line=dict(color="black", width=1))
    fig.add_shape(type='line', x0=0.708, y0=0.1, x1=-0.708, y1=0.1, line=dict(color="black", width=1))

    fig.update_layout(
        paper_bgcolor='white',
        plot_bgcolor='white',
        width=600,
        height=700,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        )
    )
    return fig

def create_movement_plot(df):
    fig = px.scatter(df, x='HorzBreak', y='InducedVertBreak', color='TaggedPitchType')
    fig.update_traces(marker=dict(size=12))

    tickvals = list(range(-16, 17, 8))
    ticktext = [str(val) for val in tickvals]

    # Update x-axis with specified tick values and add dashed lines
    fig.update_xaxes(range=[-25, 25], tickvals=tickvals, ticktext=ticktext)
    for val in tickvals:
        fig.add_shape(type='line', x0=val, y0=-25, x1=val, y1=25, line=dict(color="grey", width=1, dash="dash"))

    # Update y-axis with specified tick values and add dashed lines
    fig.update_yaxes(range=[-25, 25], tickvals=tickvals, ticktext=ticktext)
    for val in tickvals:
        fig.add_shape(type='line', x0=-25, y0=val, x1=25, y1=val, line=dict(color="grey", width=1, dash="dash"))

    # Add the horizontal and vertical center lines
    fig.add_shape(type='line', x0=-25, y0=0, x1=25, y1=0, line=dict(color="black", width=2))
    fig.add_shape(type='line', x0=0, y0=-25, x1=0, y1=25, line=dict(color="black", width=2))

    fig.update_layout(
        paper_bgcolor='white',
        plot_bgcolor='white',
        width=800,
        height=600,
        showlegend=False
    )
    return fig

# Callback for handling the file upload and updating dropdown, filename display, and figures
@app.callback(
    [Output('movement-plot', 'figure'),
     Output('command-plot', 'figure'),
     Output('pitch-type-dropdown', 'options'),
     Output('pitch-type-dropdown', 'disabled'),
     Output('pitch-type-dropdown', 'value'),
     Output('file-upload-name', 'children')],
    [Input('upload-data', 'contents'),
     Input('pitch-type-dropdown', 'value')],
    [State('upload-data', 'filename')]
)
def update_output(contents, dropdown_value, filename):
    ctx = dash.callback_context
    
    # This checks what triggered the callback, making sure it only runs when the file is uploaded
    if not ctx.triggered or ctx.triggered[0]['prop_id'].split('.')[0] == 'upload-data':
        if contents:
            df = parse_contents(contents, filename)
            if df is not None:
                # Set the dropdown options based on the uploaded file
                pitch_options = [{'label': pitch_type, 'value': pitch_type} for pitch_type in df['TaggedPitchType'].unique()]
                pitch_options.insert(0, {'label': 'All Pitches', 'value': 'All Pitches'})
                
                # If a pitch type is already selected, filter the dataframe
                if dropdown_value != 'All Pitches':
                    df = df[df['TaggedPitchType'] == dropdown_value]
                
                # Update figures
                fig1 = create_movement_plot(df)
                fig2 = create_command_plot(df)
                
                # Return updated figures, dropdown options, enabled dropdown, current dropdown value, and filename
                return fig1, fig2, pitch_options, False, 'All Pitches', filename

    # This part runs if the dropdown value changes
    if contents and dropdown_value:
        df = parse_contents(contents, filename)
        if df is not None:
            if dropdown_value != 'All Pitches':
                df = df[df['TaggedPitchType'] == dropdown_value]
            fig1 = create_movement_plot(df)
            fig2 = create_command_plot(df)
            return fig1, fig2, dash.no_update, False, dropdown_value, dash.no_update

    # Return default figures, empty dropdown, disabled dropdown, 'All Pitches' value, and no filename
    return default_fig, default_fig, [], True, 'All Pitches', ""

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
