#!/usr/bin/env python3

import scenariox as scnx

def RunExamples():
    exdir = "examples"
    scenario1 = scnx.Parser(exdir + "example.tab")
    dgraph1 = scnx.DGraph(scenario1).Viz(exdir + "output/sg_scenario")
    [scnx.TGraph(dgraph1.graph, scenario1).RanDWalk().Viz(exdir + "output/sg_instance" + str(i)) for i in range(5)]

RunExamples()
