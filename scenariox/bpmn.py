#!/usr/bin/env python3
import bpmn_python.bpmn_diagram_layouter as layouter
import bpmn_python.bpmn_diagram_visualizer as visualizer
import bpmn_python.bpmn_diagram_rep as diagram

class BPMN():
    scenario = None
    bpmn = None
    
    def __init__(self, scenario):
        self.scenario = scenario
        self.Translate()
        
    def Translate(self):
        bpmn_graph = diagram.BpmnDiagramGraph()
        bpmn_graph.create_new_diagram_graph(diagram_name="scenario")
        root_id = bpmn_graph.add_process_to_diagram()

        mapped = {'root' : bpmn_graph.add_start_event_to_diagram(root_id, start_event_name="root")}
        edges = []
        cproc = 'root'
        maxdepth = None
        def recurtravel(node, depth):
            tasks = set([i.split('-')[0] for i in self.scenario.phases[node].children])
            pgate = ' '.join(tasks) if len(tasks) > 1 else None
            if pgate:
                if pgate not in mapped.keys():
                    mapped[pgate] = bpmn_graph.add_parallel_gateway_to_diagram(root_id, gateway_name = pgate)
                bpmn_graph.add_sequence_flow_to_diagram(root_id, mapped[node][0], mapped[pgate][0])
            for i in tasks:
                if i not in mapped.keys():
                    mapped[i] = bpmn_graph.add_subprocess_to_diagram(root_id, subprocess_name = i)
                if pgate and not [pgate, i] in edges:
                    bpmn_graph.add_sequence_flow_to_diagram(root_id, mapped[pgate][0], mapped[i][0])
                    edges.append([pgate, i])
                else:
                    bpmn_graph.add_sequence_flow_to_diagram(root_id, mapped[node][0], mapped[i][0])
                for j in self.scenario.phases[node].children:
                    if j not in mapped.keys() and i in j:
                        mapped[j] = bpmn_graph.add_task_to_diagram(root_id, task_name = j)
                        bpmn_graph.add_sequence_flow_to_diagram(root_id, mapped[i][0], mapped[j][0])
                        recurtravel(j, depth + 1) if depth == None or depth != maxdepth else None
                
        recurtravel('root', 0)
        self.mapped = mapped
        self.bpmn_graph = bpmn_graph
        return self

    def Viz(self, filename):
        pos = layouter.generate_layout(self.bpmn_graph)
        visualizer.bpmn_diagram_to_png(self.bpmn_graph, filename + ".png")
        return self
