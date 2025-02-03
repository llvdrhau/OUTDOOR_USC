# -*- coding: utf-8 -*-
"""
Created on Thu Dec  9 15:23:46 2021

@author: Joshua
"""

import os

import pydot


def create_superstructure_flowsheet(superstructure, path, saveName=None):

    def make_node(graph, name, shape, orientation = 0, color = 'black'):
        """
        Create nodes inside the flowsheet graph


        """

        node = pydot.Node(name, height=0.5, width=2, fixedsize=True, shape=shape, orientation=-orientation,
                          color= color, style='filled', fillcolor='white')
        graph.add_node(node)

        return node

    def make_link(graph, a_node, b_node, label = None, width = 1,
                  style = 'solid'):
        """
        Create links / edges inside the flowsheet graph


        """
        edge = pydot.Edge(a_node, b_node)
        edge.set_penwidth(width)
        edge.set_style(style)

        if label is not None:
            edge.set_label(label)

        graph.add_edge(edge)

        return edge


    # Script

    data = list()


    for i in superstructure.UnitsList:

        if i.Possible_Sources:
            for j in i.Possible_Sources:
                data.append((j, i.Number))

        if i.Number in superstructure.distributor_list['DISTRIBUTORS']:

            for j in i.targets:
                data.append((i.Number, j))

        if i.split_factor['split_factor']:
            for j in i.split_factor['split_factor'].keys():
                data.append((j[0], j[1][0]))

        data = list(dict.fromkeys(data))


    flowchart  = pydot.Dot('flowchart', rankdir = 'LR', ratio="compress",
                           size="15!,1",  dpi="500")

    nodes = {}
    edges = {}


    for i in data:
        for v in i:
            if v not in nodes.keys():

                if v in superstructure.SourceList['RAW_MATERIAL_SOURCES']:
                    nodes[v] = make_node(flowchart, superstructure.UnitNames2['names'][v],
                                            'ellipse', color='green')

                elif v in superstructure.StoichRNumberList['STOICH_REACTORS']:

                    if v in superstructure.ElectricityGeneratorList['TURBINES']:
                        nodes[v] = make_node(flowchart, superstructure.UnitNames2['names'][v],
                                        'doubleoctagon')

                    elif v in superstructure.HeatGeneratorList['FURNACES']:
                        nodes[v] = make_node(flowchart, superstructure.UnitNames2['names'][v],
                                        'doubleoctagon')

                    else:
                        nodes[v] = make_node(flowchart, superstructure.UnitNames2['names'][v],
                                             'octagon')

                elif v in superstructure.YieldRNumberList['YIELD_REACTORS']:
                    nodes[v] = make_node(flowchart, superstructure.UnitNames2['names'][v],
                                        'octagon')

                elif v in superstructure.ProductPoolList['PRODUCT_POOLS']:
                    nodes[v] = make_node(flowchart, superstructure.UnitNames2['names'][v],
                                        shape='house', color='blue', orientation= 270)

                elif v in superstructure.distributor_list['DISTRIBUTORS']:
                    nodes[v] = make_node(flowchart, superstructure.UnitNames2['names'][v],
                                        shape='triangle', orientation= 270)

                else:
                    nodes[v] = make_node(flowchart, superstructure.UnitNames2['names'][v], 'box')



    for i in data:
        edges[i[0],i[1]] = make_link(flowchart, nodes[i[0]], nodes[i[1]])

    # path  = path + '/superstructure_flowsheet.pdf'

    if not os.path.exists(path):
        os.makedirs(path)

    # give appropriate name to the file
    if saveName is None:
        saveName = '/superstructure_flowsheet.png'
    else:
        if 'png' not in saveName:
            saveName = saveName + '.png'
        saveName = '/' + saveName


    savePath  = path + saveName
    # flowchart.write_pdf(path)
    flowchart.write_png(savePath)
