"""
Author: Lucas Van der Hauwaert, 07/2024

Part 2.1 of the AgriLoop case study: wait and see optimization run

This is script runs various scenarios with different parameters and saves the results in a pickle file for further
analysis. See part_2_2_wait_and_see_analysis.py for the analysis and plots.

Objective: EBIT (maximize the profit)
Optimization mode: wait and see
Excel file: potato_peel_case_study.xlsm

Generated files:
- saved_files/Part_2_wait_and_see_300_sc.pkl: the results of the optimization run

"""

import sys
import os
import tracemalloc

# start the memory profiler
tracemalloc.start()
scrPath = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src'))
sys.path.insert(0, scrPath)

import outdoor

# number of scenarios to be generated
n_scenarios = 300
# name of the pickle file to save the results
saveName = 'Part_2_wait_and_see_{}_sc.pkl'.format(n_scenarios)

# define the paths to the Excel file and the results directories
Excel_Path = "../Excel_files/potato_peel_case_study.xlsm"

# define save locations
current_script_dir = os.path.dirname(os.path.abspath(__file__))
results_dir = os.path.join(current_script_dir, 'results')
savePathPLots = results_dir
# location to save output files
saveDirOutput = os.path.join(current_script_dir, 'saved_files')

# set optimization mode
optimization_mode = 'wait and see'

# create the superstructure data from the Excel file
superstructure_Object = outdoor.get_DataFromExcel(Excel_Path,
                                                  optimization_mode=optimization_mode,
                                                  scenario_size=n_scenarios,
                                                  seed=29)

# check if the uncertainty data is correct
superstructure_Object.check_uncertainty_data()

# create the superstructure flowsheet (not necessary for the optimization, already done in part 1)
# outdoor.create_superstructure_flowsheet(superstructure_Object,
#                                         results_dir)

# solve the optimization problem
abstract_model = outdoor.SuperstructureProblem(parser_type='Superstructure')
solverOptions = {"IntFeasTol": 1e-8,  # tolerance for integer feasibility
                 "NumericFocus": 0}   # 0: balanced, 1: feasibility, 2: optimality, 3: feasibility and optimality

model_output = abstract_model.solve_optimization_problem(input_data=superstructure_Object,
                                                         optimization_mode=optimization_mode,
                                                         solver='gurobi',
                                                         interface='local',
                                                         options=solverOptions,)

# save the results in a pickle file for further analysis
model_output.save_with_pickel(path=saveDirOutput,
                              saveName=saveName,
                              option='small')

# # save the results in a pickle file for further analysis
# model_output.save_chunks_with_pickel(path=saveDirOutput,
#                                     saveName=saveName,
#                                     nChunks=5)


# print in green
print('\033[92m' + '------sucess---------')


