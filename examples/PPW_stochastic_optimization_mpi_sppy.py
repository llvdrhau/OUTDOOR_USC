"""
This is the case-study of the potato peel residue for the project AGRILOOP.
Made by Philippe adapted by Lucas

Possible optimization modes: "Single run optimization", "Multi-criteria optimization", "Sensitivity analysis",
"Cross-parameter sensitivity", and "Single 2-stage recourse optimization"
"""

import sys
import os
import tracemalloc
#from delete_function import delete_all_files_in_directory


# start the memory profiler
tracemalloc.start()
# add the path to the src folder to the system path
a = os.path.dirname(__file__)
a = os.path.dirname(a)
b = a + '/src'
sys.path.append(b)

import outdoor


# define the paths to the Excel file and the results directories
Excel_Path = "Excel_files/potato_peel_case_study_reduced.xlsm"
Results_Path_stochatic = r"C:\Users\Lucas\PycharmProjects\OUTDOOR_USC\examples\results\potato_peel_case_study_mpi-sppy"
savePathPLots = Results_Path_stochatic + "/plots2"

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
    "PHIterLimit": 10,
    "defaultPHrho": 10,
    "convthresh": 1e-7,
    "verbose": False,
    "display_progress": False,
    "display_timing": False,
    "iter0_solver_options": solverOptions,
    "iterk_solver_options": solverOptions,
}

model_output = abstractStochaticModel.solve_optimization_problem(input_data=superstructureObject,
                                                         mpi_sppy_options=options)

model_output.save_2_json(savePath=Results_Path_stochatic,
                         saveName="model_output_test")



#
