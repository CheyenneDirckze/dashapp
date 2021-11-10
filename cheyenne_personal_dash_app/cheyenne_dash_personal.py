#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import datetime
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import gunicorn

#df = pd.read_csv('owid-covid-data.csv')

parts = pd.read_csv('https://covid.ourworldindata.org/data/owid-covid-data.csv', chunksize = 40000)
df = pd.concat(parts, ignore_index = True)

app = dash.Dash(__name__)

server = app.server

df['date'] = pd.to_datetime(df['date'])

df['Test_to_detection'] = df['new_tests']/df['new_cases']

opts = ['total_cases', 'new_cases', 'new_deaths', 'total_deaths']

conts = ['Asia','Europe','Africa','North America', 'South America', 'Oceania']

countries = [i for i in df['location'].unique().tolist() if i not in conts]

dfworld = df[df['location']=='World']

dfsl = df[df['location']=='Sri Lanka']

sdf = df[['location','date','new_cases','total_cases', 'new_deaths','total_deaths']]

dfSL = sdf[sdf['location']=='Sri Lanka']

dfWorld = sdf[sdf['location']=='World']

dfRoW = dfWorld.set_index('date').drop('location',axis = 1).subtract(dfSL.set_index('date').drop('location', axis = 1))
dfRoW.reset_index(inplace = True)
dfRoW.insert(0,'location','RoW')

dfAsia = sdf[sdf['location']=='Asia']

dfSaarc = sdf.loc[(sdf['location']=='Afghanistan')|(sdf['location']=='Bangladesh')|(sdf['location']=='Bhutan')|
                 (sdf['location']=='India')|(sdf['location']=='Maldives')|(sdf['location']=='Nepal')|
                 (sdf['location']=='Pakistan')|(sdf['location']=='Sri Lanka')].groupby('date').sum().reset_index()
dfSaarc.insert(0,'location','SAARC')

df_2 = pd.concat([dfSaarc,dfAsia, dfSL,dfRoW],ignore_index = True)

clist = df_2['location'].unique()

aggs = ['Daily','Weekly','Monthly','7-day','14-day']

#Tabbed layout

app.layout = html.Div([
    html.H1('COVID-19 DASHBOARD'),
    dcc.Tabs(id="tabs-graph", value='tab-1-example-graph', children=[
        dcc.Tab(label='Tab One', value='tab-1-example-graph'),
        dcc.Tab(label='Tab Two', value='tab-2-example-graph'),
        dcc.Tab(label='Tab Three', value = 'tab-3-example-graph'),
        dcc.Tab(label='Tab Four', value = 'tab-4-example-graph'),
        dcc.Tab(label='Tab Five', value = 'tab-5-example-graph')
    ]),
    html.Div(id='tabs-content-example-graph'),
    html.Hr(),
    html.Div('Created by Cheyenne Dirckze (COHNDDS201P-004)')
])



#Old layout
"""
app.layout = html.Div([
    html.Div([
        html.Div(dcc.Dropdown(id = 'q1features', options = [{'label':i, 'value':i} for i in opts], value = 'new_cases')),
        html.Div(dcc.Graph(id = 'q1figure')),
        html.Div(dcc.DatePickerRange(id = 'q1dates', start_date = datetime.date(2020,1,1), end_date = datetime.date(2021,1,1)))
    ]),
    
    html.Div([
        html.H1(children = 'Question 2'),
        html.Div(dcc.Dropdown(id = 'q2features', options = [{'label':i, 'value':i} for i in opts], value = 'total_cases')),
        html.Div(dcc.Checklist(id = 'q2checklist', options = [{'label':i, 'value':i} for i in clist], value = ['Sri Lanka'])),
        html.Div(dcc.Graph(id = 'q2multiline')),
        html.Div(dcc.DatePickerRange(id = 'q2dates', start_date = datetime.date(2020,1,1), end_date = datetime.date(2021,1,1))),
        html.Div(dcc.Dropdown(id = 'q2aggregates', options = [{'label':i, 'value':i} for i in aggs], value = 'Daily'))
    ]),
    
    html.Div([
        html.H1(children = 'Test to detection ratio'),
        html.Div(dcc.Dropdown(id ='q3drop', options = [{'label':i, 'value':i} for i in countries], value = 'Sri Lanka')),
        html.Div(dcc.Graph(id = 'q3figure')),
        html.Div(dcc.DatePickerRange(id = 'q3dates', start_date = datetime.date(2020,1,1), end_date = datetime.date(2021,1,1)))
    ]),
    
    html.Div([
        html.H1(children = 'Correlation between Tests and Cases of Sri Lanka'),
        html.P(id = 'q4correlation'),
        html.Div(dcc.Graph(id = 'q4scatter')),
        html.Div(dcc.DatePickerRange(id = 'q4dates', start_date = datetime.date(2020,1,1), end_date = datetime.date(2021,1,1)))
    ]),
    
    html.Div([
        html.H1(children = 'Total Active+Recovered Cases vs. Deaths'),
        html.Div(dcc.Dropdown(id = 'q5continent', options = [{'label':i,'value':i} for i in conts], value = 'Asia')),
        html.Div(dcc.RadioItems(id = 'q5year', options = [
            #{'label':'2019','value':2019},
            {'label':'2020','value':2020},
            {'label':'2021','value':2021}
        ], value = 2021)),
        #REPEALED!#html.Div(dcc.DatePickerSingle(id='q5date', date = datetime.date(2020,1,1))),
        html.Div(dcc.Graph(id = 'q5pie'))
    ])
])

"""
@app.callback(Output('tabs-content-example-graph', 'children'),
              Input('tabs-graph', 'value'))
def render_content(tab):
    if tab == 'tab-1-example-graph':
        return html.Div([
        html.Div(dcc.Dropdown(id = 'q1features', options = [{'label':i, 'value':i} for i in opts], value = 'new_cases')),
        html.Div(dcc.Graph(id = 'q1figure')),
        html.Div(dcc.DatePickerRange(id = 'q1dates', start_date = datetime.date(2020,1,1), end_date = datetime.date(2021,1,1)))
    ])
    
    elif tab == 'tab-2-example-graph':
        return html.Div([
        html.H1(children = 'Sri Lanka | Asia | SAARC | Rest of World'),
        html.Div([
            html.Div(dcc.Dropdown(id = 'q2features', options = [{'label':i, 'value':i} for i in opts], value = 'total_cases'), 
                    style = {'display': 'inline-block', 'width': '50%'}),
            html.Div(dcc.Dropdown(id = 'q2aggregates', options = [{'label':i, 'value':i} for i in aggs], value = 'Daily'),
                    style = {'display': 'inline-block', 'width': '50%'})
            
        ]),
        
        html.Div(dcc.Checklist(id = 'q2checklist', options = [{'label':i, 'value':i} for i in clist], value = ['Sri Lanka'])),
        html.Div(dcc.Graph(id = 'q2multiline')),
        html.Div(dcc.DatePickerRange(id = 'q2dates', start_date = datetime.date(2020,1,1), end_date = datetime.date(2021,1,1)))
        
    ])
    
    elif tab == 'tab-3-example-graph':
        return html.Div([
        html.H1(children = 'Test to detection ratio'),
        html.Div(dcc.Dropdown(id ='q3drop', options = [{'label':i, 'value':i} for i in countries], value = 'Sri Lanka')),
        html.Div(dcc.Graph(id = 'q3figure')),
        html.Div(dcc.DatePickerRange(id = 'q3dates', start_date = datetime.date(2020,1,1), end_date = datetime.date(2021,1,1)))
    ])
        
    
    elif tab == 'tab-4-example-graph':
        return html.Div([
        html.H1(children = 'Correlation between Tests and Cases of Sri Lanka'),
        html.P(id = 'q4correlation'),
        html.Div(dcc.Graph(id = 'q4scatter')),
        html.Div(dcc.DatePickerRange(id = 'q4dates', start_date = datetime.date(2020,1,1), end_date = datetime.date(2021,1,1)))
    ])
        
    
    elif tab == 'tab-5-example-graph':
        return html.Div([
        html.H1(children = 'Total Active+Recovered Cases vs. Deaths'),
        html.Div(dcc.Dropdown(id = 'q5continent', options = [{'label':i,'value':i} for i in conts], value = 'Asia')),
        html.Div(dcc.RadioItems(id = 'q5year', options = [
            #{'label':'2019','value':2019},
            {'label':'2020','value':2020},
            {'label':'2021','value':2021}
        ], value = 2021)),
        #REPEALED!#html.Div(dcc.DatePickerSingle(id='q5date', date = datetime.date(2020,1,1))),
        html.Div(dcc.Graph(id = 'q5pie'))
    ])
        


@app.callback(
Output('q1figure','figure'),
Input('q1features','value'),
Input('q1dates','start_date'),
Input('q1dates','end_date'))

def question1(feature,startdate,enddate):
    #dff = df[df['location']=='World']
    fig1 = px.line(dfworld, x='date', y = feature)
    fig1.update_layout(xaxis_range = [startdate,enddate])
    return fig1


@app.callback(
Output('q2multiline','figure'),
Input('q2checklist','value'),
Input('q2dates','start_date'),
Input('q2dates','end_date'),
Input('q2aggregates','value'),
Input('q2features','value'))

def question2(region,startdate,enddate,agg,feature):
    dff = df_2[df_2['location'].isin(region)]
    if agg == 'Daily':
        figdf = dff
    elif agg == 'Weekly':
        figdf = dff.groupby(['location',pd.Grouper(key  = 'date', freq = 'W')]).mean().reset_index()
    elif agg == 'Monthly':
        figdf = dff.groupby(['location',pd.Grouper(key  = 'date', freq = 'M')]).mean().reset_index()
    elif agg == '7-day':
        figdf =  dff.groupby('location').rolling(window = 7, on = 'date').mean().reset_index()
    elif agg == '14-day':
        figdf =  dff.groupby('location').rolling(window = 14, on = 'date').mean().reset_index()
    fig2 = px.line(figdf, x = 'date', y = feature, color = 'location')
    fig2.update_layout(xaxis_range = [startdate,enddate])
    return fig2


@app.callback(
Output('q3figure','figure'),
Input('q3drop','value'),
Input('q3dates','start_date'),
Input('q3dates','end_date'))

def question3(country,startdate,enddate):
    dff = df[df['location']== country]
    figdf = pd.concat([dfsl,dff]).reset_index()
    fig3 = px.line(figdf, x='date', y = 'Test_to_detection', color = 'location')
    fig3.update_layout(xaxis_range = [startdate,enddate])
    return fig3


@app.callback(
Output('q4scatter','figure'),
Output('q4correlation','children'),
Input('q4dates', 'start_date'),
Input('q4dates','end_date'))

def question4(sd,ed):
    dfsld = dfsl[dfsl['date'].between(sd,ed)]
    fig4 = px.scatter(dfsld, x = 'total_tests', y = 'new_cases')
    c = dfsld['total_tests'].corr(dfsld['new_cases'])
    x = f'The correlation in the chosen time frame is {round(c,2)}'
    #fig4.add_annotation()
    return fig4,x


@app.callback(
Output('q5pie','figure'),
Input('q5year','value'),
Input('q5continent','value'))
#REPEALED!#Input('q5date','date'),

def question5(year5, continent):
    #df['date'] = pd.to_datetime(df['date'])
    #dfyear = df[df['date'].dt.year==year5]
    #dfg = dfdated.groupby(by='continent').mean().reset_index()
    #dfc = df[df['continent']==continent]
    dfc = df[df['location']==continent]
    #data = dfc[dfc['date'].dt.year == year5].groupby('date').max().reset_index()[['new_deaths','hosp_patients']]
    data = dfc[dfc['date'].dt.year == year5].max()
    #figdata = data.to_dict()
    recoveriesAndCases = data['total_cases'] - data['total_deaths']
    deaths = data['total_deaths']
    #dfgf = dfg[['continent','new_tests']]
    #dfgff = dfgf[dfgf['continent']==continent].drop('continent', axis = 1)
    #data = dict(labels = ['new_tests','new_cases'],values =dfgff.values.tolist()[0])
    fig5 = px.pie(names = ['Recoveries + Active Cases', 'Deaths'], values = [recoveriesAndCases,deaths])
    return fig5
    

if __name__ == '__main__':
    app.run_server(debug = False)

