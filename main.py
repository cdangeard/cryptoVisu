# -*- coding: utf-8 -*-
"""
Created on Mon Jul  8 18:34:18 2019

@author: Drimer
"""
#IMPORTS
import datetime as dt
import pandas as pd
import requests
import json
import numpy as np
from time import sleep
#from binance.client import Client

#Definitions de Fonctions
def movingaverage(values,window):
  weigths = np.repeat(1.0, window)/window
  smas = np.convolve(values, weigths, 'valid')
  return smas

def get_bars(symbol, interval = '1m'):
   url = root_url + '?symbol=' + symbol + '&interval=' + interval
   data = json.loads(requests.get(url).text)
   df = pd.DataFrame(data)
   df.columns = ['open_time',
             'o', 'h', 'l', 'c', 'v',
             'close_time', 'qav', 'num_trades',
             'taker_base_vol', 'taker_quote_vol', 'ignore']
   df.index = [dt.datetime.fromtimestamp(x/1000.0) for x in df.close_time]
   return df

def relative_strength(prices, n=5):
    deltas = np.diff(prices)
    seed = deltas[:n+1]
    up = seed[seed >= 0].sum()/n
    down = -seed[seed < 0].sum()/n
    rs = up/down
    rsi = np.zeros_like(prices)
    rsi[:n] = 100. - 100./(1. + rs)

    for i in range(n, len(prices)):
        delta = deltas[i - 1]  # cause the diff is 1 shorter
        if delta > 0:
            upval = delta
            downval = 0.
        else:
            upval = 0.
            downval = -delta
        up = (up*(n - 1) + upval)/n
        down = (down*(n - 1) + downval)/n
        rs = up/down
        rsi[i] = 100. - 100./(1. + rs)
    return rsi

#Definitions de variables
#client = Client('lgNTJNUPVbsYHRrVe7X13SjLqj2WI35CQaw1BtkknaF0Of88jyP99JXBzpgHUkCo','825D33x3yCHjGQ3QyoMHIxFCooBtSW3SVd1FqFBXEcYx7tLrTYT4JuYmrk0vEsCA')
varema=0
varrsi=0
qtx1=0
test= False
root_url = 'https://api.binance.com/api/v1/klines'


while True:
    #A voir si tu sors pas ces options de la boucle aussi si elle
    symbol = 'BTCUSDT'
    interval = '1m'
    url1 = root_url + '?symbol=' + symbol + '&interval=' + interval
    response = requests.get(url1)

    #Gestion Too Many Request
    while (response.status_code == 429):
        try:
            waitTime = response.headers['Retry-After']
            sleep(waitTime)
            response = requests.get(url1)

    #Mise en forme DataFrame
    data = json.loads(response.text)
    df = pd.DataFrame(data)
    df.columns = ['open_time',
                  'o', 'h', 'l', 'c', 'v',
                  'close_time', 'qav', 'num_trades',
                  'taker_base_vol', 'taker_quote_vol', 'ignore']

    df.index = [dt.datetime.fromtimestamp(x/1000.0) for x in df.close_time]

    #Calcul indicateurs
    XRPUSD = get_bars('BTCUSDT')

    XRPT = XRPUSD['c'].astype('float')
    prices = np.array(XRPT)
    rsi = relative_strength(prices)
    EMA1 = movingaverage(prices,15)
    EMA2 = movingaverage(prices,40)
    if (EMA1[-1])>(EMA2[-1]):
       if (varema)==0:
          varema=1
          varrsi=0
          bp1=0
          qtx1=0
          print("-----------------Long strategy on-----------------")

    if (EMA1[-1])<(EMA2[-1]):
       if (varema)==0:
          varema=2
          varrsi=0
          bp1=0
          qtx1=0
          print("----------------Short strategy on-----------------")

    if (EMA1[-1])>(EMA2[-1]):
       if (varema)==2:
          if (varrsi)==0:
             varema=0
             print("-------Trend Reversal - Short strategy off------")

    if (EMA1[-1])<(EMA2[-1]):
       if (varema)==1:
          if (varrsi)==0:
             varema=0
             print("-------Trend Reversal - Long strategy off-------")

    if (EMA1[-1])>(EMA2[-1]):
       if (varema)==2:
          if (varrsi)==1:
             varema=0
             varrsi=0
             PNL2=(XRPT[-1]*qtx1)-2000
             print("------Trend Reversal - SELL 2000$","--@--",XRPT[-1],"  PNL $  ",PNL2," PERF % ",(PNL2/2000)*100)
             sleep(15)

    if (EMA1[-1])>(EMA2[-1]):
       if (varema)==2:
          if (varrsi)==2:
             varema=0
             varrsi=0
             PNL3=(XRPT[-1]*qtx2)-6000
             print("------Trend Reversal - SELL 6000$","--@--",XRPT[-1],"  PNL $  ",PNL3," PERF % ",(PNL3/6000)*100)
             sleep(15)

    if (EMA1[-1])<(EMA2[-1]):
       if (varema)==1:
          if (varrsi)==1:
             varema=0
             varrsi=0
             PNL1=(XRPT[-1]*qtx1)-5000
             print("------Trend Reversal - SELL 5000$","--@--",XRPT[-1],"  PNL $  ",PNL1," PERF % ",(PNL1/5000)*100)
             sleep(15)


    if (varema)==1:
       if (varrsi)==0:
          if (rsi[-1])>30:
             print("BTC",XRPT[-1],"position 0$","Long strategy")

    if (varema)==1:
       if (varrsi)==0:
          if (rsi[-1])<30:
             bp1=XRPT[-1]
             qtx1=(5000/bp1)
             varrsi=1
             print("------------------------------------------------BUY 5000$","--@--",(bp1),"--QTX--",qtx1)

    if (varema)==1:
       if (varrsi)==1:
          if (rsi[-1])<70:
             print("BTC",XRPT[-1],"position 5000$","Long strategy")

    if (varema)==1:
       if (varrsi)==1:
          if (rsi[-1])>70:
             PNL1=(XRPT[-1]*qtx1)-5000
             varrsi=0
             print("------------------------------------------------SELL 5000$","--@--",XRPT[-1],"  PNL $  ",PNL1," PERF % ",(PNL1/2000)*100)

    if (varema)==2:
       if (varrsi)==0:
          if (rsi[-1])>15:
             print("BTC",XRPT[-1],"position 0$","Short strategy")

    if (varema)==2:
       if (varrsi)==0:
          if (rsi[-1])<15:
             bp1=XRPT[-1]
             qtx1=(2000/bp1)
             varrsi=1
             print("------------------------------------------------BUY 2000$","--@--",(bp1),"--QTX--",qtx1)

    if (varema)==2:
       if (varrsi)==1:
          if (rsi[-1])<55:
             print("BTC",XRPT[-1],"position 2000$","Short strategy")

    if (varema)==2:
       if (varrsi)==1:
          if (rsi[-1])>55:
             PNL2=(XRPT[-1]*qtx1)-2000
             varrsi=0
             print("------------------------------------------------SELL 2000$","--@--",XRPT[-1],"  PNL $  ",PNL2," PERF % ",(PNL2/2000)*100)

    if (varema)==2:
       if (varrsi)==1:
          if (rsi[-1])<9:
             bp2=XRPT[-1]
             qtx2=((4000/bp1)+qtx1)
             varrsi=2
             print("------------------------------------------------BUY 4000$","--@--",(bp2),"AVG",((bp1+bp2)/qtx2),"-TOT QTX-",(qtx2))

    if (varema)==2:
       if (varrsi)==2:
          if (rsi[-1])<55:
             print("BTC",XRPT[-1],"position 6000$","Short strategy")

    if (varema)==2:
       if (varrsi)==2:
          if (rsi[-1])>55:
             PNL3=(XRPT[-1]*qtx2)-6000
             varrsi=0
             print("------------------------------------------------SELL 6000$","--@--",XRPT[-1],"  PNL $  ",PNL3," PERF % ",(PNL3/6000)*100)

    sleep(1)