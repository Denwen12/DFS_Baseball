import xlsxwriter
import time
from pulp import *
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import requests
import seaborn as sns
import matplotlib.pyplot as plt

"""
#TODO: separate pitchers and batters
#TODO: get the standard deviation for each players performance
# Generate observations for each player
# strip out values less than 0
# run 10k simulations, find highest rank
# still need to figure out how to correlate team performance
# slate['new'] = np.random.normal(slate['H'], slate['H'].std()) ------# group by cleveland????? slate.groupby(['Team']).mean()
# slate['std'] = slate.groupby('Team')['H'].transform('std')

slate = slate[slate['Pos'] != 'P']
tribe = slate[slate['Team'] == 'Indians']
means = [tribe['FanDuel'].mean(), 1]
stds = [tribe['FanDuel'].std() / 3, tribe['Indians'].std() / 3]
#stds = [slate['FanDuel'].std() / 3, slate['Indians'].std() / 3]
corr = 0.5
covs = [[stds[0]**2          , stds[0]*stds[1]*corr],
        [stds[0]*stds[1]*corr,           stds[1]**2]]
m = np.random.multivariate_normal(means, covs,9)[:,0]
r4 = np.random.normal(means,covs,9)



# TODO: 2
    # sort pitchers from batters
    # pitchers get the own random
    # then batters you loop by team
    # tribe = slate[slate['Team'] == 'Indians']
    # mean is the individual players expected performance - so maybe we cant do this
    # each player gets their own std, but we can guesstimate for now
    # corr = 0.5, but tbd
    # covs = [[stds[0]**2          , stds[0]*stds[1]*corr],
#         [stds[0]*stds[1]*corr,           stds[1]**2]]
    # m = np.random.multivariate_normal(means, covs,9)[:,0]
    # then append this to the end for all the players and loop through every team


# _______________ pitchers
pitchers = slate[slate['Pos'] == 'P'].reset_index(drop=True)
pitchers['mean'] = pitchers['FanDuel']
means = [pitchers['mean'][0],1]
pitchers['std'] = abs(np.random.normal()) #placeholder
corr = 0
covs = [[pitchers['std'][0]**2          , pitchers['std'][0]*stds[1]*corr],
         [pitchers['std'][0]*stds[1]*corr,           pitchers['std'][1]**2]]
m = np.random.multivariate_normal(means,covs,len(pitchers['FanDuel']))
pitchers['test'] = np.random.multivariate_normal(pitchers['mean'],bob)




#TODO: part 3
    # using 2019 play data, calcualte new column of fanduel points earned per game
    # calculate groupby std of names to fanduel points
        # pl['std'] = pl.groupby('person.key')['B_PA'].transform('std')
        # d = pl[['person.key','std']]
        # d = d.drop_duplicates(keep='first')
    # take fangraphs data, connect names to retrosheetID
    # connect retrosheet id to calculated STDs
    # use projected average score & my STD to get random variable
        # df['RV'] = np.random.normal(loc=df['Mean'], scale=df['StdDev'])
    #compute many simulations calculating a new random variable every time
    # correlations TBD
starters = ['Max Scherzer','Johnny Cueto','Gerrit Cole','Dustin May']
import pybaseball
# _________________________________________________________ starter IDs
ids = []
for i in starters:
    first, last = str.split(i," ")
    lookup = pybaseball.playerid_lookup(last,first)
    try:
        id1 = lookup.iloc[0,2]
        ids.append(id1)
    except:
        pass

df['RV'] = np.random.normal(loc=df['Mean'], scale=df['StdDev'])

pitchers['std'] = pitchers['FanDuel'].std()
pitchers['RV'] = np.random.normal(loc=pitchers['FanDuel'],scale=pitchers['std'])

"""

import time
from pulp import *
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import requests
# ____________________________________________________________________________ start clock
start_time = time.time()
clock = time.strftime('%x')
clock2 = clock.replace("/","-")
# ____________________________________________________________________________ import fanduel data
csv = "/Users/ryangerda/PycharmProjects/DFS_Baseball/Data/FanDuel-MLB-2020-07-28-47316-players-list.csv"
fd = pd.read_csv(csv)

#slate['Name'] = slate['Name'].str.replace(' Jr.','')
csv = '/Users/ryangerda/PycharmProjects/DFS_Baseball/Data/Retrosheet_players.csv'
players = pd.read_csv(csv,',')
players = players['PLAYERID,LAST,NICKNAME,PLAY DEBUT,MGR DEBUT,COACH DEBUT,UMP DEBUT,'].str.split(',', expand=True)
players.columns = ['PLAYERID','LAST','NICKNAME','PLAY DEBUT','MGR DEBUT','COACH DEBUT','UMP DEBUT','BLANK']
del players['BLANK']
players['Name'] = players['NICKNAME'] + ' ' + players['LAST']
players['Name'] = players['Name'].str.replace(' Jr.','')

slate1 = pd.merge(slate,players[['Name','PLAYERID']],how='left',on='Name')
slate1['PLAYERID'].isnull().sum()
#slate1 = slate1[slate1['PLAYERID'].isnull()]
slate2 = pd.merge(slate1,bat,how='left',left_on='PLAYERID',right_on='person.key')
slate2 = pd.merge(slate2,pit,how='left',left_on='PLAYERID',right_on='person.key')
slate2['std'] = np.where(slate2['Pos'] == 'P',slate2['Score_P_std'],slate2['Score_B_std'])
slate2['std'] = np.where(slate2['std'].isnull(),slate2['std'].mean(),slate2['std'])
slate2['RV'] = np.random.normal(loc=slate2['FanDuel'],scale=slate2['std'])
slate2['RV'] = np.where(slate2['RV']<0,0,slate2['RV'])
writer = pd.ExcelWriter("players.xlsx", engine='xlsxwriter')
players.to_excel(writer, sheet_name='output', index=False)
writer.save()