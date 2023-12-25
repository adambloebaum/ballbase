import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import pybaseball

# pull statcast data for the 2023 season

df1 = pybaseball.statcast(start_dt='2023-03-30', end_dt='2023-04-30')
df2 = pybaseball.statcast(start_dt='2023-05-01', end_dt='2023-05-31')
df3 = pybaseball.statcast(start_dt='2023-06-01', end_dt='2023-06-30')
df4 = pybaseball.statcast(start_dt='2023-07-01', end_dt='2023-07-31')
df5 = pybaseball.statcast(start_dt='2023-08-01', end_dt='2023-08-31')
df6 = pybaseball.statcast(start_dt='2023-09-01', end_dt='2023-09-30')
df7 = pybaseball.statcast(start_dt='2023-10-01', end_dt='2023-10-20')

# combine dfs and convert to csv

df = pd.concat([df1, df2, df3, df4, df5, df6, df7])
df.to_csv('2023_MLB_Season.csv')

# ensure df is sequential

df.sort_values(by=['game_pk', 'inning', 'at_bat_number', 'pitch_number'], inplace=True)

# create total runs and half inning columns

df['total_runs'] = df['bat_score'] + df['fld_score']
df['half_inning'] = df['game_pk'].astype(str) + '_' + df['inning'].astype(str) + '_' + df['inning_topbot'].astype(str)

# group by half inning and calculate max runs in half inning and runs scored

grouped_df = df.groupby('half_inning').apply(
    lambda x: x.assign(
        max_runs_in_half_inning=x['total_runs'].max(),
        runs_scored=x['total_runs'].max() - x['total_runs']))

grouped_df = grouped_df.reset_index(drop=True)

# copy grouped df

states = grouped_df.copy()

# resolve 4 ball counts mislabel

states.loc[states['balls'] == 4, 'balls'] = 3

# make runner columns binary

states['on_1b'] = np.where(states['on_1b'].isnull() | (states['on_1b'] == ''), 0, 1)
states['on_2b'] = np.where(states['on_2b'].isnull() | (states['on_2b'] == ''), 0, 1)
states['on_3b'] = np.where(states['on_3b'].isnull() | (states['on_3b'] == ''), 0, 1)

# create count, runner, and total states

states['count_state'] = states['balls'].astype(str) + '-' + states['strikes'].astype(str)
states['runner_state'] = states['on_3b'].astype(str) + states['on_2b'].astype(str) + states['on_1b'].astype(str)
states['state'] = states['count_state'].astype(str) + '_' + states['outs_when_up'].astype(str) + '_' + states['runner_state'].astype(str)

# groupby state on the mean runs scored

states.groupby('state')['runs_scored'].mean()
median_runs_scored = states.groupby('state')['runs_scored'].median()

# create pivot table

pivot_table = pd.pivot_table(states, values='runs_scored', 
                             index=['runner_state'], 
                             columns=['outs_when_up', 'count_state'], 
                             aggfunc='mean').astype(float)

# sort unique out states

unique_outs = sorted(states['outs_when_up'].unique())

# create subplots

fig, axes = plt.subplots(nrows=len(unique_outs), ncols=1, figsize=(8, 5 * len(unique_outs)))

# one subplot axis as an array safeguard

if len(unique_outs) == 1:
    axes = [axes]

# loop through out states and plot

for i, out_state in enumerate(unique_outs):
    ax = axes[i]
    sns.heatmap(pivot_table.xs(out_state, axis=1, level=0), annot=True, fmt=".2f", 
                cmap='RdBu_r', cbar=False, ax=ax, vmin=0, vmax=pivot_table.max().max())
    ax.xaxis.tick_top()
    ax.set_title(f'Expected Runs for {out_state} Outs')
    ax.set_xlabel('Count State')
    ax.set_ylabel('Runner State')

# display and save figure

plt.tight_layout()
plt.savefig('2023_MLB_Run_Exp_Matrix.png')
plt.show()

pivot_table.to_csv('2023_MLB_Run_Exp_Matrix.csv')
