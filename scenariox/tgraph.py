#!/usr/bin/env python3
import matplotlib.pyplot as plt
import networkx as nx
import random

class TGraph():
    sg = None
    sm = None
    times = None
    complet = None
    aligned = None
    actors = None
    channels = None
    colors = None
    instance = None
    
    def __init__(self, scenario_graph, scenario_metadata, comms = ['email', 'phone', 'travel']):
        self.sg = scenario_graph
        self.sm = scenario_metadata
        self.channels = comms
        self.RanDWalk()
        self.TemporalAlignment()
        self.GenActors()
        self.GenGraph()
        self.ColorGraph()
        
    def RanDWalk(self):
        p_complet = []
        p_times = {}
        tgraphs = []
        def recurproc(node, time):
            nonlocal p_complet
            nonlocal p_times
            if node not in p_complet:
                if self.sg.node[node]['type'] == 'parallel_gateway':
                    deps = [i for i in self.sg.predecessors(node) if self.sg.node[i]['type'] == 'task']
                    if set(deps).issubset(p_complet):
                        p_complet.append(node)
                        p_times[node] = time if node not in p_times.keys() or p_times[node] < time else p_times[node]
                        [recurproc(i, p_times[node]) for i in self.sg.successors(node)]
                elif self.sg.node[node]['type'] == 'subprocess':
                    deps = [i for i in self.sg.predecessors(node) if self.sg.node[i]['type'] == 'task']
                    if set(deps).issubset(p_complet):
                        p_complet.append(node)
                        p_times[node] = time if node not in p_times.keys() or p_times[node] < time else p_times[node]
                        [recurproc(i, p_times[node]) for i in self.sg.successors(node)]
                elif self.sg.node[node]['type'] == 'task':
                    p_complet.append(node)
                    p_times[node] = time if node not in p_times.keys() or p_times[node] < time else p_times[node]
                    if len(list(self.sg.successors(node))) > 0:
                        nextnode = list(self.sg.successors(node))[0] 
                        p_times[nextnode] = time + 1 if nextnode not in p_times.keys() or p_times[nextnode] < time else p_times[nextnode]
                        recurproc(nextnode, p_times[nextnode])

        recurproc('root', 0)
        self.times = p_times
        self.complet = p_complet
        return self

    def TemporalAlignment(self):
        tasks = {}
        if self.times == None or self.complet == None:
            return self
        for i in self.times.keys():
            if self.sg.node[i]['type'] == 'task':
                tasks[self.times[i]] = [[i, self.sm.phases[i].duration]] if self.times[i] not in tasks.keys() else tasks[self.times[i]] + [[i, self.sm.phases[i].duration]]
                
        offset = 0
        assigned = {}
        for i in sorted(tasks.keys()):
            ctasks = sorted(tasks[i], key=lambda x: x[1]['max'], reverse = True)
            nmax = ctasks[0][1]['max']
            for j in ctasks:
                assigned[j[0]] = {'min' : (nmax - (j[1]['max'] - j[1]['min'])) + offset, 'max' : nmax + offset}
            offset += nmax

        self.aligned = assigned
        return self

    def GenActors(self):
        actors = {}
        for k, v in self.sm.phases.items():
            if k != 'root':
                for j in v.comms:
                    if j['p1_title'] not in actors:
                        actors[j['p1_title']] = {'min' : j['p1_range'][0], 'max' : j['p1_range'][1]}
                    else:
                        actors[j['p1_title']]['min'] = j['p1_range'][0] if j['p1_range'][0] > actors[j['p1_title']]['min'] else actors[j['p1_title']]['min']
                        actors[j['p1_title']]['max'] = j['p1_range'][1] if j['p1_range'][1] > actors[j['p1_title']]['max'] else actors[j['p1_title']]['max']
                    if j['p2_title'] not in actors:
                        actors[j['p2_title']] = {'min' : j['p2_range'][0], 'max' : j['p2_range'][1]}
                    else:
                        actors[j['p2_title']]['min'] = j['p2_range'][0] if j['p2_range'][0] > actors[j['p2_title']]['min'] else actors[j['p2_title']]['min']
                        actors[j['p2_title']]['max'] = j['p2_range'][1] if j['p2_range'][1] > actors[j['p2_title']]['max'] else actors[j['p2_title']]['max']
        for i in actors.keys():
            actors[i]['sample'] = random.randint(actors[i]['min'], actors[i]['max'])
        self.actors = actors
        return self

    def GenGraph(self):
        if self.actors == None or self.aligned == None:
            return self
        G = nx.MultiDiGraph()

        for k, v in self.actors.items():
            for i in range(v['sample']):
                G.add_node(k + '_' + str(i))
        
        for k, v in self.sm.phases.items():
            if k != 'root':
                for i in v.comms:
                    if i['channel'] in self.channels:
                        for j in range(i['comms_range'][0], i['comms_range'][1]):
                            transdate = random.randint(self.aligned[k]['min'], self.aligned[k]['max'])
                            for a in range(random.randint(i['p1_range'][0], self.actors[i['p1_title']]['sample'])):
                                for b in range(random.randint(i['p2_range'][0], self.actors[i['p2_title']]['sample'])):
                                    sender = i['p1_title'] + '_' + str(random.randint(0, self.actors[i['p1_title']]['sample']-1))
                                    receiver = i['p2_title'] + '_' + str(random.randint(0, self.actors[i['p2_title']]['sample']-1))
                                    if i['direction'] == 'to':
                                        G.add_edge(sender, receiver, date = transdate, channel = i['channel'])
                                    else:
                                        if random.randint(0,1) == 1:
                                            G.add_edge(sender, receiver, date = transdate, channel = i['channel'])
                                        else:
                                            G.add_edge(receiver, sender, date = transdate, channel = i['channel'])
        isolates = list(nx.isolates(G))
        G.remove_nodes_from(isolates)
        self.instance = G
        return self

    def AlignedGantt(self, chartname):
        import plotly.plotly as py
        import plotly.figure_factory as ff
        import datetime
        
        df = [{'Task' : k, 'Start' : datetime.datetime.fromtimestamp(v['min']).strftime("%Y-%m-%d %H:%M:%S"), 'Finish' : datetime.datetime.fromtimestamp(v['max']).strftime("%Y-%m-%d %H:%M:%S")} for k, v in self.aligned.items()]
        
        fig = ff.create_gantt(df)
        py.plot(fig, filename=chartname, world_readable=True)

        return self

    def DrawNetworkX(self):
        pos = nx.layout.kamada_kawai_layout(self.instance)
        colors = [[self.colors[b['channel']] for a,b in self.instance[u][v].items()][0] for u,v in self.instance.edges()]
        nx.draw(self.instance, pos=pos, edge_color=colors)
        nx.draw_networkx_labels(self.instance, pos=pos)
        plt.show()
        return self

    def ColorGraph(self):
        ecolor = {"email" : "green", "phone" : "blue", "travel" : "red"}
        for u,v in self.instance.edges():
            for a,b in self.instance[u][v].items():
                self.instance[u][v][a]['color'] = ecolor[b['channel']]
        return self

    def Viz(self, filename):
        A = nx.nx_agraph.to_agraph(self.instance)
        A.layout(prog='dot')
        A.draw(filename + '.png')
        return self

    def ExportEdgeList(self, filename):
        edgelist = []
        for u,v in self.instance.edges():
            for a,b in self.instance[u][v].items():
                edgelist += [[u,v,b['channel'],b['date']]]
        with open(filename, 'w') as f:
            f.write('\n'.join(['\t'.join([str(j) for j in i]) for i in edgelist]))
        return self
