import time
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import requests
import glob
import pybaseball
import seaborn as sns
import mlbgame
import math
import datetime as dt

# ____________________________________________________________________________ start clock
start_time = time.time()
yesterday = (time.time() - 86400)
yesterday = dt.datetime.fromtimestamp(yesterday)
yesterday = yesterday.strftime('%x').replace("/","_")

#path = "DFS_Lineup_" + str(yesterday) + ".xlsx"
path = "/Users/ryangerda/PycharmProjects/DFS_Baseball/Archive/Data/DFS_Lineup_" + "07_31_20" + ".xlsx"
total = pd.read_excel(path, sheet_name='total_df')
slate = pd.read_excel(path, sheet_name='slate')

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

dummy = score_total[['Rank','Team']]
ryan = pd.get_dummies(dummy, columns=['Team']).groupby('Rank').sum()
ryan['max'] = ryan.max(axis=1)
ryan = ryan.reset_index()
score_total = pd.merge(score_total,ryan[['Rank','max']],how='left',on='Rank')

per = score_total.groupby(['Rank']).agg({'RV': "sum"})
per = per.reset_index()
per = per.sort_values('RV',ascending=False)
fd = score_total.groupby(['Rank']).agg({'FanDuel': "sum"})
fd = fd.reset_index()
fd = fd.sort_values('FanDuel',ascending=False)
act = score_total.groupby(['Rank']).agg({'Score': "sum"})
act = act.reset_index()
act = act.sort_values('Score',ascending=False)
ax = score_total.groupby(['Rank']).agg({'max': "max"})
ax = ax.reset_index()
m = pd.merge(per,fd,how='left',on='Rank')
m = pd.merge(m,act,how='left',on='Rank')
m = pd.merge(m,ax,how='left',on='Rank')
bob = m.sort_values('Score',ascending=False)
bob.corr()
bob.groupby(['max']).agg({'Score': "mean"})

rob = m[m['max'] == 4]

score_total['Date'] = '2020-7-31'
score_total['Date'] = pd.to_datetime(score_total['Date'])


path = '/Users/ryangerda/jupyter/Ehlo_2020-08-12.xlsx'
ehlo = pd.read_excel(path)
ehlo['year'] = ehlo['date'].dt.year
ehlo['month'] = ehlo['date'].dt.month
ehlo['day'] = ehlo['date'].dt.day
ehlo = ehlo[ehlo['month'] == 9]
ehlo = ehlo[ehlo['day'].isin(['28','29','30'])]
simp = ehlo[['team','year','myPregameElo']]
simp = simp.groupby(['team','year']).agg({'myPregameElo':'mean'})
simp = simp.reset_index()

simp = simp.drop_duplicates(keep='first')
date = ehlo[ehlo['date'] == '7/31/2020']

score_total['Team'] = score_total.Team.replace({'Angels':'ANA',
                                                'Athletics':'OAK',
                                                'Red Sox':'BOS',
                                                'Rays':'TBR',
                                                'Reds':'CIN',
                                                'Royals':'KCR',
                                                'Indians':'CLE',
                                                'Cubs':'CHC',
                                                'Rockies':'COL',
                                                'Diamondbacks':'ARI',
                                                'White Sox':'CHW',
                                                'Tigers':'DET',
                                                'Giants':'SFG',
                                                'Astros':'HOU',
                                                'Padres':'SDP',
                                                'Dodgers':'LAD',
                                                'Brewers':'MIL',
                                                'Twins':'MIN',
                                                'Nationals':'WAS',
                                                'Mets':'NYM',
                                                'Yankees':'NYY',
                                                'Braves':'ATL',
                                                'Phillies':'PHI',
                                                'Orioles':'BAL',
                                                'Cardinals':'STL',
                                                'Pirates':'PIT',
                                                'Mariners':'SEA',
                                                'Rangers':'TEX',
                                                'Blue Jays':'TOR',
                                                'Marlins':'FLO'})

ok = pd.merge(score_total,date,left_on='Team',right_on='team',how='left')
final = ok[['FanDuel','Salary','std', 'RV','Score','max','myPregameElo', 'oppPregameElo']]


import pybaseball
import pandas as pd


pybaseball.bwar_pitch()

pitch = pybaseball.bwar_pitch()
bat = pybaseball.bwar_bat()
batg = bat.groupby(['team_ID','year_ID']).agg({'WAR':'sum'})
batg = batg.reset_index()
batg['team_ID'] = batg['team_ID'].replace({'MIA':'FLO','WSN':'WAS'})

writer = pd.ExcelWriter('war.xlsx', engine='xlsxwriter')
pitch.to_excel(writer,sheet_name='pitch')
bat.to_excel(writer,sheet_name='bat')
writer.save()


merged = pd.merge(batg,simp,left_on=['team_ID','year_ID'],right_on=['team','year'],how='left')
merged = merged[merged['year'] >= 1993]
correlate = merged[['WAR','myPregameElo']]
correlate['new'] = correlate['myPregameElo'] - 1465.6
correlate['Ehlo_per_war'] = correlate['new']/correlate['WAR']


writer = pd.ExcelWriter('cor.xlsx', engine='xlsxwriter')
correlate.to_excel(writer,sheet_name='pitch')
writer.save()