import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import dash_bootstrap_components as dbc
from dash import dash_table

# import csvs created by framing_model.py
df = pd.read_csv('2023_Catcher_Name_and_SP.csv')
sg_total = pd.read_csv('2023_Catcher_Strikes_Gained.csv')
avg_sg_marg_rel = pd.read_csv('2023_Catcher_Avg_SPG_Marg_Rel.csv')
cfr_marg = pd.read_csv('2023_Catcher_Framing_Runs_Marg.csv')

# merge the three aggregate metric dfs into one leaderboard df
leader_df = pd.merge(sg_total, avg_sg_marg_rel, on='mlb_name', how='outer')
leader_df = pd.merge(leader_df, cfr_marg, on='mlb_name', how='outer')
leader_df = leader_df[['mlb_name', 'cfr_marg', 'avg_sg_marg_rel', 'strike_prob_added_x']]
leader_df.rename(columns={'strike_prob_added_x': 'strikes_gained'}, inplace=True)

# round metrics for neatness
leader_df['avg_sg_marg_rel'] = leader_df['avg_sg_marg_rel'].round(2)
leader_df['strikes_gained'] = leader_df['strikes_gained'].round(1)
leader_df['cfr_marg'] = leader_df['cfr_marg'].round(1)

# filter only called strikes w/ <0.6 prob and balls w/ >0.4 prob
df = df[
    ((df['description'] == 'called_strike') & (df['strike_probability'] < 0.5)) |
    ((df['description'] == 'ball') & (df['strike_probability'] > 0.5))]

#initialize app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.MINTY])

# define layout
app.layout = html.Div([

    # dashboard title 
    html.H1('Catcher Framing Dashboard', style={'textAlign': 'center'}),
    
    dbc.Row([
        
        dbc.Col([
             
            # leaderboard title
            html.H4('Leaderboard: marginal pitches', style={'textAlign': 'left', 'padding-left': '10px'}),
            
            # leaderboard datatable
        
            dash_table.DataTable(
                id='leaderboard',
                columns=[
                {"name": "Catcher", "id": "mlb_name"},
                {"name": "Catcher Framing Runs", "id": "cfr_marg"},
                {"name": "Strikes Gained", "id": "strikes_gained"},
                {"name": "Strike Prob. Gained (Avg)", "id": "avg_sg_marg_rel"},
                ],
                data=leader_df.to_dict('records'),
                sort_action='native',
                style_cell={'textAlign': 'center'},
                page_size=24,
            ),
        ], width=6),

        dbc.Col([
             
            dbc.Row([
                 
                # visualizer title
                html.H4('Visualizer', style={'textAlign': 'left'}),
                
                dbc.Col([
                    
                    # catcher name dropdown
                    dcc.Dropdown(
                        id='mlb_name_dropdown',
                        options=[{'label': i, 'value': i} for i in df['mlb_name'].unique()],
                        placeholder='Select a Player',
                        multi=False,
                        style={'textAlign': 'center'}
                    ),
                ], width=3),

                dbc.Col([
                    
                    # opposing team dropown
                    dcc.Dropdown(
                        id='opponent_dropdown',
                        placeholder='Opponent',
                        multi=False,
                        style={'textAlign': 'center'}
                    ),
                ], width=2),

                dbc.Col([
                    
                    # date picker dropdown
                    dcc.DatePickerRange(
                        id='date_picker_range',
                        min_date_allowed=df['game_date'].min(),
                        max_date_allowed=df['game_date'].max(),
                        start_date=df['game_date'].min(),
                        end_date=df['game_date'].max(),
                        style={'textAlign': 'center', 'display': 'inline-block'}
                    ),
                ], width=4),
            ]),
            
            # framing plot
            dcc.Graph(
                id='sample_graph',
                    config={
                        'toImageButtonOptions': {
                                'format': 'png',
                                'filename': 'framing_plot'
                        },
                        'displayModeBar': True,
                        'modeBarButtonsToRemove': [
                            'pan2d',
                            'select2d',
                            'lasso2d',
                            'zoom2d',
                            'autoScale2d',
                            'hoverClosestCartesian',
                            'hoverCompareCartesian',
                            'toggleSpikelines'
                        ],
                        'modeBarButtonsToAdd': [
                            'zoomIn2d',
                            'zoomOut2d',
                            'resetScale2d',
                        ]
                    },
                style={'width': '80%', 'display': 'inline-block'}
            ),
        ], width=6),
    ]),
])

# callback for filtering opponent options depending on catcher name selection
@app.callback(
    Output('opponent_dropdown', 'options'),
    Input('mlb_name_dropdown', 'value')
)
def update_opponent_options(selected_mlb_name):

    # filter df for selected catcher name
    if selected_mlb_name:
        filtered_df = df[df['mlb_name'] == selected_mlb_name]
        
        # empty opponents array
        opponents = []

        # finding all teams involved in games including selected catcher name
        for i, row in filtered_df.iterrows():
            
            if row['home_team'] == selected_mlb_name:
                opponents.append(row['away_team'])

            else:
                opponents.append(row['home_team'])

        opponents = [{'label': opp, 'value': opp} for opp in set(opponents)]

        return opponents
    
    # if no catcher name selected, return no opponent options
    return []

# callback for updating the graph based on multiple dropdown selections
@app.callback(
    Output('sample_graph', 'figure'),
    [Input('mlb_name_dropdown', 'value'),
     Input('opponent_dropdown', 'value'),
     Input('date_picker_range', 'start_date'),
     Input('date_picker_range', 'end_date')]
)

def update_graph(selected_mlb_name, selected_opponent, start_date, end_date):
    filtered_df = df.copy()

    # filtering df based on selected catcher name, opponent, start and end dates
    if selected_mlb_name:
        filtered_df = filtered_df[filtered_df['mlb_name'] == selected_mlb_name]

    if selected_opponent:
                filtered_df = filtered_df[(filtered_df['away_team'] == selected_opponent) | 
                                        (filtered_df['home_team'] == selected_opponent)]

    if start_date and end_date:
        filtered_df = filtered_df[(filtered_df['game_date'] >= start_date) & 
                                  (filtered_df['game_date'] <= end_date)]
    
    # calculating strike zone average top and bottom
    sz_top_avg = filtered_df['sz_top'].mean()
    sz_bot_avg = filtered_df['sz_bot'].mean()


    # only plot rows where the selected catcher added or removed 20% or more strike probability
    plot_df = filtered_df[(filtered_df['strike_prob_added'] >= 0.2) | (filtered_df['strike_prob_added'] <= -0.2)]

    # create scatter plot
    fig = px.scatter(plot_df, x='plate_x', y='plate_z', color='strike_prob_added',
                    color_continuous_scale=[[0, 'red'], [0.5, 'white'], [1, 'green']], color_continuous_midpoint=0, range_color=[-1,1], size_max=70)

    # updating axes limits and labels
    fig.update_xaxes(range=[-2.5, 2.5], showgrid=False, zeroline=False, title_text='', ticks='', showticklabels=False)
    fig.update_yaxes(range=[-1, 4.5], showgrid=False, zeroline=False, title_text='', scaleanchor="x", scaleratio=1, ticks='', showticklabels=False)

    # set marker size
    fig.update_traces(marker=dict(size=20))

    # update layout
    fig.update_layout(
         plot_bgcolor='white',
         autosize=False,
         width=800,
         height=800
    )

    # updating the color bar
    fig.update_coloraxes(
        colorbar=dict(
            title=dict(text='Strike Prob. Added', side='right'),
            tickvals=[-1, 0, 1],
            ticktext=['-1', '0', '+1'],
            tickcolor='black',
        ),
    )

    # add strike zone patch using rect
    fig.add_shape(type="rect",
                x0=-0.71, y0=sz_bot_avg, x1=0.71, y1=sz_top_avg,
                line=dict(color="Black", width=2))

    # add home plate patch using path
    fig.add_shape(type="path",
                path="M -0.71 0.2 L -0.71 -0.12 L 0 -0.32 L 0.71 -0.12 L 0.71 0.2 Z",
                line=dict(color="Black", width=2))
    
    # construct unique title name using selected values
    title_parts = []
    
    if selected_mlb_name:
        title_parts.append(f"{selected_mlb_name}")
    
    if selected_opponent:
        title_parts.append(f"vs {selected_opponent}")
    
    if start_date or end_date:
        start_date_str = start_date if start_date else ''
        end_date_str = end_date if end_date else ''
        title_parts.append(f"{start_date_str} to {end_date_str}")

    # join the title parts with a space
    title = ' '.join(title_parts)

    # set the title
    fig.update_layout(title={'text': f'<b>{title}</b>', 'x': 0.5, 'xanchor': 'center'})

    # compute total strikes gained for specific selected values
    total_score = filtered_df['strike_prob_added'].sum().round(2)

    # create strikes gained annotation
    score_annotation = {
        'x': 0.01,
        'y': 0.01,
        'xref': 'paper',
        'yref': 'paper',
        'text': f"{total_score} strikes gained",
        'showarrow': False,
        'font': {
            'size': 20,
            'color': 'black',
        },
        'bgcolor': 'white',
        'bordercolor': 'white',
        'borderwidth': 1,
        'borderpad': 1,
    }

    # annotate the figure
    fig.add_annotation(score_annotation)

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
