import dash
import dash_html_components as html
import dash_core_components as dcc
import plotly.express as px
from dash.dependencies import Input, Output
import pandas as pd
import dash_table as dt

app = dash.Dash('Pitch Hub')

#import csv as df and select columns
#include filename
df = pd.read_csv('FILENAME.csv', index_col=False)
df = df[['PitchNo','Pitcher','TaggedPitchType','RelSpeed','SpinRate','Tilt','InducedVertBreak',
       'HorzBreak','PitchCall','PlateLocHeight','PlateLocSide','Date','SpinAxis']]
df=df.round(decimals=1)

#copy df into abbreviated version
df_short = df[['PitchNo', 'TaggedPitchType', 'RelSpeed', 'SpinRate', 'Tilt', 'InducedVertBreak', 'HorzBreak']]

def create_command_plot():
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

@app.callback(
    Output('command_plot', 'figure'),
    Input('dropdown','value'))
def update_command_plot(value):
    new_df = df[df['TaggedPitchType'] == value]
    fig = px.scatter(new_df, x='PlateLocSide', y='PlateLocHeight', width=400, height=500)
    fig.update_xaxes(range=[-2,2])
    fig.update_yaxes(range=[-0.5,5.5])
    fig.add_shape(type='rect', x0=-0.708, y0=1.5, x1=0.708, y1=3.6, line=dict(color="black", width=1))
    fig.add_shape(type='line', x0=-0.708, y0=0.1, x1=-0.608, y1=0.21, line=dict(color="black", width=1))
    fig.add_shape(type='line', x0=-0.608, y0=0.21, x1=0, y1=0.41, line=dict(color="black", width=1))
    fig.add_shape(type='line', x0=-0, y0=0.41, x1=0.608, y1=0.21, line=dict(color="black", width=1))
    fig.add_shape(type='line', x0=0.608, y0=0.21, x1=0.708, y1=0.1, line=dict(color="black", width=1))
    fig.add_shape(type='line', x0=0.708, y0=0.1, x1=-0.708, y1=0.1, line=dict(color="black", width=1))
    return fig

def create_break_plot():
    fig = px.scatter(df, x='HorzBreak', y='InducedVertBreak', color='TaggedPitchType')
    fig.update_xaxes(range=[-25,25])
    fig.update_yaxes(range=[-25,25])
    fig.add_shape(type='line', x0=-25, y0=0, x1=25, y1=0, line=dict(color="black", width=2))
    fig.add_shape(type='line', x0=0, y0=-25, x1=0, y1=25, line=dict(color="black", width=2))
    return fig

def create_pie_chart():
    piechart = px.pie(data_frame=df, names='PitchCall', hole=0.3)
    return piechart

@app.callback(
    Output('pie_chart', 'figure'),
    Input('pie_dropdown', 'value'))
def update_pie_chart(value):
    new_df = df[df['TaggedPitchType'] == value]
    piechart = px.pie(data_frame=new_df, names='PitchCall', hole=0.3)
    return piechart

def create_polar_chart():
    polarchart = px.scatter_polar(data_frame=df, r='RelSpeed', theta='SpinAxis', color='TaggedPitchType', start_angle=270, range_r=(65,95))
    return polarchart

def create_box_plot():
    boxplot = px.box(data_frame=df, x='TaggedPitchType', y='RelSpeed', color='TaggedPitchType')
    return boxplot

@app.callback(
    Output('box_plot', 'figure'),
    Input('box_dropdown', 'value'))
def update_box_plot(value):
    boxplot = px.box(data_frame=df, x='TaggedPitchType', y=df[value], color='TaggedPitchType')
    return boxplot

app.layout = html.Div(children=[
    html.H1(children='Pitching Hub'),
    
    html.Label(children='Pitch Type'),
    dcc.Dropdown(
        id='dropdown',
        options=[
            {'label': 'Fastball', 'value': 'Fastball'},
            {'label': 'Curveball', 'value': 'Curveball'},
            {'label': 'Slider', 'value': 'Slider'},
            {'label': 'ChangeUp', 'value': 'ChangeUp'}
        ],
        value='Fastball',
        multi=False,
        clearable=False,
        style={'width': '50%'}
    ),
    
    html.Div(children=[
        dcc.Graph(
            id='command_plot', figure=create_command_plot(), style={'display': 'inline-block'}),
        dcc.Graph(
            id='break_plot', figure=create_break_plot(), style={'display': 'inline-block'})]),
    
    html.Div(children=[
        html.Label(['Result Type']),
        dcc.Dropdown(
            id='pie_dropdown',
            options=[
                {'label': 'Fastball', 'value': 'Fastball'},
                {'label': 'Curveball', 'value': 'Curveball'},
                {'label': 'Slider', 'value': 'Slider'},
                {'label': 'ChangeUp', 'value': 'ChangeUp'}
            ],
            value='Fastball',
            multi=False,
            clearable=False,
            style={'width': '50%'}
        ),
    ]),

    html.Div(children=[
        dcc.Graph(id='pie_chart', figure=create_pie_chart(), style={'display': 'inline-block', 'width': '48%'}),
        dcc.Graph(id='polar_chart', figure=create_polar_chart(), style={'display': 'inline-block', 'width': '48%'})
        ]),
    
    html.Div(children=[
        html.Label(['Metric']),
        dcc.Dropdown(
            id='box_dropdown',
            options=[
                {'label': 'Velocity', 'value': 'RelSpeed'},
                {'label': 'Spin Rate', 'value': 'SpinRate'}],
            value='RelSpeed',
            multi=False,
            clearable=False,
            style={'width': '50%'}
            ),
        ]),
    
    html.Div(children=[
        dcc.Graph(id='box_plot', figure=create_box_plot())
        ]),
    
    dt.DataTable(
        id='data_table',
        columns=[{'name': i, 'id': i} for i in df_short.columns],
        data=df_short.to_dict('records'),
        editable=True,
        filter_action='native',
        sort_action='native',
        sort_mode='single',
        row_deletable=False,
        page_action='native',
        page_current=0,
        page_size=10)
])
    
if __name__ == '__main__': 
    app.run_server(debug=True)
