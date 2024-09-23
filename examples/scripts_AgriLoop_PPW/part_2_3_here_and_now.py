"""
Author: Lucas Van der Hauwaert, 07/2024

Part 2.3: Here and now analysis,

Imagine you choose to implement the best flow-sheet design from the single objective optimization. How would the
flow-sheet over the different scenarios made from the Wait and see design? We're going to do this for the three scenarios
which were feasible in the wait and see optimization. I.e. for production of Microbial Prottein, Animal Feed and PHA

Objective: EBIT (maximize the profit)
Optimization mode: here and now
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
import numpy as np
import pickle

startTime = time.time()

# start the memory profiler
tracemalloc.start()
scrPath = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src'))
sys.path.insert(0, scrPath)

import outdoor
from outdoor import MultiModelOutput
from outdoor import AdvancedMultiModelAnalyzer


# Define all the directories where data is extracted and results are stored
current_script_dir = os.path.dirname(os.path.abspath(__file__))
# define the paths to the save and results directories
results_dir = os.path.join(current_script_dir, 'results')
saved_data_dir = os.path.join(current_script_dir, 'saved_files')
savePathPLots = results_dir

# extract the data from the pickle file from part 2.2 wait and see analysis
fileName = "Part_2_2_waitAndSeeData.pkl"
pickelLocation = os.path.join(saved_data_dir, fileName)
with open(pickelLocation, 'rb') as file:
    dataDictPart2_2 = pickle.load(file)


# get the scenario files from the wait and see analysis and pass them to the superstructure object
# load the results from the pickle file
scenarioDataFiles = dataDictPart2_2['ModelOutput']
flowSheetDict = dataDictPart2_2['flowSheetDict']
boxplotData = dataDictPart2_2['boxplotData']


# for the here and now mode, we need to define the design variables.
# We can get the designs from the flowSheetDict and boxplotData from the wait and see analysis
keysDict = list(flowSheetDict.keys())

# --------------------------
# FOR MICROBIAL PROTEIN
# --------------------------
mpDesignKey = keysDict[1] # microbial protein design key is the 1st key in the keysDict!!
scKeys = list(flowSheetDict[mpDesignKey].keys())
microbialProteinDesign = flowSheetDict[mpDesignKey][scKeys[0]]  # take the first design
microbialProteinScenarioDataFiles = {}
# get the select set of scenario files from the wait and see analysis and pass them to the superstructure object
for sc in scenarioDataFiles:
    if sc not in flowSheetDict[mpDesignKey]:
        microbialProteinScenarioDataFiles.update({sc: scenarioDataFiles[sc]})

# --------------------------
# FOR Animal Feed
# --------------------------
afDesignKey = keysDict[2] # animal feed design key is the 3rd key in the keysDict!!
scKeys = list(flowSheetDict[afDesignKey].keys())
animalFeedDesign = flowSheetDict[afDesignKey][scKeys[0]]  # take the first design
annimalFeedScenarioDataFiles = {}
# get the select set of scenario files from the wait and see analysis and pass them to the superstructure object
for sc in scenarioDataFiles:
    if sc not in flowSheetDict[afDesignKey]:
        annimalFeedScenarioDataFiles.update({sc: scenarioDataFiles[sc]})

# --------------------------
# FOR PHA PRODUCTION
# --------------------------
phaDesignKey = keysDict[3] # PHA design key is the 2nd key in the keysDict!!
scKeys = list(flowSheetDict[phaDesignKey].keys())
phaDesign = flowSheetDict[phaDesignKey][scKeys[0]]  # take the first design
phaScenarioDataFiles = {}
# get the select set of scenario files from the wait and see analysis and pass them to the superstructure object
for sc in scenarioDataFiles:
    if sc not in flowSheetDict[phaDesignKey]:
        phaScenarioDataFiles.update({sc: scenarioDataFiles[sc]})

# --------------------------
# FOR COMPOST PRODUCTION
# --------------------------
compostDesignKey = keysDict[0]  # PHA design key: 0
scKeys = list(flowSheetDict[compostDesignKey].keys())
compostDesign = flowSheetDict[compostDesignKey][scKeys[0]]  # take the first design
compostScenarioDataFiles = {}
# get the select set of scenario files from the wait and see analysis and pass them to the superstructure object
for sc in scenarioDataFiles:
    if sc not in flowSheetDict[compostDesignKey]:
        compostScenarioDataFiles.update({sc: scenarioDataFiles[sc]})

# ---------------------------------------------------------------------------------------------------------------------
# delete the scenarioDataFiles to free up memory
del scenarioDataFiles
# ---------------------------------------------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------------------------------------------
# define the paths to the Excel file from which to make the superstructure object
# (the reduced superstructure, without starch production)
Excel_Path = '../../examples/Excel_files/potato_peel_case_study_no_starch.xlsm'
# set optimization mode
optimization_mode = 'here and now'
# --------------------------------------------------------------------------------------------------------------------


# ---------------------------------------------------------------------------------------------------------------------
# Run simulations with the design of Microbial Protein
# ---------------------------------------------------------------------------------------------------------------------

# create the superstructure data from the Excel file
superstructure_Object_MP = outdoor.get_DataFromExcel(path=Excel_Path,
                                                  optimization_mode=optimization_mode,
                                                  scenarioDataFiles=microbialProteinScenarioDataFiles,
                                                  )

# solve the optimization problem
abstract_model = outdoor.SuperstructureProblem(parser_type='Superstructure')
solverOptions = {"IntFeasTol": 1e-8,  # tolerance for integer feasibility
                 "NumericFocus": 0}   # 0: balanced, 1: feasibility, 2: optimality, 3: feasibility and optimality

model_output_microbial_protein = abstract_model.solve_optimization_problem(input_data=superstructure_Object_MP,
                                                                            optimization_mode=optimization_mode,
                                                                            solver='gurobi',
                                                                            interface='local',
                                                                            options=solverOptions,
                                                                            outputFileDesignSpace=microbialProteinDesign)


#print(model_output_microbial_protein._results_data)
print('scenarios of MP:', len(microbialProteinScenarioDataFiles))
print('Number of successful runs for Microbial Protein:', len(model_output_microbial_protein._results_data))


MP_HereAndNowData = []
for sc, objc in model_output_microbial_protein._results_data.items():
    data = objc._data
    try:
        MP_HereAndNowData.append(data['EBIT'])
    except:
        MP_HereAndNowData.append('xx')
        # print in red
        print('\033[91m' + 'EBIT not found in the data MP for scenario:', sc)
#print(MP_HereAndNowData)
del model_output_microbial_protein  # delete the model_output_microbial_protein to free up memory

# ---------------------------------------------------------------------------------------------------------------------
# run simulations with the design of Animal Feed
# ---------------------------------------------------------------------------------------------------------------------

superstructure_Object_AF = outdoor.get_DataFromExcel(path=Excel_Path,
                                                    optimization_mode=optimization_mode,
                                                    scenarioDataFiles=annimalFeedScenarioDataFiles,)


model_output_animal_feed = abstract_model.solve_optimization_problem(input_data=superstructure_Object_AF,
                                                                    optimization_mode=optimization_mode,
                                                                    solver='gurobi',
                                                                    interface='local',
                                                                    options=solverOptions,
                                                                    outputFileDesignSpace=animalFeedDesign)

print('scenarios of Animal Feed:', len(annimalFeedScenarioDataFiles))
print('Number of successful runs for Animal Feed:', len(model_output_animal_feed._results_data))

AF_HereAndNowData = []
for sc, objc in model_output_animal_feed._results_data.items():
    data = objc._data
    try:
        AF_HereAndNowData.append(data['EBIT'])
    except:
        # AF_HereAndNowData.append('xx')
        # print in red
        print('\033[91m' + 'EBIT not found in the data AF for scenario:', sc)
#print(AF_HereAndNowData)
del model_output_animal_feed # delete the model_output_animal_feed to free up memory

# ---------------------------------------------------------------------------------------------------------------------
# Run simulations with the design of PHA
# ---------------------------------------------------------------------------------------------------------------------


superstructure_Object_PHA = outdoor.get_DataFromExcel(path=Excel_Path,
                                                    optimization_mode=optimization_mode,
                                                    scenarioDataFiles=phaScenarioDataFiles,)

model_output_pha = abstract_model.solve_optimization_problem(input_data=superstructure_Object_PHA,
                                                                    optimization_mode=optimization_mode,
                                                                    solver='gurobi',
                                                                    interface='local',
                                                                    options=solverOptions,
                                                                    outputFileDesignSpace=phaDesign)

print('scenarios of PHA:', len(phaScenarioDataFiles))
print('Number of successful runs for PHA:', len(model_output_pha._results_data))

pha_HereAndNowData = []
for sc, objc in model_output_pha._results_data.items():
    data = objc._data
    try:
        pha_HereAndNowData.append(data['EBIT'])
    except:
        # pha_HereAndNowData.append('xx')
        # print in red
        print('\033[91m' + 'EBIT not found in the data PHA for scenario:', sc)
#print(pha_HereAndNowData)
del model_output_pha # delete the model_output_pha to free up memory

# ---------------------------------------------------------------------------------------------------------------------
# Run simulations with the design of Compost
# ---------------------------------------------------------------------------------------------------------------------

# create the superstructure data from the Excel file
superstructure_Object_compost = outdoor.get_DataFromExcel(path=Excel_Path,
                                                  optimization_mode=optimization_mode,
                                                  scenarioDataFiles=compostScenarioDataFiles,
                                                  )

# solve the optimization problem
abstract_model = outdoor.SuperstructureProblem(parser_type='Superstructure')
solverOptions = {"IntFeasTol": 1e-8,  # tolerance for integer feasibility
                 "NumericFocus": 0}   # 0: balanced, 1: feasibility, 2: optimality, 3: feasibility and optimality

model_output_compost = abstract_model.solve_optimization_problem(input_data=superstructure_Object_compost,
                                                                            optimization_mode=optimization_mode,
                                                                            solver='gurobi',
                                                                            interface='local',
                                                                            options=solverOptions,
                                                                            outputFileDesignSpace=compostDesign)


#print(model_output_microbial_protein._results_data)
print('scenarios of Compost:', len(compostScenarioDataFiles))
print('Number of successful runs for Microbial Protein:', len(model_output_compost._results_data))


compost_HereAndNowData = []
for sc, objc in model_output_compost._results_data.items():
    data = objc._data
    try:
        compost_HereAndNowData.append(data['EBIT'])
    except:
        compost_HereAndNowData.append('xx')
        # print in red
        print('\033[91m' + 'EBIT not found in the data compost for scenario:', sc)
#print(MP_HereAndNowData)
del model_output_compost  # delete the model_output_compost to free up memory

# ---------------------------------------------------------------------------------------------------------------------
# Save the relavant data in a pickle file
# ---------------------------------------------------------------------------------------------------------------------

# save boxplotData, flowSheetDict, MP_HereAndNowData, AF_HereAndNowData and pha_HereAndNowData, compost_HereAndNowData
# for further analysis

# save the data in a pickle file
dataDict = {'boxplotData': boxplotData,
            #'flowSheetDict': flowSheetDict,
            'MP_HereAndNowData': MP_HereAndNowData,
            'AF_HereAndNowData': AF_HereAndNowData,
            'pha_HereAndNowData': pha_HereAndNowData,
            'compost_HereAndNowData': compost_HereAndNowData}

pickleFilePath = os.path.join(saved_data_dir, 'Part_2_3_HAN_data.pkl')
# save the data in a pickle file
with open(pickleFilePath, 'wb') as f:
    pickle.dump(dataDict, f)

# print in green
print('\033[92m' + '------sucess---------'+ '\033[0m')


