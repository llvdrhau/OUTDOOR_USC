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
# tracemalloc.start()
scrPath = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src'))
sys.path.insert(0, scrPath)
import outdoor


# TODO found an important bug in the code, if you send source units (i.e., inputs like PPW) to multiple sinks the stream
# to which the source is connected is not the same arcoss multiple scenarios during the stochastic optimization!!
# ----------------------------TIPS-----------------
# 1) to avoid getting error when running the analysis (creating the flowsheert) and to visualise this error make sure NOT to use _tidy_data in StochasticModelOutput_mpi_sppy class
# 2) make sure in the methode def scenario_creator(self, scenarioName): that Y_DIST and Y are the stage 1 variables (optimiser class)
# 3) hack: MAKE SURE PWW IS ONLY CONNECTED TO ONE SINK IN THE SUPERSTRUCTURE (i.e., the GRINDER) that way you avoid this error

# SOLUTION: in the model constraint: ProcessGroup_logic_2_rule their is a variable self.connections.items()
# make sure through the EXCEL file that you specify that the source can only go to one sink! (like you would do in Material flow soures of a unit process)


# define the number of scenarios to be used in the stochastic optimization
n_scenarios = 11

# define the name of the saved data
saveName = "stochastic_mpi_sppy_{}sc".format(n_scenarios)
EVPIswitch = True

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
superstructureObject = outdoor.get_DataFromExcel(PathName=Excel_Path,
                                                 optimization_mode=optimization_mode,
                                                 stochastic_mode=stochastic_mode,
                                                 scenario_size=n_scenarios,
                                                 seed=45)

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


