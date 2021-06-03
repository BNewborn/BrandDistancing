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





data_dict = pickle.load(open("data_dict.pkl","rb"))
# data_dict[1][2]




# data_dict[1][0] #pca dataframe
# data_dict[1][1] #explained variance
# data_dict[1][2] #sizes dataframe

n_components = 2
col_names = [f"Principal Component {x+1}" for x in range(n_components)]







external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = JupyterDash(__name__, external_stylesheets=external_stylesheets)
server = app.server

months = [int(x) for x in sorted(data_dict.keys())]
# print(months)
month_min = min(months)
month_max = max(months)
month_names = ["Jan","Feb","Mar","Apr","May","June","July","Aug","Sept","Oct","Nov","Dec"]
month_default = 1


# fig = px.scatter(data_frame = piv_transformed.reset_index(),x='pca_0',y='pca_1',hover_name='brand_label')

definitions_table = pd.DataFrame([
    ["Tesla","tesla.com OR tesla page on cars.com/carmax/kbb",""]
    ,["Ford","ford.com OR ford page on cars.com/carmax/kbb",""]
    ,["VW","vw.com OR volkswagen page on cars.com/carmax/kbb",""]
    ,["Chevrolet","chevrolet.com OR chevrolet page on cars.com/carmax/kbb",""]
    ,["HomeDepot","homedepot.com",""]
    ,["Lowes","lowes.com",""]
    ,["Nike","nike.com",""]
    ,["Adidas","adidas.com",""]
    ,["Chanel","chanel.com",""]
    ,["McDonalds","mcdonalds.com or McD app",""]
    ,["WholeFoods","wholefoodsmarket.com",""]
    ,["BeyondMeat","beyondmeat.com OR %beyond%meat% product page on Amazon, Walmart, WholeFoods",""]
    ,["HarryStyles","","%harry%styles%"]
    ,["TaylorSwift","","%taylor%swift%"]
    ,["PatrickMahomes","","%patrick%mahomes%"]
],columns=["Brand","Site Actions","Search Actions (%=Wildcard)"])

app.layout = html.Div(children=[
    html.H1(children='Brand Distancing By Month - 2020'),
    html.Label('Months'),
    dcc.Slider(
        id='month-slider',
        min=month_min,
        max=month_max,
        marks={i: f"{month_names[int(i)-1]}" for i in months},
        value=month_min
    ),
    html.Div(id="exp-var"),

    dcc.Graph(
        id='scatter-plot'
    ),
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
[Input('month-slider','value')]
)
def update_graph(selected_month):
    df_use = data_dict[selected_month][0]
    df_size = data_dict[selected_month][2]
    df_size.columns=["brand_label","size"]
    df_use = df_use.merge(right=df_size,on='brand_label')
    
    fig = px.scatter(data_frame = df_use
                     ,x=col_names[0]
                     ,y=col_names[1]
                     ,color='brand_label'
                     ,text='brand_label'
                     ,size='size'
                     ,hover_name='brand_label')
    fig.update_layout(transition_duration=100)
    
    return fig

@app.callback(
Output('exp-var','children'),
[Input('month-slider','value')]
)
def update_exp_var(selected_month):
    exp_var = data_dict[selected_month][1]
    return f"Explained Variance this Month: {round(exp_var,4)}"
    
    

if __name__ == '__main__':
    app.run_server(debug=True)













