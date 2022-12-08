import numpy as np 
import plotly.express as px
import pandas as pd

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


def create_sunburst_engineer(raw_df, engineer_name, proj_name_list):

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

def create_engineer_timeline(raw_df, engineer_name):
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

def create_sunburst_project(raw_df, project_name, eng_name_list):

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


def create_project_timeline(raw_df, project_name):
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

def create_cummulative_project_timeline(raw_df, project_name):
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