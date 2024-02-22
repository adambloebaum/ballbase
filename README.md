# baseball

dashboards, models, pipelines, and visualizations using mlb statcast and trackman baseball data

## batch

### trackman pull & viz

batch job scripts to pull trackman csv files from filezilla using winscp into a local directory before generating visualizations to another local directory

## statcast

### catching

an xgboost model for predicted strike probability used to 'score' catcher framing performance. trained on 2022 mlb data and applied to 2023 mlb data. calculated rankings for qualified catchers includes strikes gained, marginal framing runs gained, and average relative marginal strike probability gained. an interactive dashboard for visualizing these rankings and specific player performances using catcher, date, and opposing team filters

### run expectancy

the run expectancy matrix for the 2023 mlb season for every runner/count/out situation

## trackman

### pitch dash

an interactive dashboard for visualizing user-uploaded trackman pitching csv files. dropdown capabilities to filter for specific pitch types on the command and movement plots

### pretty plot

script for generating high-quality arsenal visualizations of trackman pitching csv files. auto-generating filename for player name and session date

### pitch report

script for generating a basic command and movement visualization from trackman pitching csv files

### arsenal pdf

script for generating a pdf table of arsenal average mtrics from trackman pitching csv files