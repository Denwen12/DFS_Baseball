import pandas as pd
import numpy as np
import time
import pybaseball
from pybaseball import retrosheet
import datetime as dt
# ________________________________________________________________________________________ Constants
reg = (1 - .33)
rest = 2.3
# Home Field Advantage (number provided by FiveThirtyEight)
hfa = 24 # I previously had this number at 21. Unknown if that was a typo or fivethirtyeight model update.
# K Factor (Source:https://www.fangraphs.com/tht/elo-vs-regression-to-the-mean-a-theoretical-comparison/)
K = 4

# ________________________________________________________________________________________ Time
start_time = time.time()
time_today = time.time()
today = dt.datetime.fromtimestamp(time_today)
today = today.strftime('%x')

regSeason = []
for i in range(1903, 2020):
    year = i
    reg = retrosheet.season_game_logs(year)
    regSeason.append(reg)
    print(i)

regSeason = pd.concat(regSeason)
regSeason['Postseason'] = 0
# MLB Playoff History
ws = retrosheet.world_series_logs()
ws['Postseason'] = 4
lcs = retrosheet.lcs_logs()
lcs['Postseason'] = 3
ds = retrosheet.division_series_logs()
ds['Postseason'] = 2
wc = retrosheet.wild_card_logs()
wc['Postseason'] = 1
print('playoff history uploaded')

br_teams = ['ARI', 'ATL', 'BAL', 'BOS', 'CHW', 'CHC', 'CIN', 'CLE', 'COL',
               'DET', 'HOU', 'KCR', 'LAA', 'LAD', 'MIA', 'MIL', 'MIN', 'NYY',
               'NYM', 'OAK', 'PHI', 'PIT', 'SDP', 'SEA', 'SFG', 'STL',
               'TEX', 'TOR', 'WSN']
current = pd.DataFrame()
for t in br_teams:
    cle = pybaseball.schedule_and_record(2020,str(t))
    cle = cle[['Date','Tm','Home_Away', 'Opp','R', 'RA']]
    cle = cle[cle['Home_Away'] == 'Home']
    #cle = cle[cle['R'].notnull()]
    cle['Date'] = cle['Date'].str.replace(r"(1)",'',regex=False)
    cle['Date'] = cle['Date'].str.replace(r"(2)",'',regex=False)
    cle['Date'] = cle['Date'].str.replace(r"Sunday, ",'',regex=False)
    cle['Date'] = cle['Date'].str.replace(r"Monday, ",'',regex=False)
    cle['Date'] = cle['Date'].str.replace(r"Tuesday, ",'',regex=False)
    cle['Date'] = cle['Date'].str.replace(r"Wednesday, ",'',regex=False)
    cle['Date'] = cle['Date'].str.replace(r"Thursday, ",'',regex=False)
    cle['Date'] = cle['Date'].str.replace(r"Friday, ",'',regex=False)
    cle['Date'] = cle['Date'].str.replace(r"Saturday, ",'',regex=False)
    cle['Date'] = cle['Date'].str.strip()
    cle['Season'] = 2020
    cle['month'] = cle['Date'].apply(lambda x: x[:3])
    cle['day'] = cle['Date'].apply(lambda x: x[4:])
    cle['date'] = pd.to_datetime(cle['Season'].astype(str) + cle['month'].astype(str) + cle['day'].astype(str), format='%Y%b%d')
    cle = cle[cle['date'] <= today]
    cle['month'] = cle['date'].dt.month.map("{:02}".format)
    cle['day'] = cle['date'].dt.day.map("{:02}".format)
    cle['date_id'] = cle['Season'].astype('str') + cle['month'].astype('str') + cle['day'].astype('str')
    cle = cle[['date_id','Tm','Opp','R','RA']]
    cle = cle.rename(columns={'date_id':'date','Tm':'home_team','Opp':'visiting_team','R':'home_score','RA':'visiting_score'})
    current = current.append(cle)
    print(t)
print('added 2020 data')
# ________________________________________________________________________________________ Combine Regular and Post
mlb = pd.concat([regSeason, ws, lcs, ds, wc,current], ignore_index=True)
#mlb = mlb.sort_values(by=['date'])
mlb['date'] = mlb['date'].astype('str')
mlb = mlb.sort_values('date')

# ________________________________________________________________________________________ Abbreviations
mlb.home_team = mlb.home_team.replace(
    {'MIA': 'FLO',
     'LAA': 'ANA',
     'CAL': 'ANA'})
mlb.visiting_team = mlb.visiting_team.replace(
    {'MIA': 'FLO',
     'LAA': 'ANA',
     'CAL': 'ANA'})
print('team abbreviations have been changed as needed')

#ryan = mlb[['date','visiting_team','home_team','visiting_score','home_score']]
#TODO: home team, visiting team, home score, away score, game date
# ________________________________________________________________________________________ Create Season Variable
mlb['date'] = mlb['date'].astype('str')
mlb['date2'] = mlb['date']
mlb['season'] = mlb['date'].str[:4].astype('int')
mlb['date'] = pd.to_datetime(mlb['date'], format='%Y%m%d', errors='ignore')

# New Columns
mlb['elo_home_pre'] = 1500
mlb['elo_away_pre'] = 1500
mlb['elo_home_prob'] = 0
mlb['elo_away_prob'] = 0
mlb['elo_home_post'] = 0
mlb['elo_away_post'] = 0
mlb['home_win'] = np.where(mlb['home_score'] > mlb['visiting_score'], 1, 0)
mlb['away_win'] = np.where(mlb['home_score'] < mlb['visiting_score'], 1, 0)
mlb['tran_home'] = 0
mlb['tran_away'] = 0
mlb['home_score'] = mlb['home_score'].astype('int',errors='ignore')
mlb['visiting_score'] = mlb['visiting_score'].astype('int',errors='ignore')
mlb['uniqueID'] = mlb['date2'] + mlb['home_team'] + mlb['visiting_team'] + mlb['home_score'].map(str) + mlb['visiting_score'].map(str)
mlb['elo_home_prob'] = (1 / (10 ** (((mlb['elo_home_pre'] - hfa) - mlb['elo_away_pre']) / 400) + 1))
mlb['elo_away_prob'] = (1 / (10 ** ((mlb['elo_away_pre'] - (mlb['elo_home_pre'] - hfa)) / 400) + 1))
mlb['tran_home'] = 10 ** (mlb['elo_home_pre'] / 400)
mlb['tran_away'] = 10 ** (mlb['elo_away_pre'] / 400)
mlb['elo_home_post'] = mlb['elo_home_pre'] + K * (mlb['home_win'] - mlb['elo_home_prob'])
mlb['elo_away_post'] = mlb['elo_away_pre'] + K * (mlb['away_win'] - mlb['elo_away_prob'])
print('new columns created')

# melt
mlb = pd.melt(frame=mlb,id_vars=['date','game_num','day_of_week','visiting_team_league','visiting_game_num','home_team_league',	'home_team_game_num',
                                 'visiting_score','home_score','num_outs','day_night',	'completion_info',	'forfeit_info',	'protest_info',	'park_id',
                                 'attendance',	'time_of_game_minutes',	'visiting_line_score',	'home_line_score',	'visiting_abs',	'visiting_hits',
                                 'visiting_doubles',	'visiting_triples',	'visiting_homeruns',	'visiting_rbi',	'visiting_sac_hits',	'visiting_sac_flies',
                                 'visiting_hbp',	'visiting_bb',	'visiting_iw',	'visiting_k',	'visiting_sb',	'visiting_cs',	'visiting_gdp',	'visiting_ci',
                                 'visiting_lob',	'visiting_pitchers_used',	'visiting_individual_er',	'visiting_er',	'visiting__wp',	'visiting_balks',
                                 'visiting_po',	'visiting_assists',	'visiting_errors',	'visiting_pb',	'visiting_dp',	'visiting_tp',	'home_abs',	'home_hits',
                                 'home_doubles',	'home_triples',	'home_homeruns',	'home_rbi',	'home_sac_hits',	'home_sac_flies',	'home_hbp',	'home_bb',
                                 'home_iw',	'home_k',	'home_sb',	'home_cs',	'home_gdp',	'home_ci',	'home_lob',	'home_pitchers_used',	'home_individual_er',
                                 'home_er',	'home_wp',	'home_balks',	'home_po',	'home_assists',	'home_errors',	'home_pb',	'home_dp',	'home_tp',	'ump_home_id',
                                 'ump_home_name',	'ump_first_id',	'ump_first_name',	'ump_second_id',	'ump_second_name',	'ump_third_id',	'ump_third_name',	'ump_lf_id',
                                 'ump_lf_name',	'ump_rf_id',	'ump_rf_name',	'visiting_manager_id',	'visiting_manager_name',	'home_manager_id',	'home_manager_name',
                                 'winning_pitcher_id',	'winning_pitcher_name',	'losing_pitcher_id',	'losing_pitcher_name',	'save_pitcher_id',	'save_pitcher_name',
                                 'game_winning_rbi_id',	'game_winning_rbi_name',	'visiting_starting_pitcher_id',	'visiting_starting_pitcher_name',	'home_starting_pitcher_id',
                                 'home_starting_pitcher_name',	'visiting_1_id',	'visiting_1_name',	'visiting_1_pos',	'visiting_2_id',	'visiting_2_name',	'visiting_2_pos',
                                 'visiting_2_id.1',	'visiting_3_name',	'visiting_3_pos',	'visiting_4_id',	'visiting_4_name',	'visiting_4_pos',	'visiting_5_id',
                                 'visiting_5_name',	'visiting_5_pos',	'visiting_6_id',	'visiting_6_name',	'visiting_6_pos',	'visiting_7_id',	'visiting_7_name',
                                 'visiting_7_pos',	'visiting_8_id',	'visiting_8_name',	'visiting_8_pos',	'visiting_9_id',	'visiting_9_name',	'visiting_9_pos',
                                 'home_1_id',	'home_1_name',	'home_1_pos',	'home_2_id',	'home_2_name',	'home_2_pos',	'home_3_id',	'home_3_name',	'home_3_pos',
                                 'home_4_id',	'home_4_name',	'home_4_pos',	'home_5_id',	'home_5_name',	'home_5_pos',	'home_6_id',	'home_6_name',	'home_6_pos',
                                 'home_7_id',	'home_7_name',	'home_7_pos',	'home_8_id',	'home_8_name',	'home_8_pos',	'home_9_id',	'home_9_name',	'home_9_pos',
                                 'misc',	'acquisition_info',	'Postseason',	'date2',	'season',	'elo_home_pre',	'elo_away_pre',	'elo_home_prob',	'elo_away_prob',
                                 'elo_home_post',	'elo_away_post',	'home_win',	'away_win',	'tran_home',	'tran_away',	'uniqueID',],value_vars=['home_team','visiting_team'],var_name='outcome',value_name='team')
mlb = mlb.sort_values(by='uniqueID')
print('melted and sorted')

# find the difference
mlb['rest'] = mlb.groupby('team')['date'].diff()
mlb['rest'] = mlb.apply(lambda row: row.rest.days, axis=1)
mlb['wRest'] = np.where(mlb['rest'] > 3, 3 , mlb['rest'])
mlb.wRest.fillna(value=0, inplace=True)
print('rest calculated')

# marking whether or not "myTeam" won
mlb.loc[mlb['outcome'] == 'home_team', 'myWin'] = mlb['home_win']
mlb.loc[mlb['outcome'] == 'visiting_team', 'myWin'] = mlb['away_win']
mlb.loc[mlb['outcome'] == 'home_team', 'oppWin'] = mlb['away_win']
mlb.loc[mlb['outcome'] == 'visiting_team', 'oppWin'] = mlb['home_win']

#regmerge
mlb['oppTeam1'] = 'NA'
mlb['oppTeam2'] = 'NA'
mlb['oppTeam'] = 'NA'
mlb['oppRest1'] = 'NA'
mlb['oppRest2'] = 'NA'
mlb['oppRest'] = 'NA'
for i in range(-2, 2,1):
    rows = i
    mlb['oppTeam1'] = np.where(mlb.uniqueID == mlb.uniqueID.shift(rows), mlb.team.shift(rows),mlb['oppTeam1'])
    mlb['oppRest1'] = np.where(mlb.uniqueID == mlb.uniqueID.shift(rows), mlb.wRest.shift(rows), mlb['oppRest1'])
for i in range(2, -2,-1):
    rows = i
    mlb['oppTeam2'] = np.where(mlb.uniqueID == mlb.uniqueID.shift(rows), mlb.team.shift(rows),mlb['oppTeam2'])
    mlb['oppRest2'] = np.where(mlb.uniqueID == mlb.uniqueID.shift(rows), mlb.wRest.shift(rows), mlb['oppRest2'])

mlb['oppTeam'] = np.where(mlb.team == mlb.oppTeam2, mlb.oppTeam1, mlb.oppTeam2)
mlb['oppRest'] = np.where(mlb.team == mlb.oppTeam2, mlb.oppRest1, mlb.oppRest2)
print('opponent info locked in')

# Calculating Pregame ELO based on the end result Postgame ELO of the team's last game
mlb['myPregameElo'] = 1500
mlb['oppPregameElo'] = 1500
mlb['myPostgameElo'] = 1500
mlb['oppPostgameElo'] = 1500
hjkgkhgkjhg
for i in range(1000, 0,-1):
    rows = i
    print(i)
    #mlb['lgs'] = np.where(mlb.groupby('team').cumcount() > 0, mlb.groupby('team').season.shift(), mlb['season'])
    mlb['lgsh'] = mlb.groupby('team').season.shift()
    mlb['lgsh'] = np.where(mlb['lgsh'].isnull(),1111,mlb['lgsh'])
    mlb['lgsv'] = mlb.groupby('oppTeam').season.shift()
    mlb['lgsv'] = np.where(mlb['lgsv'].isnull(), 1111, mlb['lgsv'])
    mlb['newSeasonh'] = np.where(mlb['lgsh'] < mlb['season'], 'new', 'pie')
    mlb['newSeasonv'] = np.where(mlb['lgsv'] < mlb['season'], 'new', 'pie')
    mlb['myPregameElo'] = np.where(mlb.groupby('team').cumcount() > 0, mlb.groupby('team').myPostgameElo.shift(),1500)
    mlb['oppPregameElo'] = np.where(mlb.groupby('oppTeam').cumcount() > 0, mlb.groupby('oppTeam').oppPostgameElo.shift(), 1500)
    mlb['myPregameElo'] = np.where(mlb['newSeasonh'] == 'new',np.where(mlb['myPregameElo'] < 1500,1500 - (1500 - mlb['myPregameElo']) * .66 ,(mlb['myPregameElo'] - 1500) * .66 + 1500),mlb['myPregameElo'])
    mlb['oppPregameElo'] = np.where(mlb['newSeasonv'] == 'new',np.where(mlb['oppPregameElo'] < 1500,1500 - (1500 - mlb['oppPregameElo']) * .66 ,(mlb['oppPregameElo'] - 1500) * .66 + 1500),mlb['oppPregameElo'])
    mlb['myAdjElo'] = np.where(mlb['outcome'] == 'home_team', mlb['myPregameElo'] + hfa + (mlb['wRest'] * rest), mlb['myPregameElo'] + (mlb['wRest'] * rest))
    mlb['oppAdjElo'] = np.where(mlb['outcome'] == 'visiting_team', mlb['oppPregameElo'] + hfa + (mlb['oppRest'] * rest), mlb['oppPregameElo'] + (mlb['oppRest'] * rest))
    mlb['myProbElo'] = (1 / (10 ** ((mlb['oppAdjElo'] - mlb['myAdjElo']) / 400) + 1))
    mlb['oppProbElo'] = (1 / (10 ** ((mlb['myAdjElo'] - mlb['oppAdjElo']) / 400) + 1))
    mlb['myPostgameElo'] = mlb['myPregameElo'] + K * (mlb['myWin'] - mlb['myProbElo'])
    mlb['oppPostgameElo'] = mlb['oppPregameElo'] + K * (mlb['oppWin'] - mlb['oppProbElo'])
print('elo claculated')

#Odds
#mlb['oddsID'] = mlb['date2'] + mlb['team']
#odds = pd.read_excel('/Users/ryangerda/PycharmProjects/Ehlo/odds10_17.xlsx')
#odds = pd.DataFrame(odds)
##mlb = pd.merge(left=mlb, right=odds, left_on='oddsID', right_on='oddsID', how='left')
#print('odds inserted')


#Limiting columns one more time
mlb = mlb[
    ['uniqueID','date','team','oppTeam','oppRest','myPregameElo',
     'oppPregameElo','myPostgameElo','oppPostgameElo','lgsh','lgsv','myAdjElo','oppAdjElo','myProbElo','oppProbElo']]

print('limited columns one more time')

# PRINT OUTPUT
print(mlb.dtypes)
writer = pd.ExcelWriter('Ehlo_2020-08-10.xlsx', engine='xlsxwriter')
mlb.to_excel(writer, sheet_name='Ehlo', index=False)
writer.save()
print('excel file created')

print("--- %s minutes ---" % round((time.time() - start_time)/60,3))