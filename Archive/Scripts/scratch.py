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
        master = master.append(data)
        print(i)


