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
today = clock.replace("/","_")

path = "DFS_Lineup_" + str(today) + ".xlsx"
total = pd.read_excel(path, sheet_name='total_df')
slate = pd.read_excel(path, sheet_name='slate')
