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


def create_timeline_hours_percentage(raw_df, manager_name, manager_name_list):
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

def create_producitity_development(raw_df, manager_name, manager_name_list, select_data):

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



def create_sunburst_section(raw_df, manager_name, manager_name_list):

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
