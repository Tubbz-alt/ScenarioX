#!/usr/bin/env python3
import networkx as nx
from networkx.drawing.nx_agraph import write_dot, graphviz_layout
import matplotlib.pyplot as plt

class DGraph():
    scenario = None
    
    def __init__(self, scenario):
        self.scenario = scenario
        self.Translate()
        self.ColorGraph()
        
    def Translate(self):
        graph = nx.DiGraph()
        graph.add_node('root', type = 'subprocess')
        mapped = ['root']
        edges = []
        cproc = 'root'
        maxdepth = None
        def recurtravel(node, depth):
            nonlocal mapped
            tasks = set([i.split('-')[0] for i in self.scenario.phases[node].children])
            pgate = ' '.join(tasks) if len(tasks) > 1 else None
            if pgate:
                if pgate not in mapped:
                    graph.add_node(pgate, type = 'parallel_gateway')
                    mapped += [pgate]
                graph.add_edge(node, pgate)
            for i in tasks:
                if i not in mapped:
                    graph.add_node(i, type = 'subprocess')
                    mapped += [i]
                if pgate and not [pgate, i] in edges:
                    graph.add_edge(pgate, i)
                    edges.append([pgate, i])
                else:
                    graph.add_edge(node, i)
                for j in self.scenario.phases[node].children:
                    if j not in mapped and i in j:
                        graph.add_node(j, type = 'task')
                        mapped += [j]
                        graph.add_edge(i, j)
                        recurtravel(j, depth + 1) if depth == None or depth != maxdepth else None
                
        recurtravel('root', 0)
        self.mapped = mapped
        self.graph = graph
        return self

    def ColorGraph(self):
        ncolor = {'parallel_gateway' : 'blue', 'subprocess' : 'green', 'task' : 'red'}
        for i in self.graph.nodes():
            self.graph.nodes[i]['color'] = ncolor[self.graph.nodes[i]['type']]
        return self
    
    
    def Viz(self, filename):
        A = nx.nx_agraph.to_agraph(self.graph)
        A.layout(prog='dot')
        A.draw(filename + '.png')
        return self
