"""
Author: Lucas Van der Hauwaert, 07/2024

Part 3.2: Stochastic Optimization plots
This script opens the pickel file holding the results of the stochastic optimization and creates the optimized flow-sheet
design accounting for the uncertainty in the parameters.


Objective: EBIT (maximize the profit)
Optimization mode: Stochastic optimization using mpi-sppy
Used output File: Part_3_stochastic_optimization.pkl (generated in part_3_1_stochastic_optimisation_run.py)

Generated files:
- results/Part_3_stochastic_flow_sheet_design.png: the optimized flow-sheet design
"""

import sys
import os
import time
scrPath = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src'))
sys.path.insert(0, scrPath)
import outdoor


startTime = time.time()

# define pickel file name that contains the results
fileName = "Part_3_stochastic_optimization.pkl"
# define the name of the plot to save
saveName = "Part_3_stochastic_flow_sheet_design.png"

# define save locations of results and plots
current_script_dir = os.path.dirname(os.path.abspath(__file__))
results_dir = os.path.join(current_script_dir, 'results')
savePathPLots = results_dir


filePath = os.path.join(current_script_dir, 'saved_files') + '\\' + fileName
outputObject = outdoor.StochasticModelOutput_mpi_sppy.load_from_pickle(path=filePath)

# # Initialise the analyser object
analyzer = outdoor.BasicModelAnalyzer(outputObject)

# create the flow sheets of the superstructure and the optimized flow sheet
print('')
print("\033[95m Creating optimized flowsheet \033[00m")
analyzer.create_flowsheet(path=savePathPLots,
                          saveName=saveName)


endTime = time.time()

print("Time elapsed: ", endTime - startTime)
print('File saved at: ', savePathPLots)
print('File name: ', saveName)
