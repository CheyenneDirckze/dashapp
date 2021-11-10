#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import gunicorn

import plotly.express as px
import pandas as pd


parts = pd.read_csv('https://covid.ourworldindata.org/data/owid-covid-data.csv', chunksize = 40000)
df = pd.concat(parts, ignore_index = True)

app = dash.Dash(__name__)

server = app.server

opts =  ['total_cases', 'new_cases', 'new_deaths', 'total_deaths' ]

#fig = px.line(df[df['location']=='World'], x = 'date', y = 'new_cases')

app.layout = html.Div([html.Div(dcc.Dropdown(id = 'attribute', options = [{'label':i, 'value': i} for i in opts],
                                             value = 'new_cases' ))
                       ,dcc.Graph(id = 'line')])

@app.callback(
Output('line', 'figure'),
Input('attribute', 'value'))

def linechart(opt):
    dff = df[df['location'] == 'World']
    fig2 = px.line(dff, x = 'date', y = opt)
    return fig2

if __name__ == '__main__':
    app.run_server(debug = False)

