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

def create_timeline_engineer_prod(raw_df, engineer_name):
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