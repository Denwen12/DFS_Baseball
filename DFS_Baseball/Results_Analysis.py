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

path = "DFS_Lineup_" + str(clock) + ".xlsx"
total = pd.read_excel(path, sheet_name='total_df')
slate = pd.read_excel(path, sheet_name='slate')

per = total.groupby(['Rank']).agg({'RV': "sum"})
per = per.reset_index()
per = per.sort_values('RV',ascending=False)
fd = total.groupby(['Rank']).agg({'FanDuel': "sum"})
fd = fd.reset_index()
fd = fd.sort_values('FanDuel',ascending=False)
m = pd.merge(per,fd,how='left',on='Rank')
bob = m.sort_values('FanDuel',ascending=False)

vals = total['Name'].value_counts()
teams = total['Team'].value_counts()
pos = total['Pos'].value_counts()

print("--- %s minutes ---" % round((time.time() - start_time)/60,3))