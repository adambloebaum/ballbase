import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.patches import Polygon

# import csv as df and select columns
df=pd.read_csv(r'PATH TO CSV.csv', index_col=False)
df=df[['PitchNo','Pitcher','TaggedPitchType','RelSpeed','SpinRate','Tilt','InducedVertBreak',
       'HorzBreak','PlateLocHeight','PlateLocSide']]

# function to transform names
def transform_name(name):
    last, first = name.split(', ')
    return f"{first} {last}"

# apply the function
df['Pitcher'] = df['Pitcher'].apply(transform_name)

# Initialize plot axis
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7, 5))

# Plotting
command_plot = sns.scatterplot(ax=ax1, x=df['PlateLocSide'], y=df['PlateLocHeight'], hue=df['TaggedPitchType'], s=25)
break_plot = sns.scatterplot(ax=ax2, x=df['HorzBreak'], y=df['InducedVertBreak'], hue=df['TaggedPitchType'], s=25)

# Plot formatting for Command Plot
ax1.set_xlim(-2, 2)
ax1.set_ylim(-0.5, 5.5)
ax1.set_aspect('equal', adjustable='box')
ax1.axis('off')  # Turn off axis for command plot

# Plot formatting for Command Plot
ax2.set_xlim(-24, 24)
ax2.set_ylim(-24, 24)
ax2.set_xticks(range(-24, 25, 8))  # Set x-axis ticks
ax2.set_yticks(range(-24, 25, 8))  # Set y-axis ticks
# Add dotted lines
for pos in [8, 16, -8, -16]:
    ax2.axhline(y=pos, color='grey', linestyle='--', linewidth=0.5)
    ax2.axvline(x=pos, color='grey', linestyle='--', linewidth=0.5)
ax2.set_aspect('equal', adjustable='box')

# Customizing ticks and labels
plt.rc('xtick', labelsize=8)
plt.rc('ytick', labelsize=8)

# Removing existing legends
ax1.get_legend().remove()
ax2.get_legend().remove()

# Setting the legend for the break plot
# Customize 'bbox_to_anchor' to adjust the position (x, y)
handles, labels = ax2.get_legend_handles_labels()
fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, 0.90), ncol=len(df['TaggedPitchType'].unique()), prop={'size': 8})

# Add patches to the command plot
ax1.add_patch(Rectangle((-0.708, 1.5), 1.416, 2.1, fill=False, edgecolor='black', lw=1))
ax1.add_patch(Polygon([[-0.708, 0.01], [-0.608, 0.21], [0, 0.41], [0.608, 0.21], [0.708, 0.01]], closed=True, fill=False))

# Add center lines to the break plot
ax2.plot((-30, 30), (0, 0), color='black', linewidth=1)
ax2.plot((0, 0), (-30, 30), color='black', linewidth=1)

# Select the first pitcher's name
pitcher_name = df['Pitcher'].iloc[0]

# Setting an overarching title
fig.suptitle(f"{pitcher_name}", fontsize=14)

# Save fig as png
plt.savefig(r'PATH TO OUTPUT.png')
