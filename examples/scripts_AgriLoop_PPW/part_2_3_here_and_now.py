"""
Author: Lucas Van der Hauwaert, 07/2024

Part 2.3: Here and now analysis,

Imagine you choose to implement the best flow-sheet design from the single objective optimization. How would the
flow-sheet over the different scenarios made from the Wait and see design?

Objective: EBIT (maximize the profit)
Optimization mode: wait and see
Output file: Part_2_wait_and_see_300_sc.pkl (generated in part_2_1_wait_and_see_optimization_run.py)

Generated files:
- results/box_plot_flowsheet_designs.png: the scenario analysis box plots
- Standard Regression Coefficients (SRC) from the wait and see optimization (see notes for results from the console)

"""


# TODO figure out why only +/- 60% of the scenarios are feasible in here_and_now.py?
#  in wait_and_see_analysis.py almost all scenarios are feasible, what is going wrong here?

import sys
import os
import tracemalloc

# start the memory profiler
tracemalloc.start()
scrPath = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src'))
sys.path.insert(0, scrPath)

import outdoor
from outdoor import ModelOutput, MultiModelOutput


# define the paths to the Excel file and the results directories
#Excel_Path = '../../examples/Excel_files/potato_peel_case_study.xlsm'
Excel_Path = '../../examples/Excel_files/potato_peel_case_study_reduced.xlsm'
current_script_dir = os.path.dirname(__file__)
Results_Path = os.path.join(current_script_dir, 'results')
save_Output_object_dir = os.path.join(current_script_dir, 'saved_files')


# set optimization mode
optimization_mode = 'here and now'

# for the here and now mode, we need to define the design variables.
# We can use the variable from the single optimization to see what would happen over various scenarios with a fixed design

# load the results from the pickle file
fileName = 'single_optimization.pkl'
pickleFilePath = os.path.join(save_Output_object_dir, fileName)
SingleOptimization_Object = ModelOutput.load_from_pickle(path=pickleFilePath)
outputDataSingle = SingleOptimization_Object._data

# get the scenario files from the wait and see analysis and pass them to the superstructure object
# load the results from the pickle file
fileName = 'WaS_10_sc.pkl'
pickleFilePath = os.path.join(save_Output_object_dir, fileName)
WaitAndSee_Object = MultiModelOutput.load_from_pickle(path=pickleFilePath)
scenarioDataFiles = WaitAndSee_Object._dataFiles

# create the superstructure data from the Excel file
superstructure_Object = outdoor.get_DataFromExcel(PathName=Excel_Path,
                                                  optimization_mode=optimization_mode,
                                                  scenarioDataFiles=scenarioDataFiles,
                                                  )


# solve the optimization problem
abstract_model = outdoor.SuperstructureProblem(parser_type='Superstructure')
solverOptions = {"IntFeasTol": 1e-8,  # tolerance for integer feasibility
                 "NumericFocus": 0}   # 0: balanced, 1: feasibility, 2: optimality, 3: feasibility and optimality

model_output = abstract_model.solve_optimization_problem(input_data=superstructure_Object,
                                                         optimization_mode=optimization_mode,
                                                         solver='gurobi',
                                                         interface='local',
                                                         options=solverOptions,
                                                         outputFileDesignSpace=outputDataSingle)

print(model_output._results_data)
print('Number of sucessfull runs:', len(model_output._results_data))


feasilbeResults = list(model_output._results_data.keys())
OutputScenario = model_output._results_data[feasilbeResults[0]] # take the first feasible result
# Analyze the results of one scenario
analyzer = outdoor.BasicModelAnalyzer(OutputScenario)
# create the flow sheets of the superstructure and the optimized flow sheet
analyzer.create_flowsheet(path=Results_Path,
                          saveName='test_design')


# save the results in a pickle file for further analysis
saveName = 'here_and_now_10sc.pkl'
model_output.save_with_pickel(path=save_Output_object_dir, saveName=saveName)


# print in green
print('\033[92m' + '------sucess---------')


