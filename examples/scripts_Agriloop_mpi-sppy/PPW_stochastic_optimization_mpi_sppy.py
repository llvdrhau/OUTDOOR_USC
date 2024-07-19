"""
This is the case-study of the potato peel residue for the project AGRILOOP.
Made by Philippe and Lucas

Possible optimization modes: "Single run optimization", "Multi-criteria optimization", "Sensitivity analysis",
"Cross-parameter sensitivity", and "Single 2-stage recourse optimization"
"""

import sys
import os
import tracemalloc


# start the memory profiler
tracemalloc.start()
scrPath = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src'))
sys.path.insert(0, scrPath)

import outdoor


# define the paths to the Excel file and the results directories
Excel_Path = "../Excel_files/potato_peel_case_study_reduced.xlsm"

# define save locations
current_script_dir = os.path.dirname(os.path.abspath(__file__))
results_dir = os.path.join(current_script_dir, 'results')
saved_data_dir = os.path.join(current_script_dir, 'saveFiles')
savePathPLots = results_dir

# set optimization mode
optimization_mode = "2-stage-recourse"
stochastic_mode = "mpi-sppy"

# create the superstructure data from the Excel file and
superstructureObject = outdoor.get_DataFromExcel(Excel_Path, optimization_mode=optimization_mode,
                                                stochastic_mode=stochastic_mode)

# create the superstructure flowsheet
outdoor.create_superstructure_flowsheet(superstructureObject, savePathPLots)

# solve the optimization problem
abstractStochaticModel = outdoor.SuperstructureProblem(parser_type='Superstructure')


# solver options
solverOptions = {"IntFeasTol": 1e-8,  # tolerance for integer feasibility
                 "NumericFocus": 0}   # 0: balanced, 1: feasibility, 2: optimality, 3: feasibility and optimality

# mpi-sppy options, integrates the solver options as well
options = {
    "solver_name": "gurobi",
    "PHIterLimit": 100,
    "defaultPHrho": 5,
    "convthresh": 1e-7,
    "verbose": False,
    "display_progress": False,
    "display_timing": False,
    "iter0_solver_options": solverOptions,
    "iterk_solver_options": solverOptions,
}

model_output = abstractStochaticModel.solve_optimization_problem(input_data=superstructureObject,
                                                         mpi_sppy_options=options)

# model_output.save_2_json(savePath=Results_Path_stochatic,
#                          saveName="model_output_200_scenarios")

model_output.save_with_pickel(path=saved_data_dir,
                              saveName="test2.pkl")


