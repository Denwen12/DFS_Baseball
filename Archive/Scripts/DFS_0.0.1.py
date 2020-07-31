import xlsxwriter
import time
from pulp import *
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import requests

start_time = time.time()
groups = ['bat','pit']
teams = list(range(1,31))
master = pd.DataFrame()
for i in teams:
    for g in groups:
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



csv = "/Users/ryangerda/PycharmProjects/DFS_Baseball/Data/FanDuel-MLB-2020-07-25-47218-players-list.csv"
fd = pd.read_csv(csv)
master = pd.merge(master,fd[['Nickname','Salary','Injury Indicator']],how='left',left_on='Name',right_on='Nickname')

slate = master[master['Salary'].notna()]
print('data cleaned')
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
print('constraints in place')

#######################
#    LINEUP BUILD     #
#######################
catchers = slate[slate['Pos'] == 'C']
catchers = catchers['Name'].to_list()
prob += lpSum([player_chosen[p] for p in catchers]) == 1

b1 = slate[slate['Pos'] == '1B']
b1 = b1['Name'].to_list()
prob += lpSum([player_chosen[p] for p in b1]) == 1

b2 = slate[slate['Pos'] == '2B']
b2 = b2['Name'].to_list()
prob += lpSum([player_chosen[p] for p in b2]) == 1

b3 = slate[slate['Pos'] == '3B']
b3 = b3['Name'].to_list()
prob += lpSum([player_chosen[p] for p in b3]) == 1

ss = slate[slate['Pos'] == 'SS']
ss = ss['Name'].to_list()
prob += lpSum([player_chosen[p] for p in ss]) == 1

of = slate[slate['Pos'] == 'OF']
of = of['Name'].to_list()
prob += lpSum([player_chosen[p] for p in of]) == 3

util = slate[slate['Pos'] == 'UTIL']
util = util['Name'].to_list()
prob += lpSum([player_chosen[p] for p in util]) == 0

sp = slate[slate['Pos'] == 'P']
sp = sp['Name'].to_list()
prob += lpSum([player_chosen[p] for p in sp]) == 1

prob += (lpSum([player_chosen[p] for p in sp]) + lpSum([player_chosen[p] for p in util]) + lpSum([player_chosen[p] for p in of]) + lpSum([player_chosen[p] for p in ss]) + lpSum([player_chosen[p] for p in b3]) + lpSum([player_chosen[p] for p in b2]) + lpSum([player_chosen[p] for p in b1]) + lpSum([player_chosen[p] for p in catchers])) == 9
print('lineup built')


prob.writeLP("DFS_Lineup.lp")
print('now generating batting lineup')
prob.solve()
print("Lineup Status:", LpStatus[prob.status])
print("The optimal lineup consists of\n"+"-"*100)
appended_data = []
for v in prob.variables():
    if v.varValue > 0 and v.name[0]=='P':
        print(v.name, "=", v.varValue)
        y = str(v.name)
        appended_data.append(y)

df = pd.DataFrame(appended_data)
df = df.replace({'Player_Chosen_':''}, regex = True)
df = df.replace({'_':' '}, regex = True)
df.columns = ['Name']
#list = df['Name'].to_list()
#slate['selected'] = slate.Name.apply(lambda sentence: any(word in sentence for word in list))
#output = slate[slate['selected'] == True]
output = pd.merge(df,slate,how='left',on='Name')
output = output.append(round(output.sum(numeric_only=True),2), ignore_index=True)



writer = pd.ExcelWriter('optimization.xlsx', engine='xlsxwriter')
output.to_excel(writer, sheet_name='output', index=False)
master.to_excel(writer, sheet_name='master', index=False)
slate.to_excel(writer, sheet_name='slate', index=False)
fd.to_excel(writer, sheet_name='Fanduel', index=False)
writer.save()


print("--- %s minutes ---" % round((time.time() - start_time)/60,3))