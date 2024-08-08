"""
Author: Lucas Van der Hauwaert, 07/2024

Part 3.1: Stochastic Optimization run using mpi-sppy
Given the uncertainty in the parameters, we will now run a stochastic optimization using mpi-sppy. The optimization will
return the best possible flow-sheet design over the different scenarios. The results are saved in a pickle file for
further analysis/plots.

The model data files of each scenario are loaded from the wait and see output object and passed
to the superstructure object to solve the optimization problem with the same 300 scenarios.


Objective: EBIT (maximize the profit)
Optimization mode: Stochastic optimization using mpi-sppy
Output file used: Part_2_wait_and_see_300_sc.pkl (generated in part_2_1_wait_and_see_optimization_run.py)
Excel file: potato_peel_case_study.xlsm

Generated files:
- saved_files/Part_3_stochastic_optimization.pkl: the results of the optimization run
"""

import sys
import os
import tracemalloc
# start the memory profiler
# tracemalloc.start()
scrPath = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src'))
sys.path.insert(0, scrPath)
import outdoor
from outdoor import MultiModelOutput


# define the name of the saved data
saveName = "Part_3_stochastic_optimization.pkl"
# name the output file from the wait and see analysis
fileName = 'Part_2_wait_and_see_300_sc.pkl'
# define the path to the Excel file
Excel_Path = "../Excel_files/potato_peel_case_study.xlsm"

# define save locations
current_script_dir = os.path.dirname(os.path.abspath(__file__))
results_dir = os.path.join(current_script_dir, 'results')
saved_data_dir = os.path.join(current_script_dir, 'saved_files')
savePathPLots = results_dir

# set optimization mode
optimization_mode = "2-stage-recourse"
stochastic_mode = "mpi-sppy"

# get the data files of all scenarios from the wait and see analysis and pass them to the superstructure object
# load the results from the pickle file
pickleFilePath = os.path.join(saved_data_dir, fileName)
WaitAndSee_Object = MultiModelOutput.load_from_pickle(path=pickleFilePath)
scenarioDataFiles = WaitAndSee_Object._dataFiles


# create the superstructure data from the wait and see pickel file
superstructureObject = outdoor.get_DataFromExcel(PathName=Excel_Path,
                                                 optimization_mode=optimization_mode,
                                                 stochastic_mode=stochastic_mode,
                                                 scenarioDataFiles=scenarioDataFiles,
                                                 )


# solve the optimization problem
abstractStochaticModel = outdoor.SuperstructureProblem(parser_type='Superstructure')


# solver options
solverOptions = {"IntFeasTol": 1e-8,  # tolerance for integer feasibility
                 "NumericFocus": 0}   # 0: balanced, 1: feasibility, 2: optimality, 3: feasibility and optimality

# mpi-sppy options, integrates the solver options as well
options = {
    "solver_name": "gurobi",
    "PHIterLimit": 100,
    "defaultPHrho": 15,
    "convthresh": 1e-7,
    "verbose": False,
    "display_progress": False,
    "display_timing": False,
    "iter0_solver_options": solverOptions,
    "iterk_solver_options": solverOptions,
}

model_output = abstractStochaticModel.solve_optimization_problem(input_data=superstructureObject,
                                                                 mpi_sppy_options=options,
                                                                 calculation_EVPI=True)


model_output.save_with_pickel(path=saved_data_dir,
                              saveName=saveName)

# Now lets caluclate the EVPI for the stochastic optimization
# print in purple
print('')
print("\033[95m Calculating the EVPI for the stochastic optimization \033[00m")
EVPI = model_output.calculate_EVPI(WaitAndSeeOutputObject=WaitAndSee_Object)
print('--------------------------------')
print('--------------------------------')
print('The EVPI is: ', EVPI)

# print(model_output.uncertaintyMatrix) # print the uncertainty matrix
