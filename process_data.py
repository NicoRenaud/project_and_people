import pandas as pd
import numpy as np
import networkx as nx
import plotly.express as px

def get_unique_names(df, colname):
    names = list(df[colname])
    names = list(set(names))
    names.pop(names=='NaN')
    names.pop(names=='nan')
    return  names


def extract_data(filename):

    df = pd.read_excel(filename)
    employees = get_unique_names(df, 'Employee')
    projects = get_unique_names(df, 'Project')
    nemployee = len(employees)
    nproject = len(projects)

    out = pd.DataFrame(np.zeros((nemployee, nproject)), index=employees, columns=projects)

    for e in employees:
        proj = list(df.loc[df['Employee']==e]['Project'])
        hours = list(df.loc[df['Employee']==e]['Quantity'])
        for p,h in zip(proj,hours):
            if p not in projects:
                continue
            if e not in employees:
                continue
            out[p][e] += h

    return out

def create_graph(df):
    employees = list(df.index)
    projects = list(df.keys())
    data = df.to_numpy()
    data /= data.sum(1).reshape(-1,1)

    g = nx.Graph()
    for e in employees:
        g.add_node(e)

    for p in projects:
        g.add_node(p)

    for ie, e in enumerate(employees):
        for ip, p in enumerate(projects):
            if data[ie,ip] > 0:
                g.add_edge(e,p,weight=data[ie,ip])

    return g

def get_sections(filename):
    section = np.loadtxt(filename, delimiter=', ', dtype=str)
    d = dict()
    for s in section:
        d[s[0]] = s[1]
    return d

def plot_engineer_sunburst(df, engineer_name):

    sec = get_sections('project_sections.dat')
    tmp  = df[df.index==engineer_name]
    name = []
    section = []
    project = []
    hours = []
    for p in tmp.keys():
        hour = list(tmp[p])[0]
        if hour > 0:
            name += [engineer_name]
            section += [sec[p]]
            project += [p]

            hours += [hour]
    newdf = pd.DataFrame(
    dict(project=project, section=section, name=name, hours=hours)
        )

    fig = px.sunburst(newdf, path=['name', 'section', 'project'], values='hours')
    fig.show()

def plot_project_sunburst(df, project_name):

    sec = get_sections('engineer_sections.dat')
    tmp  = df[project_name]
    name = []
    section = []
    project = []
    hours = []
    for e in tmp.index:
        hour = tmp[e]
        if hour > 0:
            project += [project_name]
            section += [sec[e]]
            name += [e]
            hours += [hour]
    newdf = pd.DataFrame(
    dict(project=project, section=section, name=name, hours=hours)
        )

    fig = px.sunburst(newdf, path=['project', 'section', 'name'], values='hours')
    fig.show()



if __name__ == "__main__":
    df = extract_data("exactdump_6month.xlsx")
    # g = create_graph(df)
    # nx.draw(g)
    # plot_engineer_sunburst(df, 'Yidat Dzigan')
    plot_project_sunburst(df, 'EUCP H2020 - EUropean Climate Prediction system')