#!/usr/bin/env python
# coding: utf-8


from jupyter_dash import JupyterDash
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output
import plotly.express as px

import pandas as pd
from psycopg2 import sql
import numpy as np

# Commented out for Heroku
# x = ConnectDsdk(dsdk_username,dsdk_password)
# cur = x['cursor']
# conn = x['connection']

audience_creation = False
audience_load_from_table = False
audience_load_from_pickle = True

# Commented out for Heroku
# if audience_creation:
#     print(f"Audience Creation Run")
#     query = sql.SQL(open("Cross_Viz_SQL_AudCreation.sql").read())
#     audience_params = {"input_sites":["ft.com",'wsj.com','cnbc.com']
#                        ,"subpage_desc":"%international%"
#                        ,"domain_pattern":"%.%"}
#     cross_viz_run=pd.read_sql(sql=query,con=conn,params=audience_params)
#     cross_viz_run.to_pickle("CrossVizRun.pkl")
#     print(f"\tAudience Saved Locally to pickle")
    
# Commented out for Heroku
# elif audience_load_from_table:
#     print(f"Audience Load from Table Run")    
#     query = sql.SQL(open("Cross_Viz_SQL_AudLoad.sql").read())    .format(input_audience=sql.Identifier("dsdk","ads_public","sample_guids_financialnews"))
#     audience_params = {"domain_pattern":"%.%"}
#     cross_viz_run=pd.read_sql(sql=query,con=conn,params=audience_params)
#     cross_viz_run.to_pickle("CrossVizRun.pkl")
#     print(f"\tAudience Saved Locally to pickle")
    
# Commented out for Heroku
# elif audience_load_from_pickle:
#     print(f"Audience Load from Pickle")    
#     cross_viz_run=pd.read_pickle("CrossVizRun.pkl")

# Comment back out when not running Heroku
if audience_load_from_pickle:
    print(f"Audience Load from Pickle")    
    cross_viz_run=pd.read_pickle("CrossVizRun.pkl")
else:
    print("Nothing's going to work!")
    
    
cross_viz_pivot = cross_viz_run.pivot_table(index='first_site',columns='cross_site',values='pct_first_site').fillna(0)



domains_choose= np.random.choice(cross_viz_pivot.index.values,5,replace=False)


site_choices = list(cross_viz_pivot.columns.values)

x_axis = list(np.random.choice(site_choices,1))[0]
y_axis = list(np.random.choice(site_choices,1))[0]


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = JupyterDash(__name__, external_stylesheets=external_stylesheets,suppress_callback_exceptions=True)

def site_selections():
    return [html.Div([
                html.Label('Site Select'),
                dcc.Dropdown(
                    id="site-select",
                    options=[
                        {'label': i, 'value': i} for i in site_choices
                    ],multi=True,value=['target.com','etsy.com','ebay.com']),
            ],
                style={'width': "60%", 'margin-bottom': 10}
            ),

            html.Div([
                html.Label('Y Axis Select'),
                dcc.Dropdown(id="y-axis-column",value='cnn.com'),
            ],
                style={'width': "60%", 'margin-bottom': 10}
            ),
            html.Div([
                html.Label('X Axis Select'),
                dcc.Dropdown(id="x-axis-column",value='linkedin.com'), 
            ],
                style={'width': "60%", 'margin-bottom': 10}
            )]

@app.callback(
    Output("heatmap-domain-choice", "figure"), 
    [Input("site-select",'value'),Input('x-axis-column','value'),Input('y-axis-column','value')])
def filter_heatmap(inp_domains_audience,inp_domain_x,inp_domain_y):
    if type(inp_domains_audience)==str:
        inp_domains_audience = [inp_domains_audience]
        
    if len(inp_domains_audience)==0:
        inp_domains_audience=site_choices[0]
        
    
    data_to_show = cross_viz_pivot.loc[inp_domains_audience][[inp_domain_x,inp_domain_y]]*100
    data_to_show = data_to_show.round(2)
    data_to_show = data_to_show
    
    
    fig = px.imshow(data_to_show,x=data_to_show.columns,y=data_to_show.index,labels=dict(x='Cross-Viz Sites',y='Chosen Sites',color='Pct of Site Audience'))
    return fig

@app.callback(
    Output('x-axis-column', 'options'),
    [Input('y-axis-column', 'value')])
def set_x_axis_choices(existing_y_axis_choice):
    return [{'label': i, 'value': i} for i in site_choices if i!=existing_y_axis_choice]

@app.callback(
    Output('y-axis-column', 'options'),
    [Input('x-axis-column', 'value')])
def set_y_axis_choices(existing_x_axis_choice):
    return [{'label': i, 'value': i} for i in site_choices if i!=existing_x_axis_choice]

# Function to change scatter plot
@app.callback(
Output('scatter-plot-domain-choice','figure'),
[Input("site-select",'value'),Input('x-axis-column','value'),Input('y-axis-column','value')]
)    
def update_crossviz_scatter(inp_domains_audience,inp_domain_x,inp_domain_y):
    if type(inp_domains_audience)==str:
        inp_domains_audience = [inp_domains_audience]
        
    if len(inp_domains_audience)==0:
        inp_domains_audience=site_choices[0]
        
    
    data_to_show = cross_viz_pivot.loc[inp_domains_audience][[inp_domain_x,inp_domain_y]]*100
    data_to_show = data_to_show.round(2)
    data_to_show = data_to_show.reset_index()
    
    fig = px.scatter(data_frame = data_to_show
                         ,x=inp_domain_x
                         ,y=inp_domain_y
                         ,color='first_site'
                         ,text='first_site'
#                          ,size=5
                         ,hover_name='first_site'
                        ,labels={
                         "first_site": "Site Visited",
                         inp_domain_x: f"Pct of Cross-Visit to {inp_domain_x}",
                         inp_domain_y: f"Pct of Cross-Visit to {inp_domain_y}"
#                             ,"pct_aud_y":"Pct of Audience Visiting Any of Y Sites"
                         }
                    )
    
    
    fig.update_xaxes(range=[-5, 105],tickvals=np.arange(-10,105,10))
    fig.update_yaxes(range=[-5, 105],tickvals=np.arange(-10,105,10))
    fig.update_layout(transition_duration=500)
    
    fig.add_shape(type="line",
        x0=-100, y0=0, x1=110, y1=0,
        line=dict(color="Black",width=3)
        )
    fig.add_shape(type="line",
    x0=0, y0=-100, x1=0, y1=110,
    line=dict(color="Black",width=3)
    )
    
    return fig


app.layout = html.Div(children=[
    html.H1(f"Cross Visitation Within Audience"),
    
    html.Div(
        children=site_selections()  
        )
    , html.Div(
    [
     html.Div([html.H3("Cross Viz Heatmap")
              ,dcc.Graph(id='heatmap-domain-choice')]
              ,className='six columns'),   
        
     html.Div([html.H3("Cross Viz Graph")
              ,dcc.Graph(id='scatter-plot-domain-choice')]
              ,className='six columns')      
    ],className='row'
    
    
    
    )
    
    
 
]

)

if __name__ == '__main__':
    app.run_server(debug=True)


 




