"""
Author: Lucas Van der Hauwaert, 07/2024

Part 4.3: Wait and see optimization run
In this script, the wait and see optimization is run for the potato peel residue case study.
The optimization is run for 100 scenarios, we want to see what the most influential parameters are that need to be improved.
To reach a desired EBIT of 0.759. The results are saved in a pickle file for further analysis.

Objective: EBIT (maximize the profit)
Optimization mode: wait and see
Excel file: potato_peel_case_PHA_uncertainty.xlsm

Generated files:
- Part_4_3_pha_WAS.pkl (saved in saved_files directory)

"""

import sys
import os
import tracemalloc

# start the memory profiler
tracemalloc.start()
scrPath = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src'))
sys.path.insert(0, scrPath)

import outdoor


n_scenarios = 100

saveName = 'Part_4_3_pha_WAS.pkl'

# define the paths to the Excel file and the results directories
ExcelPath = '../../examples/Excel_files/potato_peel_case_PHA_uncertainty.xlsm'
currentScriptDir = os.path.dirname(__file__)
resultsPath = os.path.join(currentScriptDir, 'results')
saveOutputObjectDir = os.path.join(currentScriptDir, 'saved_files')


# set optimization mode
optimization_mode = 'wait and see'

# create the superstructure data from the Excel file
superstructure_Object = outdoor.get_DataFromExcel(ExcelPath,
                                                  optimization_mode=optimization_mode,
                                                  scenario_size=n_scenarios,
                                                  seed=66)

# check if the uncertainty data is correct
superstructure_Object.check_uncertainty_data()

# create the superstructure flowsheet
# outdoor.create_superstructure_flowsheet(superstructure_Object, Results_Path)

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
model_output.save_with_pickel(path=saveOutputObjectDir,
                              saveName=saveName)


# print in green
print('\033[92m' + '------sucess---------')


