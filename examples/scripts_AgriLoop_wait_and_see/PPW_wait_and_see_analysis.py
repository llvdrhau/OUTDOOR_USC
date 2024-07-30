"""
This is the case-study of the potato peel residue for the project AGRILOOP.
Made by Lucas Van der Hauwaert

optimization mode: wait and see
"""

import sys
import os
import tracemalloc
import time

startTime = time.time()

# start the memory profiler
tracemalloc.start()
scrPath = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src'))
sys.path.insert(0, scrPath)

import outdoor
from outdoor import MultiModelOutput
from outdoor import AdvancedMultiModelAnalyzer

# file name that contains the results
fileName = "WaS_100_sc.pkl"

# define the paths to the save and results directories
current_script_dir = os.path.dirname(os.path.abspath(__file__))
results_dir = os.path.join(current_script_dir, 'results')
saved_data_dir = os.path.join(current_script_dir, 'saved_data')
savePathPLots = results_dir

# load the results from the pickle file
pickleFilePath = os.path.join(saved_data_dir, fileName)
outputObject = MultiModelOutput.load_from_pickle(path=pickleFilePath)

# Initialise the analyser object and plot the scenario analysis
analyzer = AdvancedMultiModelAnalyzer(outputObject)
analyzer.plot_scenario_analysis(path=savePathPLots, saveName='Scenario_analysis_100', showPlot=True, flowThreshold=0.01)


endTime = time.time()
print("Time elapsed: ", endTime - startTime)
