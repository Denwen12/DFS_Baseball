import seaborn as sns
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import requests
import glob
import time
import lxml.html
import datetime as dt
start_time = time.time()

months = [3,4,5,6,7,8,9,10]
days = list(range(1,32))
years = [2014,2015,2016,2017,2018,2019,2020]
#years = [2018,2019,2020]

total_df = pd.DataFrame()
for y in years:
    for m in months:
        for d in days:
            time.sleep(3)
            try:
                stats_url = "http://rotoguru1.com/cgi-bin/byday.pl?game=fd&month=" + str(m) + "&day=" + str(d) + "&year=" + str(y)
                response = requests.get(stats_url).text
                s = lxml.html.fromstring(response)
                table = s.xpath('//table')[7]
                test = []
                item_list = ["^","0","1","2","3","4","5","6","7","8","9",'P','SS','OF','1B','C','2B','3B']
                for row in table.xpath('./tr'):
                     cells = row.xpath('./td//text()')
                     try:
                        pass
                        cells = [x for x in cells if x not in item_list]
                     except:
                        pass
                     test.append(cells)
                df = pd.DataFrame(test)
                df = df.rename(columns={0:'Player',1:'Points',2:'Salary',3:'Team'})
                df['Points'] = pd.to_numeric(df['Points'] ,errors='coerce')
                df = df[df['Points'].notnull()]
                df = df[['Player','Points','Salary','Team']]
                df['Salary'] = df['Salary'].str.replace(',', '')
                df['Salary'] = df['Salary'].str.replace('$', '')
                df['Salary'] = pd.to_numeric(df['Salary'],errors='coerce')
                df = df[df['Salary'].notnull()]
                date = dt.date(y,m,d)
                date = date.strftime('%x')
                df['Date'] = date
                print(y,m,d)
                total_df = total_df.append(df)
            except:
                pass


total_df['Date'] = pd.to_datetime(total_df['Date'])
writer = pd.ExcelWriter('Salary_Database_2014_2020.xlsx',engine='xlsxwriter')
total_df.to_excel(writer)
writer.save()
print("--- %s minutes ---" % round((time.time() - start_time)/60,3))