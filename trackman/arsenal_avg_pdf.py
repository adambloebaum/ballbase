import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

# read in csv as dataframe
df = pd.read_csv(r'PATH TO CSV.csv', index_col=False)

# select columns
df=df[['PitchNo','Pitcher','TaggedPitchType','RelSpeed','SpinRate','InducedVertBreak', 'HorzBreak']]

# create pitch count column
pitch_count = df['PitchNo'].max()

# round values to 1 decimal
df=df.round(decimals=1)

# function to transform names
def transform_name(name):
    last, first = name.split(', ')
    return f"{first} {last}"

# apply the function
df['Pitcher'] = df['Pitcher'].apply(transform_name)

# group data into new datframe and take mean of pitch type
grouped_df=df.groupby(['Pitcher','TaggedPitchType']).mean().reset_index()

# drop column
grouped_df=grouped_df.drop('PitchNo', axis=1)

# round values to 1 decimal
grouped_df=grouped_df.round(decimals=1)

# rename columns
grouped_df.rename(columns={'TaggedPitchType': 'Pitch Type', 'RelSpeed': 'Velocity', 'InducedVertBreak': 'IVB', 'HorzBreak': 'HB'}, inplace=True)

# plotting DataFrame as a table and removing axis
fig, ax = plt.subplots(figsize=(5, 2))
ax.axis('tight')
ax.axis('off')
ax.table(cellText=grouped_df.values, colLabels=grouped_df.columns, loc='center')

# save the figure to a PDF file
pdf = PdfPages(r'PATH TO OUTPUT.pdf')
pdf.savefig(fig, bbox_inches='tight')
pdf.close()
