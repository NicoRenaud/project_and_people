import base64
import datetime
import io

import dash
from dash.dependencies import Input, Output, State
from dash import dcc, html, dash_table
import plotly.express as px
import plotly.graph_objects as go
from process_data import get_unique_names
from import_gantic import gantic2pandas, create_weekly_tasks, name2fullname
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
                dcc.Graph(id='cummulative_timeline_project_planning')
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

# @app.callback(
#     Output('eng_name_dropdown', 'options'),
#     Input('store_raw_df', 'data')
# )
# def update_date_dropdown(raw_df):
#     if raw_df is not None:
#         df = pd.read_json(raw_df)
#         eng_name_list = get_unique_names(raw_df, 'Employee')
#         return [{'label': i, 'value': i} for i in eng_name_list]


@app.callback(
    Output('sunburst_engineer','figure'),
    Input('eng_name_dropdown', 'value'),
    Input('upload-data', 'contents'))
def update_sunburst_engineer(engineer_name, contents):

    # sec = get_sections('project_sections.dat')
    sec = get_project_sections_automatic(raw_df, proj_name_list)
    edf = raw_df[raw_df['Employee']==engineer_name].groupby(['Project','Hour or cost type']).sum()['Quantity']
    name = []
    section = []
    project = []
    hours = []
    hour_type = []

    for (p,t), hour in edf.items():
        name += [engineer_name]
        if p in sec:
            section += [sec[p]]
        else:
            section += ["Unkown"]
        project += [p]
        hour_type += [t]
        hours += [hour]
    newdf = pd.DataFrame(
    dict(project=project, hour_type=hour_type, section=section, name=name, hours=hours)
        )

    fig = px.sunburst(newdf, path=['name', 'section', 'project','hour_type'], values='hours')
    fig.update_layout(margin = dict(t=20, l=0, r=0, b=0))
    return fig


@app.callback(
    Output('sunburst_project','figure'),
    Input('proj_name_dropdown', 'value'))
def update_sunburst_project(project_name):

    # sec = get_sections('engineer_sections.dat')
    sec = get_engineer_sections_automatic(raw_df, eng_name_list)

    pdf = raw_df[raw_df['Project']==project_name].groupby(['Employee','Hour or cost type']).sum()['Quantity']
    name = []
    section = []
    project = []
    hours = []
    hour_type = []
    for (e,t), hour in pdf.items():
        project += [project_name]
        section += [sec[e]]
        name += [e]
        hour_type += [t]
        hours += [hour]
    newdf = pd.DataFrame(
    dict(project=project, hour_type=hour_type, section=section, name=name, hours=hours)
        )

    fig = px.sunburst(newdf, path=['project', 'hour_type', 'section', 'name'], values='hours')
    return fig


@app.callback(
    Output('timeline_engineer','figure'),
    Input('eng_name_dropdown', 'value'))
def update_engineer_timeline(engineer_name):
    edf = raw_df[raw_df['Employee']==engineer_name].groupby([raw_df['Date'].dt.strftime('%Y%W'),'Project']).sum()['Quantity']
    week = []
    project = []
    hours = []
    for (w,p), h in edf.items():
        week += [int(w)]
        project += [p]
        hours += [h]
    idx = np.argsort(week)
    week = list(np.array(week)[idx])
    project = list(np.array(project)[idx])
    hours = list(np.array(hours)[idx])

    val_week = np.sort(list(set(week)))
    text_week = [str(w)[4:]+'-'+str(w)[:4] for w in val_week]

    newdf = pd.DataFrame(
    dict(project=project, week=week, hours=hours)
        )
    fig = px.bar(newdf, x='week', y='hours', color='project')
    fig.update_layout(
    xaxis = dict(
        tickmode = 'array',
        tickvals = val_week,
        ticktext = text_week
        )
    )
    return fig

@app.callback(
    Output('timeline_project','figure'),
    Input('proj_name_dropdown', 'value'))
def update_project_timeline(project_name):
    edf = raw_df[raw_df['Project']==project_name].groupby([raw_df['Date'].dt.strftime('%Y%W'),'Employee']).sum()['Quantity']
    week = []
    employee = []
    hours = []
    for (w,e), h in edf.items():
        week += [int(w)]
        employee += [e]
        hours += [h]
    idx = np.argsort(week)
    week = list(np.array(week)[idx])
    employee = list(np.array(employee)[idx])
    hours = list(np.array(hours)[idx])

    val_week = np.sort(list(set(week)))
    text_week = [str(w)[4:]+'-'+str(w)[:4] for w in val_week]

    newdf = pd.DataFrame(
    dict(employee=employee, week=week, hours=hours)
        )
    fig = px.bar(newdf, x='week', y='hours', color='employee')
    fig.update_layout(
    xaxis = dict(
        tickmode = 'array',
        tickvals = val_week,
        ticktext = text_week
        )
    )
    return fig

@app.callback(
    Output('cummulative_timeline_project','figure'),
    Input('proj_name_dropdown', 'value'))
def update_cummulative_project_timeline(project_name):
    edf = raw_df[raw_df['Project']==project_name].groupby([raw_df['Date'].dt.strftime('%Y%W'),'Employee']).sum()['Quantity']
    week = []
    employee = []
    hours = []
    cum_hours = dict()
    total_hours = dict()

    for (w,e), h in edf.items():
        if e not in cum_hours.keys():
            cum_hours[e] = h
        else:
            cum_hours[e] += h

        week += [int(w)]
        employee += [e]
        hours += [cum_hours[e]]


        if int(w) not in total_hours:
            total_hours[int(w)] = h
        else:
            total_hours[int(w)] += h

    sorted_total_hours, sorted_total_week = [], []
    for w,h in total_hours.items():
        sorted_total_week += [w]
        sorted_total_hours += [h]

    idx = np.argsort(sorted_total_week)
    sorted_total_week = list(np.array(sorted_total_week)[idx])
    sorted_total_hours = list(np.cumsum(np.array(sorted_total_hours)[idx]))

    week += sorted_total_week
    hours += sorted_total_hours
    employee += ['Total']*len(sorted_total_week)


    idx = np.argsort(week)
    week = list(np.array(week)[idx])
    employee = list(np.array(employee)[idx])
    hours = list(np.array(hours)[idx])

    val_week = np.sort(list(set(week)))
    text_week = [str(w)[4:]+'-'+str(w)[:4] for w in val_week]
    

    newdf = pd.DataFrame(
    dict(employee=employee, week=week, hours=hours)
        )
    fig = px.line(newdf, x='week', y='hours', color='employee', markers=True)
    fig.update_layout(
    xaxis = dict(
        tickmode = 'array',
        tickvals = val_week,
        ticktext = text_week
        )
    )
    return fig



@app.callback(
    Output('cummulative_timeline_project_planning','figure'),
    Input('proj_name_dropdown', 'value'))
def update_cummulative_project_timeline_project(project_name):


    edf = gantic_weekly_tasks[gantic_weekly_tasks['Project']==project_name]
    total_cumsum = edf.groupby(['Week']).sum().cumsum()['Quantity']
    edf['Employee_cumsum'] = edf.groupby(['Employee'])['Quantity'].cumsum()
    
    week = []
    employee = []
    hours = []

    for item in edf.values.tolist():
        _employee, _week, _, _, _, _cumsum = item
        week += [_week]
        employee += [_employee]
        hours += [_cumsum]

    employee += ['Total']*len(total_cumsum)
    week += total_cumsum.index.tolist()
    hours += total_cumsum.values.tolist()

    val_week = np.sort(list(set(week)))
    text_week = [str(w)[4:]+'-'+str(w)[:4] for w in val_week]
    

    newdf = pd.DataFrame(
    dict(employee=employee, week=week, hours=hours)
        )
    fig = px.line(newdf, x='week', y='hours', color='employee', markers=True)
    fig.update_layout(
    xaxis = dict(
        tickmode = 'array',
        tickvals = val_week,
        ticktext = text_week
        )
    )
    return fig



@app.callback(
    Output('timeline_engineer_prod','figure'),
    Input('eng_name_dropdown', 'value'))
def update_timeline_engineer_prod(engineer_name):
    edf = raw_df[raw_df['Employee']==engineer_name].groupby([raw_df['Date'].dt.strftime('%W'),'Item group']).sum()['Quantity']



    week = []
    hour_type = []
    hours = []
    cum_hours = dict()
    total_hours = dict()
    core_hours = dict()

    for (w,ht), h in edf.items():

        if ht not in cum_hours.keys():
            cum_hours[ht] = h
        else:
            cum_hours[ht] += h

        week += [int(w)]
        hour_type += [ht]
        hours += [cum_hours[ht]]

        if 'Core' in ht:
            if int(w) not in core_hours:
                core_hours[int(w)] = h
            else:
                core_hours[int(w)] += h            

        if int(w) not in total_hours:
            total_hours[int(w)] = h
        else:
            total_hours[int(w)] += h

    for w, _ in total_hours.items():
        if w not in core_hours.keys():
            core_hours[w] = 0
            


    sorted_total_hours, sorted_total_week = [], []
    for w,h in total_hours.items():
        sorted_total_week += [w]
        sorted_total_hours += [h]

    sorted_core_hours, sorted_core_week = [], []
    for w,h in core_hours.items():
        sorted_core_week += [w]
        sorted_core_hours += [h]


    idx = np.argsort(sorted_total_week)
    sorted_total_week = list(np.array(sorted_total_week)[idx])
    sorted_total_hours = list(np.cumsum(np.array(sorted_total_hours)[idx]))

    idx = np.argsort(sorted_core_week)
    sorted_core_week = list(np.array(sorted_core_week)[idx])
    sorted_core_hours = list(np.cumsum(np.array(sorted_core_hours)[idx]))

    sorted_productivity = [(c/t)*100 for c,t in zip(sorted_core_hours,sorted_total_hours)]

    week = sorted_total_week + sorted_core_week + sorted_core_week
    hours = sorted_total_hours + sorted_core_hours + sorted_productivity
    hour_type = ['Total']*len(sorted_total_week) + ['Core']*len(sorted_core_week) + ['Prod']*len(sorted_core_week)

    week = sorted_core_week
    hours =  sorted_productivity
    hour_type = ['Prod']*len(sorted_core_week)

    idx = np.argsort(week)
    week = list(np.array(week)[idx])
    hour_type = list(np.array(hour_type)[idx])
    hours = list(np.array(hours)[idx])


    val_week = np.sort(list(set(week)))
    text_week = [str(w)[:4] for w in val_week]

    newdf = pd.DataFrame(
    dict(hour_type=hour_type, week=week, productivity=hours))

    fig = px.line(newdf, x='week', y='productivity', markers=True)


    fig.update_layout(
    xaxis = dict(
        tickmode = 'array',
        tickvals = val_week,
        ticktext = text_week,
        showline=True,
        showgrid=True,
        showticklabels=True,
        linecolor='rgb(204, 204, 204)',
        linewidth=2,
        ticks='outside',
        tickfont=dict(
            family='Arial',
            size=12,
            color='rgb(82, 82, 82)',
        ),
    ),

    yaxis=dict(
        showgrid=True,
        zeroline=True,
        showline=True,
        showticklabels=True,
    ),
    autosize=False,
    margin=dict(
        autoexpand=False,
        l=100,
        r=20,
        t=110,
    ),
    showlegend=False,
    plot_bgcolor='white'
)

    fig.update_yaxes(range=[0, 102])
    return fig

@app.callback(
    Output('timeline_hours_percentage', 'figure'),
    Input('manager_name_dropdown','value'))
def update_timeline_hours_percentage(manager_name):
    if manager_name in manager_name_list:
        edf = raw_df[raw_df['Manager']==manager_name].groupby([raw_df['Date'].dt.strftime('%W'),'Item group']).sum()['Quantity']
    elif manager_name == 'Total':
        edf = raw_df.groupby([raw_df['Date'].dt.strftime('%W'),'Item group']).sum()['Quantity']
    elif manager_name == 'Total-RSE':
        edf = raw_df[ (raw_df['Manager'] == 'Yifat Dzigan') |  (raw_df['Manager'] == 'Nicolas Renaud') | (raw_df['Manager'] == 'Michiel Punt') | (raw_df['Manager'] == 'Valentina Azzara')].groupby([raw_df['Date'].dt.strftime('%W'),'Item group']).sum()['Quantity']

    week = []
    project = []
    hours = []
    for (w,p), h in edf.items():
        week += [int(w)]
        project += [p]
        hours += [h]
    idx = np.argsort(week)
    week = list(np.array(week)[idx])
    project = list(np.array(project)[idx])
    hours = list(np.array(hours)[idx])

    val_week = np.sort(list(set(week)))
    # text_week = [str(w)[4:]+'-'+str(w)[:4] for w in val_week]
    text_week = [str(w)[:4] for w in val_week]

    newdf = pd.DataFrame(
    dict(project=project, week=week, hours=hours)
        )
    fig = px.bar(newdf, x='week', y='hours', color='project')
    fig.update_layout(
    xaxis = dict(
        tickmode = 'array',
        tickvals = val_week,
        ticktext = text_week
        )
    )
    return fig

@app.callback(
    Output('timeline_productivity','figure'),
    Input('manager_name_dropdown', 'value'),
    Input('select_data', 'value'))
def update_producitity_development(manager_name, select_data):

    if manager_name in manager_name_list:
        edf = raw_df[raw_df['Manager']==manager_name].groupby([raw_df['Date'].dt.strftime('%W'),'Item group']).sum()['Quantity']
    elif manager_name == 'Total':
        edf = raw_df.groupby([raw_df['Date'].dt.strftime('%W'),'Item group']).sum()['Quantity']
    elif manager_name == 'Total-RSE':
        edf = raw_df[ (raw_df['Manager'] == 'Yifat Dzigan') |  (raw_df['Manager'] == 'Nicolas Renaud') | (raw_df['Manager'] == 'Michiel Punt') | (raw_df['Manager'] == 'Valentina Azzara')].groupby([raw_df['Date'].dt.strftime('%W'),'Item group']).sum()['Quantity']

    week = []
    hour_type = []
    hours = []
    cum_hours = dict()
    total_hours = dict()

    for (w,ht), h in edf.items():
        if ht not in cum_hours.keys():
            cum_hours[ht] = h
        else:
            cum_hours[ht] += h

        week += [int(w)]
        hour_type += [ht]
        hours += [cum_hours[ht]]


        if int(w) not in total_hours:
            total_hours[int(w)] = h
        else:
            total_hours[int(w)] += h

    sorted_total_hours, sorted_total_week = [], []
    for w,h in total_hours.items():
        sorted_total_week += [w]
        sorted_total_hours += [h]

    idx = np.argsort(sorted_total_week)
    sorted_total_week = list(np.array(sorted_total_week)[idx])
    sorted_total_hours = list(np.cumsum(np.array(sorted_total_hours)[idx]))

    week += sorted_total_week
    hours += sorted_total_hours
    hour_type += ['Total']*len(sorted_total_week)


    idx = np.argsort(week)
    week = list(np.array(week)[idx])
    hour_type = list(np.array(hour_type)[idx])
    hours = list(np.array(hours)[idx])

    val_week = np.sort(list(set(week)))
    # text_week = [str(w)[4:]+'-'+str(w)[:4] for w in val_week]
    text_week = [str(w)[:4] for w in val_week]

    newdf = pd.DataFrame(
    dict(hour_type=hour_type, week=week, hours=hours)
        )

    if select_data == ['Projection']:

        all_weeks = list(range(1,53))
        n_all_week = len(all_weeks)
        proj_hour_type = []
        proj_hours = []
        proj_week = []

        for ht in set(hour_type):

            week_ht = np.array(week)[np.array(hour_type)==ht]

            hours_ht = np.array(hours)[np.array(hour_type)==ht]
            p = np.poly1d(np.polyfit(week_ht, hours_ht, 1))
            proj_hour_type += [ht+'_proj']*n_all_week
            proj_week += all_weeks
            proj_hours += list(p(all_weeks))

        val_week = np.sort(list(set(all_weeks)))
        # text_week = [str(w)[4:]+'-'+str(w)[:4] for w in val_week]
        text_week = [str(w)[:4] for w in val_week]

        newdf = pd.DataFrame(
        dict(hour_type=proj_hour_type, week=proj_week, hours=proj_hours)
            )
    fig = px.line(newdf, x='week', y='hours', color='hour_type', markers=True)
    fig.update_layout(
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
        ),
        xaxis = dict(
            tickmode = 'array',
            tickvals = val_week,
            ticktext = text_week
            )
    )
    return fig



@app.callback(
    Output('sunburst_section','figure'),
    Input('manager_name_dropdown', 'value'))
def update_sunburst_section(manager_name):

    if manager_name in manager_name_list:
        edf = raw_df[raw_df['Manager']==manager_name].groupby(['Project','Item group','Hour or cost type','Employee']).sum()['Quantity']
    elif manager_name == 'Total':
        edf = raw_df.groupby(['Project','Item group','Hour or cost type','Employee']).sum()['Quantity']
    elif manager_name == 'Total-RSE':
        edf = raw_df[ (raw_df['Manager'] == 'Yifat Dzigan') |  (raw_df['Manager'] == 'Nicolas Renaud') | (raw_df['Manager'] == 'Lars Ridder') | (raw_df['Manager'] == 'Valentina Azzara')].groupby(['Project','Item group','Hour or cost type','Employee']).sum()['Quantity']
    else:
        edf = raw_df.groupby(['Project','Item group','Hour or cost type','Employee']).sum()['Quantity']

    section = []
    project = []
    employee = []
    hours = []
    item_group = []
    hour_type = []

    for (p,ig,t,e), hour in edf.items():
        employee += [e]
        section += [manager_name]
        project += [p]
        hour_type += [t]
        item_group += [ig]
        hours += [hour]
    newdf = pd.DataFrame(
    dict(project=project, item_group=item_group, hour_type=hour_type, section=section, employee=employee, hours=hours)
        )

    fig = px.sunburst(newdf, path=['section', 'item_group', 'hour_type', 'employee'], values='hours')
    fig.update_layout(margin = dict(t=20, l=0, r=0, b=0))
    return fig




def get_sections(filename):
    section = np.loadtxt(filename, delimiter=', ', dtype=str)
    d = dict()
    for s in section:
        d[s[0]] = s[1]
    return d

def get_engineer_sections_automatic(raw_df, names):

    d = dict()
    for n in names:
        d[n] = raw_df[raw_df['Employee']==n]['Manager'].unique()[-1]
    return d
    
def get_project_sections_automatic(raw_df, names):
    d = dict()
    for n in names:
        try:
            d[n] = raw_df[raw_df['Project']==n]['Project manager'].unique()[-1]
        except:
            d[n] = 'Unkown'
    return d


if __name__ == '__main__':
    

    def open_browser():
        webbrowser.open_new("http://localhost:{}".format(port))

    port = 8050
    Timer(1, open_browser).start()
    app.run_server(debug=True, port=port)
    # app.run_server(debug=False)
