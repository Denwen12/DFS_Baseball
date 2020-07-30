import time
from pulp import *
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import requests
import glob
import pybaseball

# ____________________________________________________________________________ start clock
start_time = time.time()
clock = time.strftime('%x')
clock = clock.replace("/","_")
clock2 = time.strftime('%Y-%m-%d')
# ____________________________________________________________________________ import fanduel data
csv = glob.glob('/Users/ryangerda/PycharmProjects/DFS_Baseball/Data/FanDuel-MLB-' + str(clock2) + '*.csv')
fd = pd.read_csv(csv[0])
# ____________________________________________________________________________ import player event data '18 & '19
path = '/Users/ryangerda/PycharmProjects/DFS_Baseball/Data/playing-2019.csv'
pl = pd.read_csv(path)
path = '/Users/ryangerda/PycharmProjects/DFS_Baseball/Data/playing-2018.csv'
pl18 = pd.read_csv(path)
pl = pd.concat([pl,pl18])
# ____________________________________________________________________________ import retrosheet player ids
csv = '/Users/ryangerda/PycharmProjects/DFS_Baseball/Data/Retrosheet_players.csv'
players = pd.read_csv(csv,',')
players = players['PLAYERID,LAST,NICKNAME,PLAY DEBUT,MGR DEBUT,COACH DEBUT,UMP DEBUT,'].str.split(',', expand=True)
players.columns = ['PLAYERID','LAST','NICKNAME','PLAY DEBUT','MGR DEBUT','COACH DEBUT','UMP DEBUT','BLANK']
del players['BLANK']
players['Name'] = players['NICKNAME'] + ' ' + players['LAST']
players['Name'] = players['Name'].str.replace(' Jr.','')
# ____________________________________________________________________________ import fangraphs projections
try:
    path = "/Users/ryangerda/PycharmProjects/DFS_Baseball/DFS_Baseball/DFS_Lineup_" + str(clock) + ".xlsx"
    slate2 = pd.read_excel(path, sheet_name='slate')
except:
    groups = ['bat','pit']
    teams = list(range(1,31))
    master = pd.DataFrame()
    for i in teams:
        time.sleep(3)
        for g in groups:
            time.sleep(3)
            data = []
            headings = None
            stats_url = "https://www.fangraphs.com/dailyprojections.aspx?pos=all&stats=" + str(g) + "&type=sabersim&team=" + str(i) + "&lg=all&players=0"
            response = requests.get(stats_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            try:
                table = soup.find_all('table', {'class': 'rgMasterTable'})[0]
                if headings is None:
                    headings = [row.text.strip() for row in table.find_all('th')[0:]]
                rows = table.find_all('tr')
                for row in rows:
                    cols = row.find_all('td')
                    cols = [ele.text.strip() for ele in cols]
                    cols = [col.replace('*', '').replace('#', '') for col in cols]  # Removes '*' and '#' from some names
                    cols = [col for col in cols if
                            'Totals' not in col and 'NL teams' not in col and 'AL teams' not in col]  # Removes Team Totals and other rows
                    data.append([ele for ele in cols[0:]])
                data = pd.DataFrame(data=data, columns=headings)  # [:-5]  # -5 to remove Team Totals and other rows
                data = data.dropna()  # Removes Row of All Nones
                if g == 'bat':
                    data = data[data['Pos'] != 'P']
                master = master.append(data)
                print(i)
            except:
                pass
    master['Pos'] = np.where(master['Pos'].isna(),'P',master['Pos'])
    master['Pos'] = np.where(master['Pos'].isin(['LF','RF','CF']),'OF',master['Pos'])
    master['Pos'] = np.where(master['Pos'] == 'DH','UTIL',master['Pos'])
    master[['PA', 'H', '1B', '2B', '3B', 'HR', 'R','RBI', 'SB', 'CS',
        'BB', 'SO', 'Yahoo', 'FanDuel', 'DraftKings', 'W','IP', 'TBF']] = master[['PA', 'H', '1B', '2B', '3B', 'HR', 'R',
                                                                                  'RBI', 'SB', 'CS','BB', 'SO', 'Yahoo', 'FanDuel', 'DraftKings', 'W','IP', 'TBF']].apply(pd.to_numeric)
    master['Name'] = np.where(master['Name'] == 'Nicholas Castellanos','Nick Castellanos',master['Name'])
    master['Name'] = np.where(master['Name'] == 'Cedric Mullins II','Cedric Mullins',master['Name'])
    master = pd.merge(master,fd[['Nickname','Salary','Injury Indicator']],how='left',left_on='Name',right_on='Nickname')
    slate = master[master['Salary'].notna()]
    slate['Name'] = slate['Name'].str.replace(' Jr.', '')
    # ____________________________________________________________________________ clean player event data
    bat = pl[pl['B_PA'] >= 3]
    bat = bat[['game.date','team.key','opponent.key','person.key','B_PA','B_H','B_2B','B_3B','B_HR','B_RBI','B_R','B_BB','B_SB','B_HP']]
    bat['Score_B'] = ((bat['B_H']-bat['B_HR']-bat['B_3B']-bat['B_2B'])*3)+(bat['B_2B']*6)+(bat['B_3B']*9)+(bat['B_HR']*12)+(bat['B_RBI']*3.5)+(bat['B_R']*3.2)+(bat['B_BB']*3)+(bat['B_SB']*6)+(bat['B_HP']*3)
    bat['Score_B_std'] = bat.groupby('person.key')['Score_B'].transform('std')
    bat = bat[['person.key','Score_B_std']]
    bat = bat.drop_duplicates(keep='first')
    pit = pl[pl['P_OUT'] >= 4]
    pit = pit[['game.date','team.key','opponent.key','person.key','P_GS','P_W','P_ER','P_SO','P_OUT']]
    pit['P_QS'] = np.where((pit['P_OUT'] >= 18) & (pit['P_ER'] <= 3),1,0)
    pit['Score_P'] = (pit['P_W'] * 6) + (pit['P_QS'] * 4) + (pit['P_ER'] * -3) + (pit['P_SO'] * 3) + (pit['P_OUT'] * 1)
    pit['Score_P_std'] = pit.groupby('person.key')['Score_P'].transform('std')
    pit = pit[['person.key','Score_P_std']]
    pit = pit.drop_duplicates(keep='first')
    # ____________________________________________________________________________ Import STDs
    slate1 = pd.merge(slate,players[['Name','PLAYERID']],how='left',on='Name')
    slate2 = pd.merge(slate1,bat,how='left',left_on='PLAYERID',right_on='person.key')
    slate2['count_bat'] = slate2.groupby('Name')['Name'].transform('count')
    slate2 = slate2.drop(slate2[(slate2['person.key'].isnull()) & (slate2['Pos'] != 'P') & (slate2['count_bat'] > 1)].index)
    slate2 = pd.merge(slate2,pit,how='left',left_on='PLAYERID',right_on='person.key')
    slate2['count_pit'] = slate2.groupby('Name')['Name'].transform('count')
    slate2 = slate2.drop(slate2[(slate2['person.key_y'].isnull()) & (slate2['Pos'] == 'P') & (slate2['count_pit'] > 1)].index)
    slate2['std'] = np.where(slate2['Pos'] == 'P',slate2['Score_P_std'],slate2['Score_B_std'])
    slate2['std'] = np.where(slate2['std'].isnull(),slate2['std'].mean(),slate2['std'])

# ____________________
dist = []
print('data cleaned')
total = 100000
x = 1
total_df = pd.DataFrame()
while x <= 5000:
    # ____________________________________________________________________________ Create Random Outcomes
    slate3 = slate2.copy()
    slate3['RV'] = np.random.normal(loc=slate3['FanDuel'], scale=slate3['std'])
    slate3['RV'] = np.where(slate3['RV'] < 0, 0, slate3['RV'])
    slate3['RV'] = np.where((slate3['Pos'] == 'P')&(slate3['FanDuel'] < 10), 0, slate3['RV'])
    # ____________________________________________________________________________ Define Problem
    prob = LpProblem("DFS_Lineup",LpMaximize)
    player_items = list(slate3['Name'])
    points = dict(zip(player_items,slate3['RV']))
    cost = dict(zip(player_items,slate3['Salary']))
    budget = 35000
    print('problem defined')
    # ____________________________________________________________________________ Constraints
    player_chosen = LpVariable.dicts("Player_Chosen",player_items,0,1,cat='Integer')
    prob += lpSum([points[i]*player_chosen[i] for i in player_items]), "Total Cost of Players"
    prob += lpSum([cost[f] * player_chosen[f] for f in player_items]) <= budget, "dollarMaximum"
    print('constraints in place')
    # ____________________________________________________________________________ maximum players per team
    teams = slate3['Team'].unique().tolist()
    teams.sort()
    for t in teams:
        slate3 = slate3.copy()
        slate3[str(t)] = np.where(slate3['Team'] == t, 1, 0)
        globals()['team_{0}'.format(t)] = dict(zip(player_items, slate3[str(t)]))
        prob += lpSum([globals()['team_{0}'.format(t)][f] * player_chosen[f] for f in player_items]) <= 4, str("MaxPerTeam" + t)
    # ____________________________________________________________________________ Lineup Build
    catchers = slate3[slate3['Pos'] == 'C']
    catchers = catchers['Name'].to_list()
    prob += lpSum([player_chosen[p] for p in catchers]) >= 1
    prob += lpSum([player_chosen[p] for p in catchers]) <= 2

    b1 = slate3[slate3['Pos'] == '1B']
    b1 = b1['Name'].to_list()
    prob += lpSum([player_chosen[p] for p in b1]) >= 1
    prob += lpSum([player_chosen[p] for p in b1]) <= 2

    b2 = slate3[slate3['Pos'] == '2B']
    b2 = b2['Name'].to_list()
    prob += lpSum([player_chosen[p] for p in b2]) >= 1
    prob += lpSum([player_chosen[p] for p in b2]) <= 2

    b3 = slate3[slate3['Pos'] == '3B']
    b3 = b3['Name'].to_list()
    prob += lpSum([player_chosen[p] for p in b3]) >= 1
    prob += lpSum([player_chosen[p] for p in b3]) <= 2

    ss = slate3[slate3['Pos'] == 'SS']
    ss = ss['Name'].to_list()
    prob += lpSum([player_chosen[p] for p in ss]) >= 1
    prob += lpSum([player_chosen[p] for p in ss]) <= 2

    of = slate3[slate3['Pos'] == 'OF']
    of = of['Name'].to_list()
    prob += lpSum([player_chosen[p] for p in of]) >= 3
    prob += lpSum([player_chosen[p] for p in of]) <= 4

    util = slate3[slate3['Pos'] == 'UTIL']
    util = util['Name'].to_list()
    prob += lpSum([player_chosen[p] for p in util]) >= 0
    prob += lpSum([player_chosen[p] for p in util]) <= 1

    sp = slate3[slate3['Pos'] == 'P']
    sp = sp['Name'].to_list()
    prob += lpSum([player_chosen[p] for p in sp]) == 1

    prob += (lpSum([player_chosen[p] for p in catchers]) + lpSum([player_chosen[p] for p in b1])) >= 1
    prob += (lpSum([player_chosen[p] for p in catchers]) + lpSum([player_chosen[p] for p in b1])) <= 2
    prob += (lpSum([player_chosen[p] for p in sp]) + lpSum([player_chosen[p] for p in util]) + lpSum([player_chosen[p] for p in of]) + lpSum([player_chosen[p] for p in ss]) + lpSum([player_chosen[p] for p in b3]) + lpSum([player_chosen[p] for p in b2]) + lpSum([player_chosen[p] for p in b1]) + lpSum([player_chosen[p] for p in catchers])) == 9
    print('lineup built')
    # ____________________________________________________________________________ Optimize Lineup
    prob.writeLP("DFS_Lineup.lp")
    print('now generating batting lineup')
    prob.solve()
    print("Lineup Status:", LpStatus[prob.status])
    print("The optimal lineup consists of\n"+"-"*100)
    appended_data = []
    for v in prob.variables():
        if v.varValue != None:
            if v.varValue > 0 and v.name[0] == 'P':
                y = str(v.name)
                appended_data.append(y)
    # ____________________________________________________________________________ Create Output
    df = pd.DataFrame(appended_data)
    df = df.replace({'Player_Chosen_':''}, regex = True)
    df = df.replace({'_':' '}, regex = True)
    df.columns = ['Name']
    output = pd.merge(df,slate3,how='left',on='Name')
    output = output.append(round(output.sum(numeric_only=True),2), ignore_index=True)
    output['Rank'] = x
    x = x + 1
    print(output[['Name','Pos','Team','Game','RV','Salary','FanDuel']])
    total = output['RV'][0:9].sum()
    dist.append(round(total))
    total_df = total_df.append(output[0:9])
# ____________________________________________________________________________ write to excel
some_df = total_df[['Name', 'Team', 'Game', 'Pos', 'PA', 'H', '1B', '2B', '3B', 'HR', 'R',
       'RBI', 'SB', 'CS', 'BB', 'SO', 'FanDuel', 'W','IP', 'TBF', 'Nickname', 'Salary', 'Injury Indicator', 'PLAYERID', 'std', 'RV','Rank']]
writer = pd.ExcelWriter("DFS_Lineup_" + str(clock) + ".xlsx", engine='xlsxwriter')
output.to_excel(writer, sheet_name='output', index=False)
slate2.to_excel(writer, sheet_name='slate', index=False)
some_df.to_excel(writer, sheet_name='total_df', index=False)
writer.save()
# ____________________________________________________________________________ final
print("--- %s minutes ---" % round((time.time() - start_time)/60,3))