"""
Author: Lucas Van der Hauwaert, 07/2024

Part 4.4: Wait and see, analysis of results
In this script, the wait and see optimization results are analyzed for the potato peel residue case study.
The optimization is run for 100 scenarios, we want to see what the most influential parameters are that need to be improved.
To reach a desired EBIT of 0.759. The results are saved in a pickle file for further analysis.

Objective: EBIT (maximize the profit)
Optimization mode: wait and see
Used output file: Part_4_3_pha_WAS.pkl

Generated files:
- TODO compleet
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
fileName = 'Part_4_3_pha_WAS.pkl'

# define the paths to the save and results directories
current_script_dir = os.path.dirname(os.path.abspath(__file__))
results_dir = os.path.join(current_script_dir, 'results')
saved_data_dir = os.path.join(current_script_dir, 'saved_files')
savePathPLots = results_dir

# load the results from the pickle file
pickleFilePath = os.path.join(saved_data_dir, fileName)
ModelOutput = MultiModelOutput.load_from_pickle(path=pickleFilePath)

# Calculate the SRC
ModelOutput.calculate_SRC()

# Check if there are scenarios that are have EBIT > 0.759
print()
outputPerScenario = ModelOutput._results_data

scenarioList = []
for scenario, outputObject in outputPerScenario.items():
    EBIT = outputObject._data['EBIT']
    if EBIT >= 0.759:
        scenarioList.append(scenario)

print('there are {} scenarios that have an EBIT > 0.759'.format(len(scenarioList)))
