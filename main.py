#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 27 18:45:11 2019

@author: drimer
"""

from bokeh.layouts import row, column, gridplot
from bokeh.models import ColumnDataSource, Slider, CustomJS, DataTable, \
TableColumn, HoverTool, DatetimeTickFormatter, Span
from bokeh.models.widgets import Button
from bokeh.plotting import curdoc, figure
from bokeh.driving import count
from time import sleep

import datetime as dt
import pandas as pd
import requests    
import json   
import numpy as np 
import sys

from strategies import goldenRise
#sans doute à mettre dans un import
def saveXLSX(df, nameFile='output.xlsx', namesheet='s1'):
    try:
        writer = pd.ExcelWriter(nameFile, engine='xlsxwriter')
        df.to_excel(writer,namesheet)
        writer.save()
        print('export réussi dans ' + nameFile)
    except :
        print('export failed')
    return None

DLbutton = Button(label="dl datas", button_type="success")

javaScript="""
function table_to_csv(source) {
    const columns = Object.keys(source.data)
    const nrows = source.get_length()
    const lines = [columns.join(',')]

    for (let i = 0; i < nrows; i++) {
        let row = [];
        for (let j = 0; j < columns.length; j++) {
            const column = columns[j]
            row.push(source.data[column][i].toString())
        }
        lines.push(row.join(','))
    }
    return lines.join('\\n').concat('\\n')
}


const filename = 'AllData.csv'
filetext = table_to_csv(source)
const blob = new Blob([filetext], { type: 'text/csv;charset=utf-8;' })

//addresses IE
if (navigator.msSaveBlob) {
    navigator.msSaveBlob(blob, filename)
} else {
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = filename
    link.target = '_blank'
    link.style.visibility = 'hidden'
    link.dispatchEvent(new MouseEvent('click'))
}
"""

strat_1 = goldenRise()

# Création des dataframes
source = ColumnDataSource(dict(
    time=[], low=[], high=[], open=[], close=[],rsi=[], position = [],
    ema1=[], ema2=[], emaD=[], color=[], date = [], strdate = []
))

sourceTrans = ColumnDataSource(dict(
    decision=[], stocks=[], prix=[], valeur=[], date = [], strdate = []
))

# Création du graph
hover = HoverTool(tooltips=[
    ("Time", "@strdate"),
    ("close", "@close"),
    ("Ema 1", "@ema1"),
    ("Ema 2", "@ema2")
    ])
#premier plot (close ema1 et ema2)
p = figure(plot_height=500, tools=[hover,"xpan","wheel_zoom","xbox_zoom","reset"], 
           y_axis_location="right", title = '', x_axis_type=None)
p.x_range.follow = "end"

p.x_range.follow_interval = 600000
p.x_range.range_padding = 0


p.line(x='date', y='close', alpha=0.2, line_width=3, color='navy', source=source)
p.line(x='date', y='ema1', alpha=0.8, line_width=2, color='orange', source=source)
p.line(x='date', y='ema2', alpha=0.8, line_width=2, color='red', source=source)
#p.segment(x0='time', y0='low', x1='time', y1='high', line_width=0.5, color='black', source=source)
#p.segment(x0='time', y0='open', x1='time', y1='close', line_width=2, color='color', source=source)

#deuxieme plot (rsi)
p2 = figure(plot_height=150, x_range=p.x_range, tools="xpan,xwheel_zoom,xbox_zoom,reset",
            y_axis_location="right", y_range = (0,100), x_axis_type=None)
p2.line(x='date', y='rsi', color='red', source=source)

#troisieme (ema1-ema2)
p3 = figure(plot_height=100, x_range=p.x_range, tools="xpan,xwheel_zoom,xbox_zoom,reset",
            y_axis_location="right", x_axis_type='datetime')
p3.segment(x0='date', y0=0, x1='date', y1='emaD', line_width=6, color='color', alpha=0.5, source=source)
p3.xaxis.formatter = DatetimeTickFormatter(seconds=["%H:%M:%S"],
                                           minsec = ["%H:%M:%S"],
                                           minutes =["%H:%M:%S"],
                                           hourmin = ["%H:%M"],
                                           hours=["%H:%M"],
                                           days = ['%d/%m'])

#creation des tableaux d'affichage
columns = [TableColumn(field="strdate", title="Date", width = 140),
           TableColumn(field="close", title="prix", width = 60)]

data_table1 = DataTable(source=source, columns=columns,index_position=None,
                   width=200, height=500,selectable= False)

columns2 = [TableColumn(field="strdate", title="Date", width = 130),
           TableColumn(field="prix", title="Prix", width = 50),
           TableColumn(field="decision", title="Decision", width = 50),
           TableColumn(field="stocks", title="Qte Stocks", width = 50)]
data_table2 = DataTable(source=sourceTrans, columns=columns2,index_position=None,
                   width=280, height=300,selectable= False)
    
def getData(symbol = 'XRPUSDT', interval = '1m'):
    root_url = 'https://api.binance.com/api/v1/klines'
    url = root_url + '?symbol=' + symbol + '&interval=' + interval
    response = requests.get(url)
    while (response.status_code == 429):
        try:
            waitTime = response.headers['Retry-After']
            sleep(waitTime)
            response = requests.get(url)
        except :
            sys.exit(0)
    df = pd.DataFrame(json.loads(response.text))
    df.columns = ['open_time','o', 'h', 'l', 'c', 'v','close_time', 'qav',
                  'num_trades', 'taker_base_vol', 'taker_quote_vol', 'ignore']
    df.index = [dt.datetime.fromtimestamp(x/1000.0) for x in df.close_time]
    return df

def last_info(df):
    XRPT = df['c'].astype('float')
    prices = np.array(XRPT)
    rsi = _relative_strength(prices)
    EMA1 = _moving_avg(prices,15)
    EMA2 = _moving_avg(prices,40)
    last = df[-1:]
    o= float(last['o'])
    c = float(last['c'])
    return o, float(last['h']), float(last['l']), c, rsi, EMA1, EMA2
    
def _moving_avg(prices, window):
    weigths = np.repeat(1.0, window)/window
    smas = np.convolve(prices, weigths, 'valid')
    return smas # as a numpy array

def _relative_strength(prices, n=5):
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

@count()
def update(t):
    global strat_1
    df = getData()
    open, high, low, close, rsi, EMA1, EMA2 = last_info(df)
    color = "green" if open < close else "red"
    date = dt.datetime.now()
    strdate = date.strftime("%Y-%m-%d %H:%M:%S")
    decision = strat_1.makeDecision(EMA1, EMA2, rsi)
    #cas de transaction
    if decision != 0:
        vline = Span(location=date, dimension='height',
                     line_color='red' if decision>0 else 'green', line_width=1)
        strat_1.stock += decision/close
        p.renderers.extend([vline])
        p2.renderers.extend([vline])
        dat = dict(decision=[decision], stocks=[strat_1.stock], prix=[close],
                   valeur=[strat_1.stock*close], date = [date], strdate = [strdate])
        sourceTrans.stream(dat,None)    

    new_data = dict(
        time=[t],
        open=[open],
        high=[high],
        low=[low],
        close=[close],
        color=[color],
        rsi = [rsi[-1]],
        ema1 = [EMA1[-1]],
        ema2 = [EMA2[-1]],
        date = [date],
        strdate = [strdate],
        position = [strat_1.position]
    )
    #maj du titre
    p.title.text = """{0} | prix: {1:.3f} | rsi : {2:.0f}| position : {3} |
 stock : {4:.3f} | valeur : {5:.3f} | vars : {6}/{7}  >>> {8}""".format(strdate,close,
    rsi[-1],strat_1.position,strat_1.stock,strat_1.stock*close,strat_1.varema,
    strat_1.varrsi, strat_1.strategy)
    close = source.data['close'] + [close]
    new_data['emaD'] = [EMA1[-1] - EMA2[-1]]
    source.stream(new_data, None)

curdoc().add_root(row(column(gridplot([[p], [p2], [p3]], toolbar_location="left", plot_width=1000)),column(DLbutton, data_table1, data_table2)))
curdoc().add_periodic_callback(update, 5000)
curdoc().title = "XRPUSDT"
DLbutton.callback = CustomJS(args=dict(source=source),code=javaScript)