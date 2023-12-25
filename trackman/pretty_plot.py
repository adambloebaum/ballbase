import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# import csv as df and select columns
df=pd.read_csv('DATA_NAME.csv', index_col=False)

# group data by pitch type
grouped_df = df.groupby('TaggedPitchType').mean().reset_index()

# create a color mapping dictionary for each type
color_mapping = {'Fastball': 'orange', 'Sinker': 'brown', 'ChangeUp': 'green', 'Curveball': 'purple', 'Slider': 'blue', 'Cutter': 'red'}

# define the order of hue levels based on the color mapping dictionary
order = ['Fastball', 'Sinker', 'ChangeUp', 'Curveball', 'Slider', 'Cutter']

df['Color'] = grouped_df['TaggedPitchType'].map(color_mapping)
grouped_df['Color'] = grouped_df['TaggedPitchType'].map(color_mapping)

# create the scatter plot with colors assigned based on the 'Color' column
ax = sns.scatterplot(data=grouped_df, x='HorzBreak', y='InducedVertBreak', hue='TaggedPitchType', palette=color_mapping, hue_order=order, s=100, legend=False)

# create average pitch velocity value
for i, row in grouped_df.iterrows():
    rounded_rel_speed = round(row['RelSpeed'], 1)
    ax.text(row['HorzBreak'] + 1, row['InducedVertBreak'], f"{rounded_rel_speed}" , fontsize=8, va='center')

# set up plot
sns.scatterplot(data=df, x='HorzBreak', y='InducedVertBreak', hue='TaggedPitchType', palette=color_mapping, hue_order=order, alpha=0.15, ax=ax)
plt.xlabel('Horizontal Break (in)')
plt.ylabel('Induced Vertical Break (in)')
ax.set_title('Arsenal Plot w/ Avg Velo)', loc='left')
plt.axhline(0, color='black', linewidth=1)
plt.axvline(0, color='black', linewidth=1)
ax.legend(fontsize='small', loc='lower left')
plt.savefig(r'PATH TO OUTPUT.png')
