import pickle
from jupyter_dash import JupyterDash
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px


with open('data_dict_v6.pkl', 'rb') as handle:
    data_dict = pickle.load(handle)

with open('axes_nums_v6.pkl', 'rb') as handle:
    axes_nums = pickle.load(handle)



cols_save = list(axes_nums.index.values)


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = JupyterDash(__name__, external_stylesheets=external_stylesheets)
# Create server variable with Flask server object for use with gunicorn
server = app.server

quarters_menu = [x for x in quarters_run]
# print(months)
quarter_first = quarters_menu[0]
quarter_last = quarters_menu[-1]
quarter_default = quarter_first

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
    html.H1(children='Brand Distancing - By Quarter - 2020'),
    html.Label('Quarter'),
    dcc.Slider(
        id='quarter-slider',
        min=0,
        max=3,
        marks={quarter_idx: quarter for quarter_idx,quarter in enumerate(quarters_menu)},
        value=0
    ),
    dcc.RadioItems(
                id='graph-type',
                options=[{'label': i, 'value': i} for i in ['Pct', 'Delta from Random']],
                value='Pct',
                labelStyle={'display': 'inline-block'}
            ),
    dcc.Graph(
        id='scatter-plot'
    ),
    html.Div(["Y-Axis Choice",dcc.Dropdown(
                id='y-axis-column',
                options=[{'label': i, 'value': i} for i in cols_save],
                value=cols_save[1]
            ),"X-Axis Choice",dcc.Dropdown(
                id='x-axis-column',
                options=[{'label': i, 'value': i} for i in cols_save],
                value=cols_save[0]
            )
             ], style={"width": "50%"}
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
[Input('quarter-slider','value'),Input('x-axis-column','value'),Input('y-axis-column','value')
 ,Input("graph-type",'value')
]
)
def update_graph(selected_quarter,x_axis_column,y_axis_column,graph_type):       
    df_use = data_dict[selected_quarter][0]
    df_random = data_dict[selected_quarter][1]
    df_size = data_dict[selected_quarter][2]
    
    

    df_pct =         pd.concat([data_dict[selected_quarter][0],data_dict[selected_quarter][1]]).merge(data_dict[selected_quarter][2],on='brand_label',how='left')        .fillna(value={"total_guids":round(data_dict[selected_quarter][2]['total_guids'].mean())})
    
    df_delta = data_dict[selected_quarter][4].merge(data_dict[selected_quarter][2],on='brand_label',how='left')
    
    
    if graph_type == "Pct":
    
        fig = px.scatter(data_frame = df_pct
                         ,x=x_axis_column
                         ,y=y_axis_column
                         ,color='brand_label'
                         ,text='brand_label'
                         ,size='total_guids'
                         ,hover_name='brand_label'
                        ,labels={
                         "brand_label": "Brand Label",
                         "total_guids": "Number of Visitors"
                         })


        x_min = axes_nums.loc[x_axis_column]['min']
        x_max = axes_nums.loc[x_axis_column]['max']

        y_min = axes_nums.loc[y_axis_column]['min']
        y_max = axes_nums.loc[y_axis_column]['max']
        
    else: #graph_type = "Delta from Random"
        fig = px.scatter(data_frame = df_delta
                         ,x=x_axis_column
                         ,y=y_axis_column
                         ,color='brand_label'
                         ,text='brand_label'
                         ,size='total_guids'
                         ,hover_name='brand_label'
                        ,labels={
                         "brand_label": "Brand Label",
                         "total_guids": "Number of Visitors"
                         })
        
        x_min = -.2
        x_max = .2
        
        y_min = -.2
        y_max = .2
        

        fig.add_shape(type="line",
        x0=-1, y0=0, x1=1, y1=0,
        line=dict(color="Black",width=3)
        )
        fig.add_shape(type="line",
        x0=0, y0=-1, x1=0, y1=1,
        line=dict(color="Black",width=3)
        )
    
    fig.update_xaxes(range=[x_min, x_max])
    fig.update_yaxes(range=[y_min, y_max])
    fig.update_layout(transition_duration=500)
    return fig
 
    

if __name__ == '__main__':
    app.run_server(debug=True)





