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
# ____________________________________________________________________________ import fangraphs projections
try:
    path = "/Users/ryangerda/PycharmProjects/DFS_Baseball/DFS_Baseball/DFS_Lineup_" + str(clock) + ".xlsx"
    slate = pd.read_excel(path, sheet_name='slate')
except:
    groups = ['bat','pit']
    teams = list(range(1,31))
    master = pd.DataFrame()
    for i in teams:
        time.sleep(1)
        for g in groups:
            time.sleep(1)
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

dist = []
print('data cleaned')
total = 100000
x = 1
total_df = pd.DataFrame()
while x <= 10:
    # ____________________________________________________________________________ Define Problem
    prob = LpProblem("DFS_Lineup",LpMaximize)
    player_items = list(slate['Name'])
    points = dict(zip(player_items,slate['FanDuel']))
    cost = dict(zip(player_items,slate['Salary']))
    budget = 35000
    print('problem defined')
    # ____________________________________________________________________________ Constraints
    player_chosen = LpVariable.dicts("Player_Chosen",player_items,0,1,cat='Integer')
    prob += lpSum([points[i]*player_chosen[i] for i in player_items]), "Total Cost of Players"
    prob += lpSum([cost[f] * player_chosen[f] for f in player_items]) <= budget, "dollarMaximum"
    #prob += lpSum([points[f] * player_chosen[f] for f in player_items]) <= (total - 0.01), "pointMaximum"
    print('constraints in place')
    # ____________________________________________________________________________ maximum players per team
    teams = slate['Team'].unique().tolist()
    teams.sort()
    for t in teams:
        slate = slate.copy()
        slate[str(t)] = np.where(slate['Team'] == t,1,0)
        globals()['team_{0}'.format(t)] = dict(zip(player_items,slate[str(t)]))
        prob += lpSum([globals()['team_{0}'.format(t)][f] * player_chosen[f] for f in player_items]) <= 4, str("MaxPerTeam" + t)
    # ____________________________________________________________________________ Lineup Build
    catchers = slate[slate['Pos'] == 'C']
    catchers = catchers['Name'].to_list()
    prob += lpSum([player_chosen[p] for p in catchers]) >= 1
    prob += lpSum([player_chosen[p] for p in catchers]) <= 2

    b1 = slate[slate['Pos'] == '1B']
    b1 = b1['Name'].to_list()
    prob += lpSum([player_chosen[p] for p in b1]) >= 1
    prob += lpSum([player_chosen[p] for p in b1]) <= 2

    b2 = slate[slate['Pos'] == '2B']
    b2 = b2['Name'].to_list()
    prob += lpSum([player_chosen[p] for p in b2]) >= 1
    prob += lpSum([player_chosen[p] for p in b2]) <= 2

    b3 = slate[slate['Pos'] == '3B']
    b3 = b3['Name'].to_list()
    prob += lpSum([player_chosen[p] for p in b3]) >= 1
    prob += lpSum([player_chosen[p] for p in b3]) <= 2

    ss = slate[slate['Pos'] == 'SS']
    ss = ss['Name'].to_list()
    prob += lpSum([player_chosen[p] for p in ss]) >= 1
    prob += lpSum([player_chosen[p] for p in ss]) <= 2

    of = slate[slate['Pos'] == 'OF']
    of = of['Name'].to_list()
    prob += lpSum([player_chosen[p] for p in of]) >= 3
    prob += lpSum([player_chosen[p] for p in of]) <= 4

    util = slate[slate['Pos'] == 'UTIL']
    util = util['Name'].to_list()
    prob += lpSum([player_chosen[p] for p in util]) >= 0
    prob += lpSum([player_chosen[p] for p in util]) <= 1

    sp = slate[slate['Pos'] == 'P']
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
    output = pd.merge(df,slate,how='left',on='Name')
    output = output.append(round(output.sum(numeric_only=True),2), ignore_index=True)
    output['Rank'] = x
    x = x + 1
    print(output[['Name','Pos','Team','Game','FanDuel','Salary']])
    total = output['FanDuel'][0:9].sum()
    dist.append(total)
    total_df = total_df.append(output[0:9])
# ____________________________________________________________________________ write to excel
writer = pd.ExcelWriter("DFS_Lineup_" + str(clock) + ".xlsx", engine='xlsxwriter')
output.to_excel(writer, sheet_name='output', index=False)
slate.to_excel(writer, sheet_name='slate', index=False)
total_df.to_excel(writer, sheet_name='total_df', index=False)
writer.save()
# ____________________________________________________________________________ final
print("--- %s minutes ---" % round((time.time() - start_time)/60,3))