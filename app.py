#!/usr/bin/env python
# coding: utf-8




from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# !pip install jupyter-dash
from jupyter_dash import JupyterDash
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import pickle





data_dict = pickle.load(open("data_dict_v6.pkl","rb"))
# data_dict[1][2]
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = JupyterDash(__name__, external_stylesheets=external_stylesheets)
# Create server variable with Flask server object for use with gunicorn
server = app.server

months = [int(x) for x in sorted(data_dict.keys())]

month_min = min(months)
month_max = max(months)
month_names = ["Jan","Feb","Mar","Apr","May","June","July","Aug","Sept","Oct","Nov","Dec"]
month_default = 1

cols_save = data_dict[1][0].columns


definitions_table = pd.DataFrame([
    ["Nike","nike.com",""]
    ,["Adidas","adidas.com",""]
    ,["lululemon","lululemon.com",""]
    ,["Chanel","chanel.com",""]
    ,["Nordstrom","nordstrom.com",""]
    ,["Nieman Marcus","neimanmarcus.com",""]
    ,["Saks Fifth Avenue","saksfifthavenue.com",""]
    ,["Gap","gap.com",""]
    ,["H&M","hm.com",""]
    ,["Zara","zara.com",""]
    ,["Abercrombie","abercrombie.com",""]
    ,["Uniqlo","uniqlo.com",""]
],columns=["Brand","Site Actions","Search Actions (%=Wildcard)"])

app.layout = html.Div(children=[
    html.H1(children='Brand Distancing - By Month - 2020'),
    html.Label('Months'),
    html.H4(children=f'''Starting instructions: pick two domain categories that you think are worth exploring against one another. Double click the graph to get the best axis fit and set the x and y min/max for optimal viewing (.02 +- your min and max is a good starting point)
    Then, start sliding across the months one by one and see if you can notice any changes in how the brand audiences shift against one another or as groups of domains. The axes represent the overlap of that brand audience (in that month) in that chosen category'''),
    dcc.Slider(
        id='month-slider',
        min=month_min,
        max=month_max,
        marks={i: f"{month_names[int(i)-1]}" for i in months},
        value=month_min
    ),
    dcc.Graph(
        id='scatter-plot'
    ),
    html.Div(["X-Axis Choice (Domain Category)",dcc.Dropdown(
                id='x-axis-column',
                options=[{'label': i, 'value': i} for i in cols_save],
                value=cols_save[0]
            )
            ,html.Label('x min'),dcc.Input(
            id='x-axis-min',
            type='number',
            value=-.01,
            min=-0.5,
            max=1,
            step=0.01
            )
            ,html.Label('x max'),dcc.Input(
            id='x-axis-max',
            type='number',
            value=.05,
            min=-0.5,
            max=1,
            step=0.01
            )
             ], style={'columnCount': 3}),
#     html.Div("\n"),
    html.Div(["Y-Axis Choice (Domain Category)",dcc.Dropdown(
                id='y-axis-column',
                options=[{'label': i, 'value': i} for i in cols_save],
                value=cols_save[1]
            )
             ,html.Label('y min'),dcc.Input(
            id='y-axis-min',
            type='number',
            value=-.01,
            min=-0.5,
            max=1,
            step=0.01
            )
          ,html.Label('y max'),dcc.Input(
            id='y-axis-max',
            type='number',
            value=.05,
            min=-0.5,
            max=1,
            step=0.01
            )
             ], style={'columnCount': 3}),
    
    html.H1(children="Brand Definitions:"),
    html.Div(dash_table.DataTable(
        id='brand-definitions',
        columns=[{"name": i, "id": i} 
                 for i in definitions_table.columns],
        data=definitions_table.to_dict('records'),
        style_cell=dict(textAlign='left'),
        style_header=dict(backgroundColor="paleturquoise"),
        style_data=dict(backgroundColor="lavender")
    ))
])

@app.callback(
Output('scatter-plot','figure'),
[Input('month-slider','value'),Input('x-axis-column','value'),Input('y-axis-column','value')
,Input('x-axis-min','value'),Input('x-axis-max','value')\
,Input('y-axis-min','value'),Input('y-axis-max','value') 
]
)
def update_graph(selected_month,x_axis_column,y_axis_column,x_min_use,x_max_use,y_min_use,y_max_use):
        
    df_use = data_dict[selected_month][0]
    df_size = data_dict[selected_month][1]
    df_size.columns=["brand_label","size"]
    df_use = df_use.merge(right=df_size,on='brand_label')
    fig = px.scatter(data_frame = df_use
                     ,x=x_axis_column
                     ,y=y_axis_column
                     ,color='brand_label'
                     ,text='brand_label'
                     ,size='size'
                     ,hover_name='brand_label'
                    ,labels={
                     "brand_label": "Brand Label",
                     "size": "Number of Visitors"
                     })
        
    fig.update_xaxes(range=[x_min_use, x_max_use])
    fig.update_yaxes(range=[y_min_use, y_max_use])
    fig.update_layout(transition_duration=500)
    return fig  
    

if __name__ == '__main__':
    app.run_server(debug=True)













