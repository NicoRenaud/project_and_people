import base64
import datetime
import io

import dash
from dash.dependencies import Input, Output, State
from dash import dcc, html, dash_table
import plotly.express as px
import plotly.graph_objects as go
from process_data import get_unique_names
from import_gantic import gantic2pandas, create_weekly_tasks, name2fullname, create_cummulative_project_timeline_project
from import_exact_engineer import create_sunburst_engineer,  create_engineer_timeline, create_timeline_engineer_prod
from import_exact_project import create_cummulative_project_timeline, create_project_timeline, create_sunburst_project
from import_exact_section import create_producitity_development,create_sunburst_section, create_timeline_hours_percentage
import numpy as np
import pandas as pd
import webbrowser
from threading import Timer


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# fname = "./data/hoursJanFeb2022.xlsx"
fname = "HoursJanOct2022.xlsx"
raw_df = pd.read_excel(fname)

eng_name_list = get_unique_names(raw_df, 'Employee')
proj_name_list = get_unique_names(raw_df, 'Project')
manager_name_list = get_unique_names(raw_df, 'Manager') 


gantic_filename = 'planning2022.csv'
gantic_data = gantic2pandas(gantic_filename)
gantic_weekly_tasks = create_weekly_tasks(gantic_data)

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

test_png = './assets/NleSc.png'
test_base64 = base64.b64encode(open(test_png, 'rb').read()).decode('ascii')

app.title = "eScience Data Xplorer"

server = app.server

app_color = {"graph_bg": "#082255", "graph_line": "#007ACE"}

app.layout = html.Div([
    html.Div([

        html.Div([
            html.Img(src='data:image/png;base64,{}'.format(test_base64),
                    style={'width':'20%',}
                    ),
                
        ], style={'width':'40%', 'display': 'inline-block'}),
        html.Div([
            dcc.Upload(
                id='upload-data',
                children=html.Div([
                    'Drag and Drop or ',
                    html.A('Select Files')
                ]),
                style={
                    'display': 'inline-block',
                    'width': '100%',
                    'height': '40px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin': '10px'
                },
                # Allow multiple files to be uploaded
                multiple=False
            ),
            html.Div('Hello', id='output'),
            # dcc.Store(id='store_raw_df'),
        ], style={'width':'49%','display': 'inline-block'}),
        
    ], style={'display': 'flex'}),

    dcc.Tabs([
        dcc.Tab(label='Employee', children=[
            # dcc.Dropdown(manager_name_list + ['All Managers'], 'All Managers', 
            #             id='manager_filter_name_dropdown', style={'width': '50%'},
            #             placeholder="Select a manager"),
            dcc.Dropdown(eng_name_list, eng_name_list[0], 
                         id='eng_name_dropdown', 
                         style={'width': '50%'},
                         searchable=True,
                         placeholder="Select an engineer"),
            html.Div([
                dcc.Graph(id='sunburst_engineer', style={'display': 'inline-block'}),
                dcc.Graph(id='timeline_engineer_prod', style={'display': 'inline-block'}), 
                dcc.Graph(id='timeline_engineer')]),
        ]),
        dcc.Tab(label='Project', children=[
            dcc.Dropdown(proj_name_list, proj_name_list[0], id='proj_name_dropdown', style={'width': '50%'}),
            html.Div([
                dcc.Graph(id='sunburst_project', style={'display': 'inline-block'}), 
                dcc.Graph(id='cummulative_timeline_project', style={'display': 'inline-block'}),
                dcc.Graph(id='timeline_project'),
                ]),
        ]),

        dcc.Tab(label='Line Manager', children=[

            html.Div
            (
                [
                    dcc.Dropdown(manager_name_list + ['Total', 'Total-RSE'], manager_name_list[0], 
                                 id='manager_name_dropdown', style={'width': '50%'}),
 
                    html.Div([
                        dcc.Graph(id='sunburst_section', style={'display': 'inline-block'}),
                        dcc.Graph(id='timeline_productivity', style={'display': 'inline-block'})
                        
                    ])
                   
                ],
            ),
            html.Div
            (
                [
                    dcc.Checklist(['Projection'], [], id='select_data', inline=True)
                ],
                style={
                    "display": "inline-block",
                    "width": "100%",
                    "margin-left": "0px",
                    'display':'flex',
                    'margin-right':'20px',
                    'vertical-align':'bottom',
                    "justify-content":'center'
                }
            ),
            html.Div
            (
                [
                    dcc.Graph(id='timeline_hours_percentage', style={'width': '100%'})
                ]
            ),
        ]),
        dcc.Tab(label='Planning', children=[
            dcc.Dropdown(proj_name_list, proj_name_list[0], id='proj_name_dropdown_planning', style={'width': '50%'}),
            html.Div([
                dcc.Graph(id='cummulative_timeline_project_planning')
                ]),
        ]),
    ])
])


@app.callback(Output('eng_name_dropdown', 'options'),
              Output('proj_name_dropdown', 'options'),
              Output('manager_name_dropdown', 'options'),
              Output('output', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'))
def clean_data(contents, filename, dates):

    if filename is not None:
        global raw_df
        global eng_name_list
        global proj_name_list
        global manager_name_list

        raw_df = pd.read_excel(filename)

        eng_name_list = get_unique_names(raw_df, 'Employee')
        proj_name_list = get_unique_names(raw_df, 'Project')
        manager_name_list = get_unique_names(raw_df, 'Manager') 
	
    return eng_name_list, proj_name_list, manager_name_list + ['Total', 'Total-RSE'], filename


@app.callback(
    Output('sunburst_engineer','figure'),
    Input('eng_name_dropdown', 'value'),
    Input('upload-data', 'contents'))
def update_sunburst_engineer(engineer_name, contents):
    return create_sunburst_engineer(raw_df, engineer_name, proj_name_list)

@app.callback(
    Output('timeline_engineer_prod','figure'),
    Input('eng_name_dropdown', 'value'))
def update_timeline_engineer_prod(engineer_name):
    return create_timeline_engineer_prod(raw_df, engineer_name)

@app.callback(
    Output('timeline_engineer','figure'),
    Input('eng_name_dropdown', 'value'))
def update_engineer_timeline(engineer_name):
    return create_engineer_timeline(raw_df, engineer_name)

@app.callback(
    Output('sunburst_project','figure'),
    Input('proj_name_dropdown', 'value'))
def update_sunburst_project(project_name):
    return create_sunburst_project(raw_df, project_name, eng_name_list)


@app.callback(
    Output('timeline_project','figure'),
    Input('proj_name_dropdown', 'value'))
def update_project_timeline(project_name):
    return create_project_timeline(raw_df, project_name)

@app.callback(
    Output('cummulative_timeline_project','figure'),
    Input('proj_name_dropdown', 'value'))
def update_cummulative_project_timeline(project_name):
    return create_cummulative_project_timeline(raw_df, project_name)


@app.callback(
    Output('timeline_hours_percentage', 'figure'),
    Input('manager_name_dropdown','value'))
def update_timeline_hours_percentage(manager_name):
    return create_timeline_hours_percentage(raw_df, manager_name, manager_name_list)

@app.callback(
    Output('timeline_productivity','figure'),
    Input('manager_name_dropdown', 'value'),
    Input('select_data', 'value'))
def update_producitity_development(manager_name, select_data):
    return create_producitity_development(raw_df, manager_name, manager_name_list, select_data)


@app.callback(
    Output('sunburst_section','figure'),
    Input('manager_name_dropdown', 'value'))
def update_sunburst_section(manager_name):
    create_sunburst_section(raw_df, manager_name, manager_name_list)



@app.callback(
    Output('cummulative_timeline_project_planning','figure'),
    Input('proj_name_dropdown_planning', 'value'))
def update_cummulative_project_timeline_project(project_name):
    return create_cummulative_project_timeline_project(gantic_weekly_tasks, project_name)




if __name__ == '__main__':
    

    def open_browser():
        webbrowser.open_new("http://localhost:{}".format(port))

    port = 8050
    Timer(1, open_browser).start()
    app.run_server(debug=True, port=port)
    # app.run_server(debug=False)
