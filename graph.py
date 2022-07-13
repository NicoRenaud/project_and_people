import numpy as np
import pandas as pd
import networkx as nx
import plotly.graph_objects as go

from pyvis.network import Network

fname = "HoursJanMay2022.xlsx"
raw_df = pd.read_excel(fname)

df = raw_df.groupby(['Employee','Project','Hour or cost type']).sum()['Quantity']

G0 = nx.Graph()

ignore_proj = ['Other personnel related costs', 'Work council', 'Acquisition', 
               'Call Activities', 'Communication','Knowledge Development', 'Operations & Support',
               'Line management and internal strategy','Parental Leave','Personal development (not project related)','Dissemination & Community']
ignore_emp = ['Nicolas Renaud', 'Yifat Dzigan', 'Willem van Hage','Rob van Nieuwpoort',
              'Rena Bakhshi','Pablo Lopez-Tarifa','Niels Drost','Lars Ridder','Jisk Attema','Patrick Bos',
              'Maria Chertova', 'Jesús Garcia González']
for (emp, proj, _), hours in df.items():
    
    if proj not in ignore_proj:
        if emp not in ignore_emp:
            G0.add_node(emp, type='rse')
            G0.add_node(proj, type='project')
            G0.add_edge(emp,proj,weight=hours)

# G = G0

G = nx.Graph()

for n,attr in G0.nodes.data():

    if attr['type']=='project':
        e = list(G0.edges(n))
        nedge = len(e)
        for ie in range(nedge-1):
            eng1 = e[ie][1]
            for iie in range(1,nedge):
                eng2 = e[iie][1]

                G.add_node(eng1)
                G.add_node(eng2)
                
                w1 = G0.get_edge_data(eng1,n)['weight']
                w2 = G0.get_edge_data(eng2,n)['weight']
                w = w1+w2
                if w>1E2:
                    w = np.exp(0.001*w)-1
                    G.add_edge(eng1,eng2,weight=w)


# G.add_edge('Artur Palha Da Silva Clerigo', 'Luisa Orozco', weight = np.exp(0.001*1E2)-1)
# G.add_edge('Johan Hidding', 'Hanno Spreeuw', weight = np.exp(0.001*1E2)-1)
# G.add_edge('Stef Smeets', 'Victor Azizi Tarksalooyeh', weight = np.exp(0.001*1E2)-1)



g = Network()
g = Network(height='800px', width='100%',heading='',bgcolor='black',font_color="white")
# g.barnes_hut()
g.from_nx(G)

g.show_buttons(filter_=['physics'])
g.show('graph.html')



if 0:

    pos = nx.spring_layout(G, iterations=500)


    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]

        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines')

    node_x = []
    node_y = []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        marker=dict(
            showscale=True,
            # colorscale options
            #'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
            #'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
            #'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
            colorscale='YlGnBu',
            reversescale=True,
            color=[],
            size=10,
            colorbar=dict(
                thickness=15,
                title='Node Connections',
                xanchor='left',
                titleside='right'
            ),
            line_width=2))


    node_adjacencies = []
    node_text = []
    for node, attr in G.nodes.data():
        try:
            if attr['type'] == 'rse':  
                node_adjacencies.append(0)
            else:
                node_adjacencies.append(1)
        except:
            node_adjacencies.append(0)
        node_text.append(node)

    node_trace.marker.color = node_adjacencies
    node_trace.text = node_text


    node_adjacencies = []
    node_text = []
    for node, adjacencies in enumerate(G.adjacency()):
        node_adjacencies.append(len(adjacencies[1]))
        node_text.append(adjacencies[0] + ' #'+str(len(adjacencies[1])))

    node_trace.marker.color = node_adjacencies
    node_trace.text = node_text

    fig = go.Figure(data=[edge_trace, node_trace],
                layout=go.Layout(
                    title='<br>Network graph made with Python',
                    titlefont_size=16,
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20,l=5,r=5,t=40),
                    annotations=[ dict(
                        text="Python code: <a href='https://plotly.com/ipython-notebooks/network-graphs/'> https://plotly.com/ipython-notebooks/network-graphs/</a>",
                        showarrow=False,
                        xref="paper", yref="paper",
                        x=0.005, y=-0.002 ) ],
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                    )
    fig.show()


