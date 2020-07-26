import xlsxwriter
import time
from pulp import *
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import requests
import seaborn as sns
import matplotlib.pyplot as plt

xx = np.array(slate['FanDuel'])
yy = np.array(slate['Indians'])
means = [xx.mean(), yy.mean()]
stds = [xx.std() / 3, yy.std() / 3]
corr = 0.8
covs = [[stds[0]**2          , stds[0]*stds[1]*corr],
        [stds[0]*stds[1]*corr,           stds[1]**2]]
m = np.random.multivariate_normal(means, covs, 1000)


mean = (0, 0)
cov = [[1, .5], [.5, 1]]
x = np.random.multivariate_normal(mean, cov, 10000)



avg = slate['FanDuel'].mean()
std_dev = slate['FanDuel'].std()
num_reps = 500
num_simulations = 1000
pct_to_target = np.random.normal(avg, std_dev, num_reps).round(2)

all_stats = []

# Loop through many simulations
for i in range(num_simulations):
    # Choose random inputs for the sales targets and percent to target
    sales_target = np.random.choice(slate['FanDuel'], num_reps)
    pct_to_target = np.random.normal(avg, std_dev, num_reps)
    # Build the dataframe based on the inputs and number of reps
    df = pd.DataFrame(index=range(num_reps), data={'Pct_To_Target': pct_to_target,
                                                   'Sales_Target': sales_target})
    # Back into the sales number using the percent to target rate
    df['Sales'] = df['Pct_To_Target'] * df['Sales_Target']
    # We want to track sales,commission amounts and sales targets over all the simulations
    all_stats.append([df['Sales'].sum().round(0),
                      df['Sales_Target'].sum().round(0)])


#TODO: separate pitchers and batters
#TODO: get the standard deviation for each players performance
# Generate observations for each player
# strip out values less than 0
# run 10k simulations, find highest rank
# still need to figure out how to correlate team performance
# slate['new'] = np.random.normal(slate['H'], slate['H'].std()) ------# group by cleveland????? slate.groupby(['Team']).mean()
# slate['std'] = slate.groupby('Team')['H'].transform('std')