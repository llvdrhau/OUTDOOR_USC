"""
This is the case-study of the potato peel residue for the project AGRILOOP.
Lucas Van der Hauwaert, 2024 - 2025

Stochastic optimization Using mpi-sppy. The files of the scenarios are loaded from the wait and see analysis and passed
to the superstructure object in order to solve the same optimization problem. The results are saved in a pickle file.
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


# define the number of scenarios to be used in the stochastic optimization
n_scenarios = 10

# define the name of the saved data
saveName = "stochastic_mpi_sppy_{}sc".format(n_scenarios)
EVPIswitch = True

# define the paths to the Excel file and the results directories
Excel_Path = "../Excel_files/potato_peel_case_study_reduced.xlsm"

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
fileName = 'WaS_{}_sc.pkl'.format(n_scenarios)
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
                                                                 calculation_EVPI=EVPIswitch)


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

print(model_output.uncertaintyMatrix) # print the uncertainty matrix
