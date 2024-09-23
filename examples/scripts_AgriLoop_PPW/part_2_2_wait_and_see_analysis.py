"""
Author: Lucas Van der Hauwaert, 07/2024

Part 2.2: Wait and see analysis,

This script makes box plots of possible flow-sheet designs and calculates the SRC from the wait and see optimization. To
see the most influential parameters. The relevant parameters will be considered in the stochastic optimization.

Objective: EBIT (maximize the profit)
Optimization mode: wait and see
Output file: Part_2_wait_and_see_300_sc.pkl (generated in part_2_1_wait_and_see_optimization_run.py)

Generated files:
- results/box_plot_flowsheet_designs.png: the scenario analysis box plots
- Standard Regression Coefficients (SRC) from the wait and see optimization (see notes for results from the console)

"""

import sys
import os
import tracemalloc
import time
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import pickle


def plot_percent_occurance(flowSheetDict, showPlot=False):
    """
    This function plots the percentage of occurance of each flow sheet design as a bar plot
    each bar has a different color for each flow sheet design
    :param flowSheetDict:
    :return:

    flowsheetDictExtra[keyFlowSheet].update({scenario: dataScenario})


    """
    designKeys = flowSheetDict.keys()
    percentagesDict = {}
    sumN = 0
    for key in designKeys:
        nDesigns = len(flowSheetDict[key].keys())
        sumN += nDesigns
        percentagesDict.update({key: nDesigns})

    percentagesDict = {key: value/sumN for key, value in percentagesDict.items()}

    # Get a color map
    # colormap = cm.get_cmap('viridis', len(percentagesDict))
    # colors = [colormap(i) for i in range(len(designKeys))]

    # colormap = cm.get_cmap('viridis', len(percentagesDict))
    # colors = [colormap(i / len(percentagesDict)) for i in range(len(percentagesDict))]

    fig, ax = plt.subplots()
    xTicks = ["Design " + str(i) for i in range(1, len(percentagesDict)+1)]
    ax.bar(xTicks, list(percentagesDict.values()))

    for i, design in enumerate(designKeys):
        print('Design ', i)
        print(f'{design}: {percentagesDict[design]*100:.2f}%')

    ax.set_ylabel('Percentage of occurance')
    # ax.set_title('Percentage of occurance of each flow sheet design')
    # save the plot
    plt.savefig('results/Part_2_2_percent_occurance.png')

    if showPlot:
        plt.show()

    return percentagesDict

# start the timer
startTime = time.time()

# start the memory profiler
tracemalloc.start()
scrPath = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src'))
sys.path.insert(0, scrPath)

import outdoor
from outdoor import MultiModelOutput
from outdoor import AdvancedMultiModelAnalyzer

# file name that contains the results
fileName =  'Part_2_1_wait_and_see_data.pkl'


# check the size of the pickle file
current_script_dir = os.path.dirname(os.path.abspath(__file__))


# define the paths to the save and results directories
results_dir = os.path.join(current_script_dir, 'results')
saved_data_dir = os.path.join(current_script_dir, 'saved_files')
savePathPLots = results_dir

# load the results from the pickle file
pickleFilePath = os.path.join(saved_data_dir, fileName)
#ModelOutput = MultiModelOutput.load_chunks_from_pickle(path=saved_data_dir,
#                                                       saveName=fileName,
#                                                       nChunks=5)
ModelOutput = MultiModelOutput.load_from_pickle(path=pickleFilePath)

# Calculate the SRC
ModelOutput.calculate_SRC()


# Initialise the analyser object and plot the scenario analysis
analyzer = AdvancedMultiModelAnalyzer(ModelOutput)
_, flowSheetDict, boxplotData = analyzer.plot_scenario_analysis(path=savePathPLots,
                                                                saveName='Part_2_2_box_plot_flowsheet_designs',
                                                                showPlot=False,
                                                                flowThreshold=0.01)

plot_percent_occurance(flowSheetDict, showPlot=False)


# Save some specific results so we don't have to open the model output object (less memory usage)
# save flowSheetDict, boxplotData, ModelOutput._dataFiles with pickle
waitAndSeeData = {'flowSheetDict': flowSheetDict,
                  'boxplotData': boxplotData,
                  'ModelOutput': ModelOutput._dataFiles}

with open(os.path.join(saved_data_dir, 'Part_2_2_waitAndSeeData.pkl'), 'wb') as f:
    pickle.dump(waitAndSeeData, f)




endTime = time.time()
print("Time elapsed: ", endTime - startTime)
current, peak = tracemalloc.get_traced_memory()
print(f"Current memory usage is {current / 10 ** 6}MB; Peak was {peak / 10 ** 6}MB")
print('\033[92m' + '------sucess---------'+ '\033[0m')
