# baseball

### Table of Contents

- [Batch](#batch)
- [Statcast](#statcast)
- [TrackMan](#trackman)

## Batch

This system consists of scripts and configurations to automate the pulling and visualization of baseball data from TrackMan. It uses batch scripts for data retrieval and a Python script for data visualization.

### System Overview

The system includes:
- `trackman_pull.bat` and `trackman_pull.txt`: Scripts for automating the download of TrackMan baseball data.
- `trackman_viz.bat` and `trackman_viz.py`: Scripts for visualizing the downloaded data.

### Installation

1. Ensure Python and necessary libraries (`matplotlib`, `pandas`) are installed.
2. Place the `.bat` and `.txt` scripts in an appropriate directory on your system.
3. Update the scripts with relevant paths and credentials.

### Usage

- To pull data from TrackMan:
  Run `trackman_pull.bat` with necessary parameters.
- To visualize the data:
  Run `trackman_viz.bat` after the data pull is complete.

### Files Description

##### trackman_pull.txt

- This script is used for SFTP connection to TrackMan's server to download data.
- It contains commands for batch aborting, turning off confirmations, opening an SFTP session, changing directories, and downloading files.

  ```txt
  option batch abort
  option confirm off
  open sftp://[USERNAME]:[PASSWORD]@ftp.trackmanbaseball.com:[PORT]
  cd /practice/[parameters]
  lcd [local path]
  get *
  exit
  ```

#### trackman_viz.py

This Python script performs data visualization for the TrackMan baseball data. It includes the following key functionalities:

- **Date Calculation**:
  ```python
  today = datetime.date.today()
  yesterday = today - datetime.timedelta(days=1)
  date_str = yesterday.strftime("%Y-%m-%d")
  ```
  Calculates yesterday's date to target the specific dataset for visualization.

- **Directory Path Setup**:
  ```python
  data_dir = f"**PATH TO DATA FOLDER**\\{date_str}"
  viz_dir = f"**PATH TO VIZ FOLDER**\\{date_str}-Viz"
  ```
  Sets up the directory paths for data storage and visualization output, using the calculated date.

- **Data Directory Check**:
  ```python
  if os.path.exists(data_dir) and any(fname.endswith('.csv') for fname in os.listdir(data_dir)):
      # Proceed with visualization
  ```
  Checks if the data directory exists and contains CSV files, which are necessary for the visualization process.

- **Data Processing**:
  The script iterates through CSV files in a specified data directory:
  ```python
  for filename in os.listdir(data_dir):
      if filename.endswith(".csv"):
          data_path = os.path.join(data_dir, filename)
          df = pd.read_csv(data_path)
          # ... additional processing ...
  ```
  It reads each CSV file into a Pandas DataFrame for analysis.

- **Data Condensation and Grouping**:
  ```python
  df_condensed = df[['TaggedPitchType', 'RelSpeed', 'InducedVertBreak', 'HorzBreak']]
  df_condensed = df_condensed.dropna(subset=['TaggedPitchType'])
  grouped_df = df_condensed.groupby(['TaggedPitchType']).mean()
  ```
  The script condenses the DataFrame to focus on key metrics like pitch type, release speed, and break, then groups by pitch type to calculate average metrics.

- **Visualization Setup**:
  ```python
  pitch_types = df_condensed['TaggedPitchType'].unique()
  colors = plt.cm.get_cmap('Dark2', len(pitch_types))
  color_map = {pitch_type: colors(i) for i, pitch_type in enumerate(pitch_types)}
  fig, ax = plt.subplots(figsize=(10, 6))
  ```
  Sets up a color map for different pitch types and initializes the plot.

- **Scatter Plot Creation**:
  ```python
  for pitch_type in pitch_types:
      subset = df_condensed[df_condensed['TaggedPitchType'] == pitch_type]
      ax.scatter(subset['HorzBreak'], subset['InducedVertBreak'], color=color_map[pitch_type], ...)
      # ... plotting average pitches ...
  ```
  Creates scatter plots for each pitch type, representing their horizontal and vertical breaks.

- **Plot Formatting and Saving**:
  ```python
  plt.xlabel('Horizontal Break (in)')
  plt.ylabel('Induced Vertical Break (in)')
  # ... additional formatting ...
  file_name = f"{formatted_name}_{formatted_date}.png"
  plt.savefig(os.path.join(viz_dir, file_name), ...)
  ```
  Adds labels, formatting to the plot, and saves the visualizations as PNG files in the specified directory.

## Statcast

This suite of Python scripts and dashboards is designed for advanced baseball analytics with Statcast data, focusing on catcher framing and run expectancy for the 2023 MLB season. It includes a model for evaluating catcher framing, an interactive dashboard for visualizing the results, and a script for analyzing run expectancy.

### System Overview

The system includes:
- `framing_model.py`: Builds an XGBoost model to analyze catcher framing.
- `framing_dash.py`: A Dash-based dashboard for visualizing catcher framing data.
- `run_exp_matrix.py`: Script for calculating the run expectancy matrix for every game situation for the 2023 MLB season.

### Installation

1. Ensure Python and necessary libraries (xgboost, pandas, matplotlib, seaborn, pybaseball, dash, etc.) are installed.
2. Place the scripts in an appropriate directory on your system.

### Usage

- **Catcher Framing Model**:
  Run `framing_model.py` to train the XGBoost model on catcher framing data and calculate framing value statistics.
- **Catcher Framing Dashboard**:
  Execute `framing_dash.py` to launch the `Plotly` dashboard for visualizing framing data.
- **Run Expectancy Matrix**:
  Use `run_exp_matrix.py` to calculate and visualize the run expectancy matrix for the 2023 MLB season.

### Files Description

#### framing_model.py

- **Data Preparation**:
  ```python
  # Pull statcast data for the 2022 season to train the model on
  df = pd.concat([df1, df2, df3, df4, df5, df6, df7])
  df.to_csv('2022_MLB_Season.csv')
  ```

- **Data Processing**:
  ```python
  # Convert pitcher and batter handedness columns to binary
  df['p_throws'] = df['p_throws'].map({'L': 0, 'R': 1})
  df['stand'] = df['stand'].map({'L': 0, 'R': 1})

  # Select only called balls and strikes and convert to binary
  df = df[df['description'].isin(['called_strike', 'ball'])]
  df['description'] = df['description'].map({'ball': 0, 'called_strike': 1})
  ```

- **Feature Selection and Model Training**:
  ```python
  # Feature selection and data splitting
  X = df[features]
  y = df['description']
  ```

- **Train Valid Test Split**:
  ```python
  X_train, X_valid, y_train, y_valid = train_test_split(X, y, test_size=0.2, random_state=42)
  ```

- **Set Up XGBoost Regression Model**:
  ```python
  bst = xgb.train(params, dtrain, num_round, evallist)
  ```

- **Model Evaluation**:
  ```python
  # Predict values and calculate validation accuracy and log loss
  y_pred_prob = bst.predict(dvalid)
  accuracy = accuracy_score(y_valid, y_pred)
  log_loss_value = log_loss(y_valid, y_pred_prob)
  ```

- **Feature Importance Analysis**:
  ```python
  # Feature importance analysis and plot
  importance = bst.get_score(importance_type='gain')
  xgb.plot_importance(importance)
  ```

#### framing_dash.py

- **Data Import and Processing**:
  ```python
  # Import CSVs created by framing_model.py and merge dataframes
  df = pd.read_csv('2023_Catcher_Name_and_SP.csv')
  leader_df = pd.merge(sg_total, avg_sg_marg_rel, on='mlb_name', how='outer')
  ```

- **Dashboard Initialization**:
  ```python
  # Initialize Dash app and define layout
  app = dash.Dash(__name__, external_stylesheets=[dbc.themes.MINTY])
  app.layout = html.Div([
      html.H1('Catcher Framing Dashboard', style={'textAlign': 'center'}),
      ...
  ])
  ```

- **Data Visualization Components**:
  ```python
  # Framing plot component
  dcc.Graph(id='sample_graph', config={...}, style={'width': '80%', 'display': 'inline-block'})
  ```

- **Callbacks and Dynamic Updates**:
  ```python
  # Callbacks for filtering and updating graph based on selections
  @app.callback(
      Output('sample_graph', 'figure'),
      [Input('mlb_name_dropdown', 'value'), Input('opponent_dropdown', 'value'), ...]
  )
  def update_graph(...):
      ...
  ```

#### run_exp_matrix.py

- **Data Preparation**:
  ```python
  # Pull statcast data for the 2023 season and combine into a single dataframe
  df = pd.concat([df1, df2, df3, df4, df5, df6, df7])
  df.to_csv('2023_MLB_Season.csv')
  ```

- **Creating Total Runs and Half Inning Columns**:
  ```python
  # Create total runs and half inning columns for analysis
  df['total_runs'] = df['bat_score'] + df['fld_score']
  df['half_inning'] = df['game_pk'].astype(str) + '_' + df['inning'].astype(str) + '_' + df['inning_topbot'].astype(str)
  ```

- **Group By and Calculate Runs Scored**:
  ```python
  # Group by half inning and calculate max runs in half inning and runs scored
  grouped_df = df.groupby('half_inning').apply(...)
  ```

- **Pivot Table Creation and Visualization**:
  ```python
  # Create pivot table for the run expectancy matrix
  pivot_table = pd.pivot_table(states, values='runs_scored', index=['runner_state'], columns=['outs_when_up', 'count_state'], aggfunc='mean')

- **Subplots Creation and Heatmap Plotting**:
  ```python
  fig, axes = plt.subplots(...)
  ...
  ```

## TrackMan

This project consists of a suite of Python scripts designed for analyzing and visualizing TrackMan baseball pitching data. Each script serves a unique role in processing the data, generating reports, and creating interactive dashboards.

### System Overview

The system includes:
- `arsenal_pdf.py`: Generates PDF reports of pitch data.
- `pitch_dash.py`: Creates an interactive dashboard for pitch data analysis.
- `pitch_report.py`: Produces pitch ball flight metric reports.
- `pretty_plot.py`: Creates visually appealing plots for pitch data.

### Installation

1. Ensure Python and necessary libraries (pandas, matplotlib, seaborn, Dash, Plotly) are installed.
2. Download the scripts to your local machine.
3. Update paths to CSV files and export locations within each script as necessary.

### Usage

- Run `arsenal_pdf.py` to generate PDF reports of pitch data.
- Execute `pitch_dash.py` to launch an interactive dashboard.
- Use `pitch_report.py` for detailed pitch analysis.
- Run `pretty_plot.py` to create polished visualizations of the data.

### Scripts Description

#### arsenal_pdf.py

`arsenal_pdf.py` generates PDF reports of pitch data, focusing on essential metrics like pitch type, velocity, spin rate, and break.

- **Data Import and Preparation**:
  ```python
  df = pd.read_csv(r'PATH TO CSV.csv', index_col=False)
  df = df[['PitchNo', 'Pitcher', 'TaggedPitchType', 'RelSpeed', 'SpinRate', 'InducedVertBreak', 'HorzBreak']]
  ```

- **Data Transformation and Grouping**:
  ```python
  grouped_df = df.groupby(['Pitcher', 'TaggedPitchType']).mean().reset_index()
  grouped_df = grouped_df.drop('PitchNo', axis=1)
  ```

- **Plotting DataFrame as a Table**:
  ```python
  fig, ax = plt.subplots(figsize=(5, 2))
  ax.axis('off')
  ax.table(cellText=grouped_df.values, colLabels=grouped_df.columns, loc='center')
  ```

- **Saving Figure to PDF**:
  ```python
  pdf = PdfPages(r'PATH TO OUTPUT.pdf')
  pdf.savefig(fig, bbox_inches='tight')
  pdf.close()
  ```

#### pitch_dash.py

`pitch_dash.py` creates an interactive dashboard for pitch data analysis using Dash and Plotly.

- **App Initialization and Layout Definition**:
  ```python
  app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
  app.layout = html.Div([...])
  ```

- **Data Visualization Components**:
  ```python
  dcc.Graph(id='sample_graph', ...)
  ```

- **Callback for Updating Dashboard**:
  ```python
  @app.callback(...)
  def update_output(contents, dropdown_value, filename):
      ...
  ```

- **Graph Creation and Formatting**:
  ```python
  fig = px.scatter(df, x='...', y='...', color='TaggedPitchType', ...)
  ```

#### pitch_report.py

`pitch_report.py` produces comprehensive reports on pitching data, with detailed visualizations.

- **Data Import and Selection**:
  ```python
  df = pd.read_csv(r'PATH TO CSV.csv', index_col=False)
  ```

- **Plotting Command and Break Plots**:
  ```python
  command_plot = sns.scatterplot(ax=ax1, x='PlateLocSide', y='PlateLocHeight', hue='TaggedPitchType', s=25)
  break_plot = sns.scatterplot(ax=ax2, x='HorzBreak', y='InducedVertBreak', hue='TaggedPitchType', s=25)
  ```

- **Customizing Ticks, Labels, and Legends**:
  ```python
  plt.rc('xtick', labelsize=8)
  plt.rc('ytick', labelsize=8)
  fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, 0.90), ncol=len(df['TaggedPitchType'].unique()), prop={'size': 8})
  ```

- **Adding Patches and Center Lines**:
  ```python
  ax1.add_patch(Rectangle((-0.708, 1.5), 1.416, 2.1, fill=False, edgecolor='black', lw=1))
  ax2.plot((-30, 30), (0, 0), color='black', linewidth=1)
  ```

#### pretty_plot.py

`pretty_plot.py` creates visually appealing plots of pitch data, highlighting key pitch metrics.

- **Data Grouping and Aggregation**:
  ```python
  grouped_df = df_condensed.groupby(['TaggedPitchType']).mean()
  ```

- **Name and Date Formatting**:
  ```python
  def format_name(name):
      parts = name.split(", ")
      return f"{parts[1]} {parts[0]}"
  def parse_date(date_str):
      return datetime.datetime.strptime(date_str, fmt).strftime("%Y_%m_%d")
  ```

- **Plot Initialization and Scatter Plotting**:
  ```python
  fig, ax = plt.subplots(figsize=(10, 6))
  ax.scatter(subset['HorzBreak'], subset['InducedVertBreak'], ...)
  ```

- **Plot Formatting and Legend Customization**:
  ```python
  plt.xlabel('Horizontal Break (in)')
  plt.ylabel('Induced Vertical Break (in)')
  plt.legend(loc='upper center', ...)
  ```
