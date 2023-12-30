import os
import datetime
import matplotlib.pyplot as plt
import pandas as pd

# initialize import/export directories
import_dir = r'PATH TO CSV FILE'
export_dir = r'PATH TO SAVE LOCATION'

df = pd.read_csv(import_dir)

# condense df, groupby tagged pitch type, calculate mean pitch metrics

df_condensed = df[['TaggedPitchType', 'RelSpeed', 'InducedVertBreak', 'HorzBreak']]
df_condensed = df_condensed.dropna(subset=['TaggedPitchType'])
grouped_df = df_condensed.groupby(['TaggedPitchType']).mean()

# convert name from Last, First to First Last

def format_name(name):
    parts = name.split(", ")
    if len(parts) == 2:
        return f"{parts[1]} {parts[0]}"
    return name

pitcher_name = df.loc[0, 'Pitcher']
session_date = df.loc[0, 'Date']

formatted_name = "_".join(pitcher_name.split(", ")[::-1]).replace(" ", "_")

# convert date formats to yyyy_mm_dd format for file path

def parse_date(date_str):
    for fmt in ("%m/%d/%Y", "%m-%d-%Y", "%Y-%m-%d"):  # Add more formats if needed
        try:
            return datetime.datetime.strptime(date_str, fmt).strftime("%Y_%m_%d")
        except ValueError:
            pass
    raise ValueError(f"Date format for '{date_str}' is not supported")

formatted_date = parse_date(df.loc[0, 'Date'])

# create standard color map by pitch type for plot

pitch_types = df_condensed['TaggedPitchType'].unique()
colors = plt.cm.get_cmap('Dark2', len(pitch_types))
color_map = {pitch_type: colors(i) for i, pitch_type in enumerate(pitch_types)}

# get number of unique pitch types

unique_pitch_types = len(grouped_df['RelSpeed'].unique())

# initialize plot

fig, ax = plt.subplots(figsize=(10, 6))

# plot for each pitch type

for pitch_type in pitch_types:

    subset = df_condensed[df_condensed['TaggedPitchType'] == pitch_type]
    ax.scatter(subset['HorzBreak'], subset['InducedVertBreak'], color=color_map[pitch_type], s=50, alpha=0.25, edgecolor='none')
    
    if pitch_type in grouped_df.index:

        # plot average pitch

        avg_horz_break = grouped_df.loc[pitch_type, 'HorzBreak']
        avg_vert_break = grouped_df.loc[pitch_type, 'InducedVertBreak']
        ax.scatter(avg_horz_break, avg_vert_break, color=color_map[pitch_type], s=50, label=pitch_type, alpha=1.0)
        rounded_rel_speed = round(grouped_df.loc[pitch_type, 'RelSpeed'], 1)
        ax.text(avg_horz_break + 0.5, avg_vert_break + 0.5, f"{rounded_rel_speed}", fontsize=8, va='center')

# plot formatting

plt.xlabel('Horizontal Break (in)')
plt.ylabel('Induced Vertical Break (in)')
plt.grid(which='major', linestyle=':', linewidth='0.5', color='gray')
plt.axhline(0, color='black', linewidth=2)
plt.axvline(0, color='black', linewidth=2)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.set_xlim(-24, 24)
ax.set_ylim(-24, 24)
ax.set_title(f"{format_name(df['Pitcher'].iloc[0])} - {df['Date'].iloc[0]}", loc='left')
plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.10), ncols=unique_pitch_types, frameon=False)

# create file name using formatted name and date

file_name = f"{formatted_name}_{formatted_date}.png"

# save fig to specific directory using file name

plt.savefig(os.path.join(export_dir, file_name), bbox_inches='tight', pad_inches=0.3)