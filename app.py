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
raw_df = pd.read_excel("hours2021.xlsx")
eng_name_list = get_unique_names(raw_df, 'Employee')
proj_name_list = get_unique_names(raw_df, 'Project')
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)



app.title = "eScience Data Xplorer"

server = app.server

app_color = {"graph_bg": "#082255", "graph_line": "#007ACE"}

app.layout = html.Div([


        # header
        html.Div(
            [
                html.Div(
                    [
                        html.H1("eScience Data Explorer", className="app__header__title"),
                    ],
                    className="app__header__desc",
                ),
            ],
            className="app__header",
        ),

    dcc.Dropdown(eng_name_list, eng_name_list[0], id='eng_name_dropdown', style={'width': '50%'}),
    html.Div([dcc.Graph(id='sunburst_engineer'), dcc.Graph(id='timeline_engineer')]),
    dcc.Dropdown(proj_name_list, proj_name_list[0], id='proj_name_dropdown', style={'width': '50%'}),
    html.Div([dcc.Graph(id='sunburst_project'), dcc.Graph(id='timeline_project'), dcc.Graph(id='cummulative_timeline_project')]),
])

def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])


@app.callback(
    Output('sunburst_engineer','figure'),
    Input('eng_name_dropdown', 'value'))
def update_sunburst_engineer(engineer_name):

    sec = get_sections('project_sections.dat')
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
    return fig


@app.callback(
    Output('sunburst_project','figure'),
    Input('proj_name_dropdown', 'value'))
def update_sunburst_project(project_name):

    sec = get_sections('engineer_sections.dat')
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
    edf = raw_df[raw_df['Project']==project_name].groupby([raw_df['Date'].dt.strftime('%W'),'Employee']).sum()['Quantity']
    week = []
    employee = []
    hours = []
    cum_hours = dict()
    cum_hours['total'] = 0
    for (w,e), h in edf.items():
        if e not in cum_hours.keys():
            cum_hours[e] = h
        else:
            cum_hours[e] += h

        week += [int(w)]
        employee += [e]
        hours += [cum_hours[e]]

    idx = np.argsort(week)
    week = list(np.array(week)[idx])
    employee = list(np.array(employee)[idx])
    hours = list(np.array(hours)[idx])
    newdf = pd.DataFrame(
    dict(employee=employee, week=week, hours=hours)
        )
    fig = px.line(newdf, x='week', y='hours', color='employee',markers=True)
    return fig


def get_sections(filename):
    section = np.loadtxt(filename, delimiter=', ', dtype=str)
    d = dict()
    for s in section:
        d[s[0]] = s[1]
    return d

if __name__ == '__main__':
    app.run_server(debug=True)