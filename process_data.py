import pandas as pd
import numpy as np
import networkx as nx
import plotly.express as px
import plotly.graph_objects as go

def get_unique_names(df, colname):
    names = list(df[colname])
    names = list(set(names))
    names.pop(names=='NaN')
    names.pop(names=='nan')
    names.pop(names==float('NaN'))
    return  names



def extract_data(df):

    # df = pd.read_excel(filename)
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


def plot_engineer_sunburst_raw(df, engineer_name):


    sec = get_sections('project_sections.dat')
    edf = df[df['Employee']==engineer_name].groupby(['Project','Hour or cost type']).sum()['Quantity']
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
    fig.show()
    return newdf



def plot_project_sunburst_raw(df, project_name):

    sec = get_sections('engineer_sections.dat')
    pdf = df[df['Project']==project_name].groupby(['Employee','Hour or cost type']).sum()['Quantity']
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
    fig.show()
    return newdf



# def plot_engineer_sunburst(df, engineer_name):

#     sec = get_sections('project_sections.dat')
#     tmp  = df[df.index==engineer_name]
#     name = []
#     section = []
#     project = []
#     hours = []


#     for p in tmp.keys():
#         hour = list(tmp[p])[0]
#         if hour > 0:
#             name += [engineer_name]
#             section += [sec[p]]
#             project += [p]

#             hours += [hour]
#     newdf = pd.DataFrame(
#     dict(project=project, section=section, name=name, hours=hours)
#         )

#     fig = px.sunburst(newdf, path=['name', 'section', 'project','hour_type'], values='hours')
#     fig.show()

# def plot_project_sunburst(df, project_name):

#     sec = get_sections('engineer_sections.dat')
#     tmp  = df[project_name]
#     name = []
#     section = []
#     project = []
#     hours = []
#     for e in tmp.index:
#         hour = tmp[e]
#         if hour > 0:
#             project += [project_name]
#             section += [sec[e]]
#             name += [e]
#             hours += [hour]
#     newdf = pd.DataFrame(
#     dict(project=project, section=section, name=name, hours=hours)
#         )

#     fig = px.sunburst(newdf, path=['project', 'section', 'name'], values='hours')
#     fig.show()


def plot_sankey_section(odf):

    df = extract_data(odf)

    eng_sec = get_sections('engineer_sections.dat')
    proj_sec = get_sections('project_sections.dat')

    employees = list(df.index)
    projects = list(df.keys())

    eng_sec_name = ["LS", "SSH", "NS", "ES"]
    proj_sec_name = ["LS", "SSH", "NS", "ES", "Other"]

    hours_data = df.to_numpy()
    data = np.zeros((4,5))

    for ie, e in enumerate(employees):
        for ip, p in enumerate(projects):
            if hours_data[ie,ip] > 0:
                esec = eng_sec[e]
                psec = proj_sec[p]

                if esec not in eng_sec_name:
                    continue
                if psec not in proj_sec_name:
                    continue

                iesec = eng_sec_name.index(esec)
                ipsec = proj_sec_name.index(psec)

                data[iesec, ipsec] +=  hours_data[ie,ip]


    data = list(data.flatten())
    source = [0]*5 + [1]*5 + [2]*5 + [3]*5 + [4]*5
    target = [4,5,6,7,8]*5

    fig = go.Figure(data=[go.Sankey(
        node = dict(
        pad = 15,
        thickness = 20,
        line = dict(color = "black", width = 0.5),
        label = ["Life", "SSH", "Nat", "Env", "Life", "SSH", "Nat", "Env", "Other"]
        ),
        link = dict(
        source = source,
        target = target,
        value = data
    ))])

    fig.update_layout(title_text="Basic Sankey Diagram", font_size=10)
    fig.show()


if __name__ == "__main__":
    # df = extract_data("exactdump_6month.xlsx")
    df = pd.read_excel("exactdump_6month.xlsx")
    ndf = plot_engineer_sunburst_raw(df, 'Nicolas Renaud')
    # plot_project_sunburst(df, 'EUCP H2020 - EUropean Climate Prediction system')