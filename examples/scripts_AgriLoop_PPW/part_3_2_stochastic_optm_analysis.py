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
import pickle
import time

import numpy as np

scrPath = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src'))
sys.path.insert(0, scrPath)
import outdoor
from outdoor import MultiModelOutput


startTime = time.time()

# define pickel file name that contains the results
fileName = "Part_3_stochastic_optimization.pkl"
# name the output file from the wait and see analysis, so the same scenarios can be used
fileName_WaitAndSee = 'Part_2_1_wait_and_see_data.pkl'
# define the name of the plot to save
saveName = "Part_3_stochastic_flow_sheet_design.png"

# define save locations of results and plots
current_script_dir = os.path.dirname(os.path.abspath(__file__))
results_dir = os.path.join(current_script_dir, 'results')
saved_data_dir = os.path.join(current_script_dir, 'saved_files')
savePathPLots = results_dir


filePath = os.path.join(current_script_dir, 'saved_files') + '\\' + fileName
outputObject = outdoor.StochasticModelOutput_mpi_sppy.load_from_pickle(path=filePath)

# get the data files of all scenarios from the wait and see analysis and pass them to the superstructure object
# load the results from the pickle file
pickleFilePath_WaitAndSee = os.path.join(saved_data_dir, fileName_WaitAndSee)
WaitAndSee_Object = MultiModelOutput.load_from_pickle(path=pickleFilePath_WaitAndSee)

# Microbial Protein is the route chosen from the deterministic optimization problem (see scripts part 1)
# to calculate the VSS we need the results of the here and now optimization, with the design of the microbial protein production
# the results are saved in the pickle file 'Part_1_HAN_optimization.pkl'
fileName_HAN = 'Part_2_3_HAN_data.pkl'
pickleFilePath_HAN = os.path.join(saved_data_dir, fileName_HAN)
with open(pickleFilePath_HAN, 'rb') as file:
    HAN_Dict = pickle.load(file)
boxplotData = HAN_Dict['boxplotData']
MP_HereAndNowData = HAN_Dict['MP_HereAndNowData']
MP_key = list(boxplotData.keys())[1]
MP_WaitAndSee = boxplotData[MP_key]
# EVDS = Expected Value of the Deterministic Solution
mircobialProteinData = MP_WaitAndSee + MP_HereAndNowData
EVDS = np.mean(mircobialProteinData) # mean of the microbial protein data

# Now lets caluclate the EVPI for the stochastic optimization
# print in purple
print('')
print("\033[95m Calculating the EVPI for the stochastic optimization \033[00m")
EVPI, ExpectedEBIT, WaitAndSee = outputObject.calculate_EVPI(WaitAndSeeOutputObject=WaitAndSee_Object)
print('--------------------------------')
print('--------------------------------\n')
print('The Expected Value of the Deterministic Solution (EVDS) is: ', EVDS)
print('The Expected value of with Perfect Information (EVwPI) is: ', WaitAndSee)
print('The Expected Value of the Stochastic Solution (EVSS) is: ', ExpectedEBIT)
print('The Expected value of Perfect Information (EVPI) is: ', EVPI)
print('The Value of the Stochastic Solution (VSS) is: ', ExpectedEBIT - EVDS)
print('')
print('--------------------------------')
print('--------------------------------')


# # Initialise the analyser object
analyzer = outdoor.BasicModelAnalyzer(outputObject, deepcopy=False)

# create the flow sheets of the superstructure and the optimized flow sheet
print('')
print("\033[95m Creating optimized flowsheet \033[00m")
analyzer.create_flowsheet(path=savePathPLots,
                          saveName=saveName)


endTime = time.time()

print("Time elapsed: ", endTime - startTime)
print('File saved at: ', savePathPLots)
print('File name: ', saveName)
print('\033[92m' + '------sucess---------'+ '\033[0m')
