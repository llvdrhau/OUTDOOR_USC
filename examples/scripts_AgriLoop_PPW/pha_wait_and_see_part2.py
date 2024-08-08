"""
This is the case-study of the potato peel residue for the project AGRILOOP.
Made by Lucas Van der Hauwaert

optimization mode: wait and see
analyze the results of the wait and see optimization mode
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
fileName = 'PHA_WaS_100_sc.pkl'

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
