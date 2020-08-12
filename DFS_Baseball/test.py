from typing import Any, Union

import pybaseball
from pandas import DataFrame, Series
from pandas.io.parsers import TextFileReader

b = pybaseball.batting()
b2 = pybaseball.batting_stats_bref()
b3 = pybaseball.bwar_bat()


s = pybaseball.statcast_batter(start_dt='2020-7-31',end_dt='2020-08-01',player_id=596019)


import numpy as np
np.set_printoptions(threshold=np.inf)
r: Union[Union[TextFileReader, Series, DataFrame, None], Any] = pybaseball.retrosheet.season_game_logs(2019)
r = np.array(r.columns)

l = pybaseball.lahman.batting()

import pandas as pd
path = '/Users/ryangerda/PycharmProjects/DFS_Baseball/Data/playing-2019.csv'
p = pd.read_csv(path)
p = np.array(p.columns)

path = '/Users/ryangerda/PycharmProjects/DFS_Baseball/Data/teams-2019.csv'
t = pd.read_csv(path)
t = np.array(t.columns)

path = '/Users/ryangerda/PycharmProjects/DFS_Baseball/Data/batting-platoon-2019.csv'
toon = pd.read_csv(path)
toon = np.array(toon.columns)

path = '/Users/ryangerda/PycharmProjects/DFS_Baseball/Data/headtohead-2019.csv'
h = pd.read_csv(path)
h = np.array(h.columns)