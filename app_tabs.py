import base64
import datetime
import io

import dash
from dash.dependencies import Input, Output, State
from dash import dcc, html, dash_table
import plotly.express as px
from process_data import get_unique_names
from process_data import plot_engineer_sunburst_raw
import numpy as np
import pandas as pd



external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

fname = "hours2021.xlsx"
fname = "hoursJanFeb2022.xlsx"
raw_df = pd.read_excel(fname)

eng_name_list = get_unique_names(raw_df, 'Employee')
proj_name_list = get_unique_names(raw_df, 'Project')
manager_name_list = get_unique_names(raw_df, 'Manager') 



app = dash.Dash(__name__, external_stylesheets=external_stylesheets)



app.title = "eScience Data Xplorer"

server = app.server

app_color = {"graph_bg": "#082255", "graph_line": "#007ACE"}

app.layout = html.Div([

    dcc.Tabs([
        dcc.Tab(label='Engineer', children=[
            dcc.Dropdown(eng_name_list, eng_name_list[0], id='eng_name_dropdown', style={'width': '50%'}),
            html.Div([
                dcc.Graph(id='sunburst_engineer', style={'display': 'inline-block'}),
                dcc.Graph(id='sunburst_engineer_prod', style={'display': 'inline-block'}), 
                dcc.Graph(id='timeline_engineer')]),
        ]),
        dcc.Tab(label='Project', children=[
            dcc.Dropdown(proj_name_list, proj_name_list[0], id='proj_name_dropdown', style={'width': '50%'}),
            html.Div([dcc.Graph(id='sunburst_project'), dcc.Graph(id='timeline_project'), dcc.Graph(id='cummulative_timeline_project')]),
        ]),
        dcc.Tab(label='Section', children=[
            dcc.Dropdown(manager_name_list+ ['Total'], manager_name_list[0], id='manager_name_dropdown', style={'width': '50%'}),
            html.Div([
                dcc.Graph(id='sunburst_section', style={'display': 'inline-block'}),
                dcc.Checklist(['Projection'], [], id='select_data', inline=True),
                dcc.Graph(id='timeline_productivity')]),
        ]),
    ])
])





@app.callback(
    Output('sunburst_engineer','figure'),
    Input('eng_name_dropdown', 'value'))
def update_sunburst_engineer(engineer_name):

    # sec = get_sections('project_sections.dat')
    sec = get_project_sections_automatic(raw_df,proj_name_list)
    edf = raw_df[raw_df['Employee']==engineer_name].groupby(['Project','Hour or cost type']).sum()['Quantity']
    name = []
    section = []
    project = []
    hours = []
    hour_type = []

    for (p,t), hour in edf.items():
        name += [engineer_name]
        section += [sec[p]]
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
    edf = raw_df[raw_df['Employee']==engineer_name].groupby([raw_df['Date'].dt.strftime('%W'),'Project']).sum()['Quantity']
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
    newdf = pd.DataFrame(
    dict(project=project, week=week, hours=hours)
        )
    fig = px.bar(newdf, x='week', y='hours', color='project')
    return fig

@app.callback(
    Output('timeline_project','figure'),
    Input('proj_name_dropdown', 'value'))
def update_project_timeline(project_name):
    edf = raw_df[raw_df['Project']==project_name].groupby([raw_df['Date'].dt.strftime('%W'),'Employee']).sum()['Quantity']
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
    newdf = pd.DataFrame(
    dict(employee=employee, week=week, hours=hours)
        )
    fig = px.bar(newdf, x='week', y='hours', color='employee')
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
    Output('sunburst_engineer_prod','figure'),
    Input('eng_name_dropdown', 'value'))
def update_sunburst_engineer_prod(engineer_name):


    bill = []
    name = []
    hour_type = []
    hours = []
    total_billable = 0
    total_nonbillable = 0
    edf = raw_df[raw_df['Employee']==engineer_name].groupby(['Item group', 'Hour or cost type']).sum()['Quantity']


    try:
        core_proc = edf['0001 - Core Process']
        for k in core_proc.keys():

            name += [engineer_name]
            bill += ['billable']
            hour_type += [k]
            hours += [core_proc[k]]
            total_billable += core_proc[k]
    except:
        pass

    try:
        core_proc = edf['0005 - Core Hours']
        for k in core_proc.keys():

            name += [engineer_name]
            bill += ['billable']
            hour_type += [k]
            hours += [core_proc[k]]
            total_billable += core_proc[k]
    except:
        pass

    try:
        core_proc = edf['0003 - Support Process']
        for k in core_proc.keys():
            # if k not in ['Holiday', 'Public Holidays']:
            name += [engineer_name]
            bill += ['non billable']
            hour_type += [k]
            hours += [core_proc[k]]
            total_nonbillable += core_proc[k]

    except:
        pass

    prod = total_nonbillable / (total_billable + total_nonbillable)
    name = [n + '\n' + str(prod)[:4] for n in name]
    newdf = pd.DataFrame(
    dict(name=name, bill=bill, hour_type=hour_type, hours=hours)
        )

    fig = px.sunburst(newdf, path=['name', 'bill', 'hour_type'], values='hours')
    fig.update_layout(margin = dict(t=20, l=0, r=0, b=0))
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
        text_week = [str(w)[:4] for w in val_week]

        newdf = pd.DataFrame(
        dict(hour_type=proj_hour_type, week=proj_week, hours=proj_hours)
            )
    fig = px.line(newdf, x='week', y='hours', color='hour_type', markers=True)
    fig.update_layout(
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
        d[n] = raw_df[raw_df['Project']==n]['Project manager'].unique()[-1]
    return d


if __name__ == '__main__':
    app.run_server(debug=True)