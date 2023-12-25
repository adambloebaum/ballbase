import dash
import dash_html_components as html
import dash_core_components as dcc
import plotly.express as px
from dash.dependencies import Input, Output
import pandas as pd

app = dash.Dash('Trend Finder')

#import csv as df and select columns
#insert FILENAME
df = pd.read_csv('FILENAME.csv', index_col=False)
df = df[['PitchNo','Date','Pitcher','TaggedPitchType','RelSpeed','SpinRate','Tilt','InducedVertBreak',
       'HorzBreak','PitchCall','PlateLocHeight','PlateLocSide','SpinAxis']]
df=df.round(decimals=1)

def create_line_plot():
    df_pitch = df[df['TaggedPitchType'] == 'Fastball']
    df_pitch_group = df_pitch.groupby(['Date'], as_index=False).mean()
    lineplot = px.line(data_frame=df_pitch_group, x='Date', y='RelSpeed')
    return lineplot

@app.callback(
    Output('line_plot', 'figure'),
    Input('metric_dropdown', 'value'),
    Input('pitch_dropdown', 'value'))
    #multi input?
def update_line_plot(metric, pitch):
   #make lineplot
   df_pitch = df[df['TaggedPitchType'] == pitch]
   df_pitch_group = df_pitch.groupby(['Date'], as_index=False).mean()
   lineplot = px.line(data_frame=df_pitch_group, x='Date', y=df_pitch_group[metric])
   return lineplot

app.layout = html.Div(children=[
    html.H1(children='Trend Finder'),
    
    html.Div(children=[
        html.Label(['Pitch Type']),
        dcc.RadioItems(
            id='pitch_dropdown',
            options=[
                {'label': 'Fastball', 'value': 'Fastball'},
                {'label': 'Curveball', 'value': 'Curveball'},
                {'label': 'Slider', 'value': 'Slider'},
                {'label': 'ChangeUp', 'value': 'ChangeUp'}],
            value='Fastball',
            style={'width': '50%'}
            ),
        html.Label(['Metric']),
        dcc.RadioItems(
            id='metric_dropdown',
            options=[
                {'label': 'Velocity', 'value': 'RelSpeed'},
                {'label': 'Spin Rate', 'value': 'SpinRate'},
                {'label': 'Spin Axis', 'value': 'SpinAxis'},
                {'label': 'Horizontal Break', 'value': 'HorzBreak'},
                {'label': 'Vertical Break', 'value': 'InducedVertBreak'}],
            value='RelSpeed',
            style={'width': '50%'}
            )
        ]),
    
    html.Div(children=[
        dcc.Graph(id='line_plot', figure=create_line_plot())
        ]),
    
])
    
if __name__ == '__main__': 
    app.run_server(debug=True)
