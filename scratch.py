import xlsxwriter
import numpy as np
import pandas as pd
import time
from pulp import *


start_time = time.time()
budget = 260
batter_split = .68
pitcher_split = .32
batter = budget * batter_split
pitcher = budget * pitcher_split
#######################
#    FILE IMPORT      #
#######################
dhit = "/Users/ryangerda/PycharmProjects/NFBC_Auction_2020/Data/AuctionValue_HItter.csv"
dpitch = "/Users/ryangerda/PycharmProjects/NFBC_Auction_2020/Data/AuctionValue_Pitcher.csv"
ziphit = "/Users/ryangerda/PycharmProjects/NFBC_Auction_2020/Data/ZIPS_Hitter.csv"
zippitch = "/Users/ryangerda/PycharmProjects/NFBC_Auction_2020/Data/ZIPS_Pitcher.csv"
dhit = pd.read_csv(dhit)
dpitch = pd.read_csv(dpitch)
ziphit = pd.read_csv(ziphit)
zippitch = pd.read_csv(zippitch)
print('files imported')

#######################
#     DATA CLEAN      #
#######################
dhit = dhit[dhit['ADP'] < 600]
dhit['newPOS'] = dhit['POS'].str[:2]
dhit['newPOS'] = np.where(dhit['newPOS'] == 'C/','C',dhit['newPOS'])
dhit = dhit[dhit['newPOS'] != 'P/']
dhit = dhit.replace({'\$':''}, regex = True)
dhit[['ADP', 'PA', 'mAVG', 'mRBI', 'mR', 'mSB','mHR', 'PTS', 'aPOS', 'Dollars']] = (dhit[['ADP', 'PA', 'mAVG', 'mRBI', 'mR', 'mSB','mHR', 'PTS', 'aPOS', 'Dollars']].replace( '[\$,)]','', regex=True ).replace( '[(]','-',   regex=True ).astype(float))
dhit[['ADP', 'PA', 'mAVG', 'mRBI', 'mR', 'mSB','mHR', 'PTS', 'aPOS', 'Dollars']] = dhit[['ADP', 'PA', 'mAVG', 'mRBI', 'mR', 'mSB','mHR', 'PTS', 'aPOS', 'Dollars']].apply(pd.to_numeric, errors='coerce').fillna(0)

dpitch = dpitch[dpitch['ADP'] < 600]
dpitch = dpitch.replace({'\$':''}, regex = True)
dpitch[['ADP','IP','mW','mSV','mERA','mWHIP','mSO','PTS','aPOS', 'Dollars']] = (dpitch[['ADP','IP','mW','mSV','mERA','mWHIP','mSO','PTS','aPOS', 'Dollars']].replace( '[\$,)]','', regex=True ).replace( '[(]','-',   regex=True ).astype(float))
dpitch[['ADP','IP','mW','mSV','mERA','mWHIP','mSO','PTS','aPOS', 'Dollars']] = dpitch[['ADP','IP','mW','mSV','mERA','mWHIP','mSO','PTS','aPOS', 'Dollars']].apply(pd.to_numeric, errors='coerce').fillna(0)

print('data cleaned')


#######################
#   PROBLEM DEFINED   #
#######################
prob = LpProblem("Auction_Batter",LpMaximize)
player_items = list(dhit['PlayerName'])
costs = dict(zip(player_items,dhit['PTS']))

prob_pitch = LpProblem("Auction_Pitcher",LpMaximize)
player_items_pitch = list(dpitch['PlayerName'])
costs_pitch = dict(zip(player_items_pitch,dpitch['PTS']))

hr = dict(zip(player_items,dhit['mHR']))
rbi = dict(zip(player_items,dhit['mRBI']))
r = dict(zip(player_items,dhit['mR']))
sb = dict(zip(player_items,dhit['mSB']))
avg = dict(zip(player_items,dhit['mAVG']))
dollars = dict(zip(player_items,dhit['Dollars']))

w = dict(zip(player_items_pitch,dpitch['mW']))
sv = dict(zip(player_items_pitch,dpitch['mSV']))
era = dict(zip(player_items_pitch,dpitch['mERA']))
whip = dict(zip(player_items_pitch,dpitch['mWHIP']))
so = dict(zip(player_items_pitch,dpitch['mSO']))
ip = dict(zip(player_items_pitch,dpitch['IP']))
dollars_pitch = dict(zip(player_items_pitch,dpitch['Dollars']))
print('problem defined')


#######################
#    CONSTRAINTS      #
#######################
player_chosen = LpVariable.dicts("Batter_Chosen",player_items,0,1,cat='Integer')
prob += lpSum([costs[i]*player_chosen[i] for i in player_items]), "Total Cost of Batters"

player_chosen_pitch = LpVariable.dicts("Pitcher_Chosen",player_items_pitch,0,1,cat='Integer')
prob_pitch += lpSum([costs_pitch[i]*player_chosen_pitch[i] for i in player_items_pitch]), "Total Cost of Pitchers"

prob += lpSum([dollars[f] * player_chosen[f] for f in player_items]) <= batter, "dollarMaximum"
prob_pitch += lpSum([dollars_pitch[f] * player_chosen_pitch[f] for f in player_items_pitch]) <= pitcher, "dollarMaximum"

prob_pitch += lpSum([ip[f] * player_chosen_pitch[f] for f in player_items_pitch]) >= 1100, "IPminimum"

prob += lpSum([hr[f] * player_chosen[f] for f in player_items]) >= 0.0, "hrMinimum"
prob += lpSum([hr[f] * player_chosen[f] for f in player_items]) <= 15.0, "hrMaximum"
prob += lpSum([rbi[f] * player_chosen[f] for f in player_items]) >= 0.0, "rbiMinimum"
prob += lpSum([rbi[f] * player_chosen[f] for f in player_items]) <= 15.0, "rbiMaximum"
prob += lpSum([r[f] * player_chosen[f] for f in player_items]) >= 2.0, "rMinimum"
prob += lpSum([r[f] * player_chosen[f] for f in player_items]) <= 15.0, "rMaximum"
prob += lpSum([sb[f] * player_chosen[f] for f in player_items]) >= 0.0, "sbMinimum"
prob += lpSum([sb[f] * player_chosen[f] for f in player_items]) <= 15.0, "sbMaximum"
prob += lpSum([avg[f] * player_chosen[f] for f in player_items]) >= 0.0, "avgMinimum"
prob += lpSum([avg[f] * player_chosen[f] for f in player_items]) <= 15.0, "avgMaximum"

prob_pitch += lpSum([w[f] * player_chosen_pitch[f] for f in player_items_pitch]) >= 13.0, "wMinimum"
prob_pitch += lpSum([w[f] * player_chosen_pitch[f] for f in player_items_pitch]) <= 25.0, "wMaximum"
prob_pitch += lpSum([sv[f] * player_chosen_pitch[f] for f in player_items_pitch]) >= 0.0, "svMinimum"
prob_pitch += lpSum([sv[f] * player_chosen_pitch[f] for f in player_items_pitch]) <= 11.0, "svMaximum"
prob_pitch += lpSum([era[f] * player_chosen_pitch[f] for f in player_items_pitch]) >= -28.0, "eraMinimum"
prob_pitch += lpSum([era[f] * player_chosen_pitch[f] for f in player_items_pitch]) <= -5.0, "eraMaximum"
prob_pitch += lpSum([whip[f] * player_chosen_pitch[f] for f in player_items_pitch]) >= -16.0, "whipMinimum"
prob_pitch += lpSum([whip[f] * player_chosen_pitch[f] for f in player_items_pitch]) <= -5.0, "whipMaximum"
prob_pitch += lpSum([so[f] * player_chosen_pitch[f] for f in player_items_pitch]) >= 11.0, "soMinimum"
prob_pitch += lpSum([so[f] * player_chosen_pitch[f] for f in player_items_pitch]) <= 20.0, "soMaximum"

print('constraints in place')

#######################
#    LINEUP BUILD     #
#######################
catchers = dhit[dhit['newPOS'] == 'C']
catchers = catchers['PlayerName'].to_list()
prob += lpSum([player_chosen[p] for p in catchers]) == 2
#prob += lpSum([player_chosen[p] for p in catchers]) <= 3

b1 = dhit[dhit['newPOS'] == '1B']
b1 = b1['PlayerName'].to_list()
prob += lpSum([player_chosen[p] for p in b1]) >= 1
prob += lpSum([player_chosen[p] for p in b1]) <= 2

b2 = dhit[dhit['newPOS'] == '2B']
b2 = b2['PlayerName'].to_list()
prob += lpSum([player_chosen[p] for p in b2]) >= 1
prob += lpSum([player_chosen[p] for p in b2]) <= 2

b3 = dhit[dhit['newPOS'] == '3B']
b3 = b3['PlayerName'].to_list()
prob += lpSum([player_chosen[p] for p in b3]) >= 1
prob += lpSum([player_chosen[p] for p in b3]) <= 2

ss = dhit[dhit['newPOS'] == 'SS']
ss = ss['PlayerName'].to_list()
prob += lpSum([player_chosen[p] for p in ss]) >= 1
prob += lpSum([player_chosen[p] for p in ss]) <= 2

of = dhit[dhit['newPOS'] == 'OF']
of = of['PlayerName'].to_list()
prob += lpSum([player_chosen[p] for p in of]) >= 5
prob += lpSum([player_chosen[p] for p in of]) <= 6

dh = dhit[dhit['newPOS'] == 'DH']
dh = dh['PlayerName'].to_list()
prob += lpSum([player_chosen[p] for p in dh]) >= 0
prob += lpSum([player_chosen[p] for p in dh]) <= 1

prob += (lpSum([player_chosen[p] for p in b2]) + lpSum([player_chosen[p] for p in ss])) >= 3
prob += (lpSum([player_chosen[p] for p in b1]) + lpSum([player_chosen[p] for p in b3])) >= 3
prob += (lpSum([player_chosen[p] for p in b1]) + lpSum([player_chosen[p] for p in b3]) + lpSum([player_chosen[p] for p in b2]) + lpSum([player_chosen[p] for p in ss]) + lpSum([player_chosen[p] for p in catchers]) + lpSum([player_chosen[p] for p in of]) + lpSum([player_chosen[p] for p in dh])) ==14





pitchers_list = dpitch[dpitch['POS'].str.contains('P')]
pitchers_list = pitchers_list['PlayerName'].to_list()
prob_pitch += lpSum([player_chosen_pitch[z] for z in pitchers_list]) == 9
#prob_pitch += lpSum([player_chosen_pitch[p] for p in player_items_pitch]) <= 1



print('lineup built')


prob.writeLP("Auction_Batter.lp")
print('now generating batting lineup')
prob.solve()
print("Batting Lineup Status:", LpStatus[prob.status])
print("The optimal batting lineup consists of\n"+"-"*100)
appended_data = []
for v in prob.variables():
    if v.varValue > 0 and v.name[0]=='B':
        print(v.name, "=", v.varValue)
        y = str(v.name)
        appended_data.append(y)


prob_pitch.writeLP("Auction_Pitcher.lp")
print('now generating pitching lineup')
prob_pitch.solve()
print("Pitching Lineup Status:", LpStatus[prob_pitch.status])
print("The optimal pitching lineup consists of\n"+"-"*100)
appended_data_pitch = []
for p in prob_pitch.variables():
    if p.varValue>0 and p.name[0]=='P':
        print(p.name, "=", p.varValue)
        y = str(p.name)
        appended_data_pitch.append(y)

df = pd.DataFrame(appended_data)
df = df.replace({'Batter_Chosen_':''}, regex = True)
df = df.replace({'_':' '}, regex = True)
df.columns = ['Name']
list = df['Name'].to_list()
dhit['selected'] = dhit.PlayerName.apply(lambda sentence: any(word in sentence for word in list))
output = dhit[dhit['selected'] == True]
output = pd.merge(output,ziphit[['Name', 'G','AB', 'H','HR', 'R', 'RBI', 'SB', 'AVG', 'OBP']],how='left',left_on='PlayerName',right_on='Name')
output = output.append(round(output.sum(numeric_only=True),2), ignore_index=True)

df_pitch = pd.DataFrame(appended_data_pitch)
df_pitch = df_pitch.replace({'Pitcher_Chosen_':''}, regex = True)
df_pitch = df_pitch.replace({'_':' '}, regex = True)
df_pitch.columns = ['Name']
list_pitch = df_pitch['Name'].to_list()
dpitch['selected'] = dpitch.PlayerName.apply(lambda sentence: any(word in sentence for word in list_pitch))
output_pitch = dpitch[dpitch['selected'] == True]
output_pitch = pd.merge(output_pitch,zippitch[['Name','W','L','ERA','GS','G','IP','H','ER','HR','SO','BB','WHIP']],how='left',left_on='PlayerName',right_on='Name')
output_pitch = output_pitch.append(round(output_pitch.sum(numeric_only=True),2), ignore_index=True)




writer = pd.ExcelWriter('output.xlsx', engine='xlsxwriter')
output.to_excel(writer, sheet_name='Batters', index=False)
output_pitch.to_excel(writer, sheet_name='Pitchers', index=False)
writer.save()


print("--- %s minutes ---" % round((time.time() - start_time)/60,3))