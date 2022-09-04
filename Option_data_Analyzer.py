#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from nsepython import *
import re
import pandas as pd
import json
import winsound
import numpy as np
import seaborn as sns
sns.set_style("darkgrid")
from datetime import datetime as dt
import matplotlib.pyplot as plt
get_ipython().run_line_magic('matplotlib', 'inline')
import requests
from os import path

file_name = str(dt.now().date())+ '.csv'
file_path = "C:\\Users\\adarsh.sandhu\\Downloads\\Market Data\\Option_Open-interest based analysis\\"

while 1:
    if dt.now().strftime("%H:%M") <= '09:15':
        winsound.Beep(3000, 500)        
        print("Waiting Current Time:- "+dt.now().strftime("%H:%M"))
        time.sleep(30)
        continue
    break

while dt.now().strftime("%H:%M") <= '15:35':
    cache={}
    try:
        data=nsefetch('https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY')
        main=data['records']['data']    
        assumedUnderLyingValue = nse_fno("NIFTY")['underlyingValue']
    except:
        print("An exception occurred in fetching data")
        time.sleep(100)
        continue
    print("**************NIFTY's Current Value:- "+str(assumedUnderLyingValue)+"**************")

    with open(file_path+'main.txt', 'w') as outfile:
        json.dump(main, outfile)
    df=pd.read_json(file_path+'main.txt')
    df=df.dropna()
    df1=pd.json_normalize(df['PE'])
    df2=pd.json_normalize(df['CE'])

    latestExpiryDate = re.findall("expiryDates\':\s*\['([\w-]*)\'", str(data))[0]
    future_Date = latestExpiryDate

    df1=df1[df1['expiryDate']== future_Date]

    put1=(df1[df1['strikePrice'] >= assumedUnderLyingValue]).nsmallest(6,'strikePrice')
    put2=(df1[df1['strikePrice'] <= assumedUnderLyingValue]).nlargest(6,'strikePrice')

    putTotal=put1['changeinOpenInterest'].sum()+put2['changeinOpenInterest'].sum()

    df2=df2[df2['expiryDate']== future_Date]

    call1=(df2[df2['strikePrice'] >= assumedUnderLyingValue]).nsmallest(6,'strikePrice')
    call2=(df2[df2['strikePrice'] <= assumedUnderLyingValue]).nsmallest(6,'strikePrice')

    callTotal=call1['changeinOpenInterest'].sum()+call2['changeinOpenInterest'].sum()

    diff=callTotal-putTotal

    now = dt.now().strftime("%H:%M")
    print("*****Difference:",str(diff)+"\tSaved data at time:- "+str(now)+"*****")
    dic={now:diff}
    cache[now]=diff
    if path.exists(file_path+file_name) == False:
        temp_df = pd.DataFrame([],columns=['Time','Value'])
        temp_df.to_csv(file_path+file_name, index=False)
    temp_df = pd.read_csv(file_path+file_name)
    temp_df.loc[len(temp_df.index)]=[now,diff]
    temp_df.to_csv(file_path+file_name, index=False)
        
    plt.figure(figsize=(15, 8))
    plt.xticks(rotation=90)
    plt.plot(temp_df['Time'], temp_df['Value'])
    try:
        plt.savefig(file_path+file_name[:-4]+"PLOT.png")
        plt.close()
    except:
        print("An exception occurred in saving plot")
        continue
    winsound.Beep(2000, 500)
    time.sleep(290)


# In[ ]:




