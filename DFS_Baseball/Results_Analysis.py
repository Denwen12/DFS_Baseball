import time
from pulp import *
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import requests
import glob
import pybaseball
import seaborn as sns
import mlbgame
import statsapi
import math
import datetime as dt

# ____________________________________________________________________________ start clock
start_time = time.time()
clock = time.strftime('%x')
clock = clock.replace("/","_")
clock2 = time.strftime('%Y-%m-%d')
yesterday = (time.time() - 86400)
yesterday = dt.datetime.fromtimestamp(yesterday)
yesterday = yesterday.strftime('%x').replace("/","_")

path = "DFS_Lineup_" + str(clock) + ".xlsx"
path = "DFS_Lineup_" + "07_31_20" + ".xlsx"
total = pd.read_excel(path, sheet_name='total_df')
slate = pd.read_excel(path, sheet_name='slate')

per = total.groupby(['Rank']).agg({'RV': "sum"})
per = per.reset_index()
per = per.sort_values('RV',ascending=False)
fd = total.groupby(['Rank']).agg({'FanDuel': "sum"})
fd = fd.reset_index()
fd = fd.sort_values('FanDuel',ascending=False)
act = total.groupby(['Rank']).agg({'max': "max"})
act = act.reset_index()
m = pd.merge(per,fd,how='left',on='Rank')
m = pd.merge(m,act,how='left',on='Rank')
bob = m.sort_values('FanDuel',ascending=False)
rob = bob[bob['max'] == 4]

vals = total['Name'].value_counts()
teams = total['Team'].value_counts()
pos = total['Pos'].value_counts()

#tot = "/Users/ryangerda/PycharmProjects/DFS_Baseball/DFS_Baseball/tot.xlsx"
#tot = pd.read_excel(tot)

res_bat = "/Users/ryangerda/PycharmProjects/DFS_Baseball/Data/batting_leaders_20200731.csv"
res_bat = pd.read_csv(res_bat)

res_pit = "/Users/ryangerda/PycharmProjects/DFS_Baseball/Data/pitching_leaders_20200731.csv"
res_pit = pd.read_csv(res_pit)


res_bat['Score'] = (res_bat['1B']*3)+(res_bat['2B']*6)+\
                     (res_bat['3B']*9)+(res_bat['HR']*12)+(res_bat['RBI']*3.5)+(res_bat['R']*3.2)+\
                     (res_bat['BB']*3)+(res_bat['SB']*6)+(res_bat['HBP']*3)
res_bat['Name'] = res_bat['Name'].str.replace(' Jr.','')

res_pit['QS'] = np.where((res_pit['IP'] >= 6) & (res_pit['ER'] <= 3), 1, 0)
res_pit['int'] = round(res_pit['IP'],0)
res_pit['dec'] = res_pit['IP'] - res_pit['int']
res_pit['out'] = (res_pit['int']*3) + (res_pit['dec']*10)
res_pit['Score'] = (res_pit['W'] * 6) + (res_pit['QS'] * 4) + (res_pit['ER'] * -3) + (res_pit['SO'] * 3) + \
                     (res_pit['out'] * 1)
res_pit['Name'] = res_pit['Name'].str.replace(' Jr.','')

b_total = total[total['Pos'] != 'P']
p_total = total[total['Pos'] == 'P']

b_total = pd.merge(b_total,res_bat[['Name','Score']],how='left',on='Name')
p_total = pd.merge(p_total,res_pit[['Name','Score']],how='left',on='Name')

score_total = pd.concat([b_total,p_total])
score_total['Score'] = np.where(score_total['Score'].isnull(),0,score_total['Score'])

#writer = pd.ExcelWriter('score.xlsx',engine='xlsxwriter')
#score_total.to_excel(writer)
#writer.save()

per = score_total.groupby(['Rank']).agg({'RV': "sum"})
per = per.reset_index()
per = per.sort_values('RV',ascending=False)
fd = score_total.groupby(['Rank']).agg({'FanDuel': "sum"})
fd = fd.reset_index()
fd = fd.sort_values('FanDuel',ascending=False)
act = score_total.groupby(['Rank']).agg({'Score': "sum"})
act = act.reset_index()
act = act.sort_values('Score',ascending=False)
m = pd.merge(per,fd,how='left',on='Rank')
m = pd.merge(m,act,how='left',on='Rank')
bob = m.sort_values('FanDuel',ascending=False)
bob.corr()

teams = score_total['Team'].unique().tolist()
teams.sort()
for t in teams:
    score_total = score_total.copy()
    score_total[str(t)] = np.where(score_total['Team'] == t, 1, 0)



#df.groupby(['Mt'], sort=False)['count'].max()
#some_df.groupby(['Rank'],sort=False)['Team'].max()
#ryan = pd.get_dummies(some_df, columns=['Team']).groupby('Rank').sum()
#ryan = ryan.reset_index()

ryan = pd.get_dummies(score_total, columns=['Team']).groupby('Rank').sum()
ryan = ryan.reset_index()
ryan = ryan[['Rank','FanDuel','Salary','RV','Score','Team_Angels', 'Team_Astros',
       'Team_Athletics', 'Team_Braves', 'Team_Cubs', 'Team_Diamondbacks',
       'Team_Dodgers', 'Team_Giants', 'Team_Indians', 'Team_Mariners',
       'Team_Mets', 'Team_Orioles', 'Team_Padres', 'Team_Pirates',
       'Team_Rangers', 'Team_Rays', 'Team_Red Sox', 'Team_Reds',
       'Team_Rockies', 'Team_Royals', 'Team_Tigers', 'Team_Twins',
       'Team_White Sox', 'Team_Yankees']]
ryan['max'] = ryan[['Team_Angels', 'Team_Astros',
       'Team_Athletics', 'Team_Braves', 'Team_Cubs', 'Team_Diamondbacks',
       'Team_Dodgers', 'Team_Giants', 'Team_Indians', 'Team_Mariners',
       'Team_Mets', 'Team_Orioles', 'Team_Padres', 'Team_Pirates',
       'Team_Rangers', 'Team_Rays', 'Team_Red Sox', 'Team_Reds',
       'Team_Rockies', 'Team_Royals', 'Team_Tigers', 'Team_Twins',
       'Team_White Sox', 'Team_Yankees']].max(axis=1).copy()
ryan.groupby(['max']).agg({'Score': "mean"})
writer = pd.ExcelWriter('score.xlsx',engine='xlsxwriter')
ryan.to_excel(writer)
writer.save()
print("--- %s minutes ---" % round((time.time() - start_time)/60,3))
