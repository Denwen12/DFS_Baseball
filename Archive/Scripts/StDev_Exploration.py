import numpy as np
import pandas as pd


path = '/Users/ryangerda/PycharmProjects/DFS_Baseball/Data/playing-2019.csv'
pl = pd.read_csv(path)
path = '/Users/ryangerda/PycharmProjects/DFS_Baseball/Data/playing-2018.csv'
pl18 = pd.read_csv(path)
pl = pd.concat([pl,pl18])

bat = pl[pl['B_PA'] >= 3]
bat = bat[['game.date','team.key','opponent.key','person.key','B_PA','B_H','B_2B','B_3B','B_HR','B_RBI','B_R','B_BB','B_SB','B_HP']]
bat['Score_B'] = ((bat['B_H']-bat['B_HR']-bat['B_3B']-bat['B_2B'])*3)+(bat['B_2B']*6)+(bat['B_3B']*9)+(bat['B_HR']*12)+(bat['B_RBI']*3.5)+(bat['B_R']*3.2)+(bat['B_BB']*3)+(bat['B_SB']*6)+(bat['B_HP']*3)
bat['Score_B_std'] = bat.groupby('person.key')['Score_B'].transform('std')
bat = bat[['person.key','Score_B_std']]
bat = bat.drop_duplicates(keep='first')

pit = pl[pl['P_GS'] == 1]
pit = pit[['game.date','team.key','opponent.key','person.key','P_GS','P_W','P_ER','P_SO','P_OUT']]
pit['P_QS'] = np.where((pit['P_OUT'] >= 18) & (pit['P_ER'] <= 3),1,0)
pit['Score_P'] = (pit['P_W'] * 6) + (pit['P_QS'] * 4) + (pit['P_ER'] * -3) + (pit['P_SO'] * 3) + (pit['P_OUT'] * 1)
pit['Score_P_std'] = pit.groupby('person.key')['Score_P'].transform('std')
pit = pit[['person.key','Score_P_std']]
pit = pit.drop_duplicates(keep='first')

writer = pd.ExcelWriter("dd.xlsx", engine='xlsxwriter')
#pl.to_excel(writer, sheet_name='output', index=False)
bat.to_excel(writer, sheet_name='bat', index=False)
pit.to_excel(writer, sheet_name='pit', index=False)
writer.save()

# BATTER
# sort where B_PA >= 3

# 3 pt single = B_H - B_2B - B_3B - B_HR
# 6pt double = B_2B
# 9pt triple = B_3B
# 12pt homer = B_HR
# 3.5 RBI B_RBI
# 3.2 runs = B_R
# 3 B_BB walk = B_BB
# 6 SB = B_SB
# 3 HBP = B_HP

# PITCHER
# sort where P_GS = 1

# 6 win = P_W
# 4 QS = if outs >= 18 & ER <= 3
# -3 ER = P_ER
# 3 SO = P_SO
# 1 OUTS = P_OUT
