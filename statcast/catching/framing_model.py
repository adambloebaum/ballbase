import xgboost as xgb
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.model_selection import train_test_split
import mysql.connector
import pybaseball
from sklearn.metrics import accuracy_score, log_loss

# pull statcast data for the 2022 season to train the model on

df1 = pybaseball.statcast(start_dt='2022-03-30', end_dt='2022-04-30')
df2 = pybaseball.statcast(start_dt='2022-05-01', end_dt='2022-05-31')
df3 = pybaseball.statcast(start_dt='2022-06-01', end_dt='2022-06-30')
df4 = pybaseball.statcast(start_dt='2022-07-01', end_dt='2022-07-31')
df5 = pybaseball.statcast(start_dt='2022-08-01', end_dt='2022-08-31')
df6 = pybaseball.statcast(start_dt='2022-09-01', end_dt='2022-09-30')
df7 = pybaseball.statcast(start_dt='2022-10-01', end_dt='2022-11-01')

# combine dfs and save as csv

df = pd.concat([df1, df2, df3, df4, df5, df6, df7])
df.to_csv('2022_MLB_Season.csv')

# convert pitcher and batter handedness columns to binary

df['p_throws'] = df['p_throws'].map({'L': 0, 'R': 1})
df['stand'] = df['stand'].map({'L': 0, 'R': 1})

# select only called balls and strikes and convert to binary

df = df[df['description'].isin(['called_strike', 'ball'])]
df['description'] = df['description'].map({'ball': 0, 'called_strike': 1})

# feature selection and data splitting

features = ['stand', 'p_throws', 'balls', 'strikes', 'plate_x', 'plate_z', 'sz_top', 'sz_bot']

# create features and targets

X = df[features]
y = df['description']

# train valid test split

X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.2, random_state=42)
X_valid, X_test, y_valid, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42)

# set up xgboost regression model

dtrain = xgb.DMatrix(X_train, label=y_train)
dvalid = xgb.DMatrix(X_valid, label=y_valid)

# identfiy parameters

params = {
    'max_depth': 6,
    'eta': 0.3,
    'objective': 'binary:logistic',
    'eval_metric': 'logloss'
}

# train model

evallist = [(dvalid, 'eval'), (dtrain, 'train')]
num_round = 50
bst = xgb.train(params, dtrain, num_round, evallist)

# predict values

y_pred_prob = bst.predict(dvalid)
y_pred = [1 if p > 0.5 else 0 for p in y_pred_prob]

# calculate validation accuracy

accuracy = accuracy_score(y_valid, y_pred)
print(f"Validation Accuracy: {accuracy * 100:.2f}%")

# calculate validation log loss

log_loss_value = log_loss(y_valid, y_pred_prob)
print(f"Validation Log Loss: {log_loss_value:.4f}")

#Validation Accuracy: 93.31%
#Validation Log Loss: 0.1559

# train on valididation and training set combined

dtrain_full = xgb.DMatrix(pd.concat([X_train, X_valid]), label=pd.concat([y_train, y_valid]))

# retrain the model

bst = xgb.train(params, dtrain_full, num_boost_round=100)

# feature importance analysis

importance = bst.get_score(importance_type='gain')

# plot feature importance

xgb.plot_importance(importance)

# save fig as png
plt.savefig('Strike_Prob_Model_Feature_Importance.png')

plt.show()

# load in current season's data

df_2023 = pd.read_csv('2023_MLB_Season.csv')

# select features

df_features = df_2023[features]

# make pitcher and hitter handedness columns binary

df_features['p_throws'] = df_features['p_throws'].map({'L': 0, 'R': 1})
df_features['stand'] = df_features['stand'].map({'L': 0, 'R': 1})

# convert df to xgboost dmatrix

d2023 = xgb.DMatrix(df_features)

# predict strike probabilities

strike_probabilities = bst.predict(d2023)

# apply strike probabilities to df

df_2023['strike_probability'] = strike_probabilities

# calculate strike probability added for each pitch

df_2023['strike_prob_added'] = np.where(df_2023['description'] == 'called_strike', 
                                            1 - df_2023['strike_probability'], 
                                            np.where(df_2023['description'] == 'ball', 
                                                     0 - df_2023['strike_probability'], 0))

df_2023.to_csv('2023_MLB_w_strike_probs.csv')

# I used mysqlconnector with a private database to pull MLB IDs, but those are publically available online as well

# theoretical df that has name and MLB ID for all active players

ids = pd.read_csv('mlb_ids.csv')

# ensure df is sequential

df_2023.sort_values(by=['game_pk', 'inning', 'at_bat_number', 'pitch_number'], inplace=True)

# pair player ids with player names

df_2023 = df_2023.merge(ids, left_on='fielder_2', right_on='mlb_id', how='left')

# resolve 4 ball count mistake

df_2023.loc[df_2023['balls'] == 4, 'balls'] = 3

# filter only called strikes and balls

df_filtered = df_2023.loc[df_2023['description'].isin(['called_strike', 'ball'])]

# groupby catcher name and get counts

pitch_counts = df_filtered.groupby('mlb_name')['mlb_name'].transform('count')

# qualified player treshold: 6 pitches per game

threshold = 6*162

# filter by threshold

df_qualified = df_filtered[pitch_counts > threshold]

# filter only called strikes w/ <0.6 prob and balls w/ >0.4 prob

df_qualified = df_qualified[
    ((df_qualified['description'] == 'called_strike') & (df_qualified['strike_probability'] < 0.5)) |
    ((df_qualified['description'] == 'ball') & (df_qualified['strike_probability'] > 0.5))]

# strikes gained per catcher over the 2023 season

sum_df = df_qualified.groupby('mlb_name')['strike_prob_added'].sum().round(2).astype(float).reset_index()
sum_df = sum_df.sort_values(by='strike_prob_added', ascending=False).round(2).reset_index()

# loop to print

for index, row in sum_df.iterrows():
    print(f"{row['mlb_name']}: {row['strike_prob_added']}")

# calculate average strike probability gained for a marginal pitch

avg_spg = df_qualified['strike_prob_added'].mean()

# groupby catcher name, calculate avg strike probability added per catcher 

mean_df = df_qualified.groupby('mlb_name')['strike_prob_added'].mean().round(4).astype(float).reset_index()

# normalize to mean

mean_df['avg_sg_marg_rel'] = mean_df['strike_prob_added'] - avg_spg

# sort from highest to lowest avg strikes gained relative to mean

mean_df = mean_df.sort_values(by='avg_sg_marg_rel', ascending=False).round(4).reset_index()

# loop to print

for index, row in mean_df.iterrows():
    print(f"{row['mlb_name']}: {row['avg_sg_marg_rel']}")

# catcher framing runs on marginal pitches per catcher over 2023

# calculate avg value of a ball and strike

called_strikes = df_2023[df_2023['description'] == 'called_strike']
called_balls = df_2023[df_2023['description'] == 'ball']

called_strike_val = called_strikes['delta_run_exp'].mean()
called_ball_val = called_balls['delta_run_exp'].mean()

# catcher framing runs on marginal pitches per catcher over 2023

df_qualified['cfr_marg'] = df_qualified.apply(lambda row: abs(row['strike_prob_added']) * called_strike_val if row['description'] == 'called_strike' else (abs(row['strike_prob_added']) * called_ball_val if row['description'] == 'ball' else None), axis=1)

cfr_marg_df = df_qualified.groupby('mlb_name')['cfr_marg'].sum().round(2).astype(float).reset_index()
cfr_marg_df = cfr_marg_df.sort_values(by='cfr_marg', ascending=True).round(2).reset_index()

# loop to print

for index, row in cfr_marg_df.iterrows():
    print(f"{row['mlb_name']}: {row['cfr_marg']}")

# save dfs

# mlb pitch data paired w/ mlb ids

df_2023.to_csv('2023_Catcher_Name_and_SP.csv')

# total strikes gained

sum_df.to_csv('2023_Catcher_Strikes_Gained.csv')

# avg strike probability gained on marginal pitches relative to the mean

mean_df.to_csv('2023_Catcher_Avg_SPG_Marg_Rel.csv')

# total catcher framing runs on marginal pitches

cfr_marg_df.to_csv('2023_Catcher_Framing_Runs_Marg.csv')
