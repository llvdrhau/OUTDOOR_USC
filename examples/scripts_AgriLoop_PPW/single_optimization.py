"""
This is the case-study of the potato peel residue for the project AGRILOOP.
Made by Philippe Kenkle adapted by Lucas Van der Hauwaert

Possible optimization modes: "Single run optimization", "Multi-criteria optimization", "Sensitivity analysis",
"Cross-parameter sensitivity", and "Single 2-stage recourse optimization"
"""

import sys
import os
import tracemalloc


# start the memory profiler
tracemalloc.start()
# add the path to the src folder to the system path
scrPath = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src'))
sys.path.insert(0, scrPath)

import outdoor


# define the paths to the Excel file and the results directories
Excel_Path = "../Excel_files/potato_peel_case_study_reduced.xlsm"

# define save locations
current_script_dir = os.path.dirname(os.path.abspath(__file__))
results_dir = os.path.join(current_script_dir, 'results')
savePathPLots = results_dir
# location to save output files
saveDirOutput = os.path.join(current_script_dir, 'saved_files')


# set optimization mode
optimization_mode = 'single'

# create the superstructure data from the Excel file and
superstructure_Data = outdoor.get_DataFromExcel(Excel_Path, optimization_mode=optimization_mode)

# create the superstructure flowsheet
outdoor.create_superstructure_flowsheet(superstructure_Data, path=savePathPLots)

# solve the optimization problem
abstract_model = outdoor.SuperstructureProblem(parser_type='Superstructure')
solverOptions = {"IntFeasTol": 1e-8,  # tolerance for integer feasibility
                 "NumericFocus": 0}   # 0: balanced, 1: feasibility, 2: optimality, 3: feasibility and optimality

model_output = abstract_model.solve_optimization_problem(input_data=superstructure_Data,
                                                         optimization_mode=optimization_mode,
                                                         solver='gurobi',
                                                         interface='local',
                                                         calculation_VSS=False,
                                                         calculation_EVPI=False,
                                                         options=solverOptions,)

# current, peak = tracemalloc.get_traced_memory()
# print(f"Current memory usage is {current / 10 ** 6}MB; Peak was {peak / 10 ** 6}MB")

print('Single optimization problem run')
# save the results as a txt file, you have to specify the path
model_output.get_results(path=results_dir,
                         saveName='single_optimization_overview')
# save and analyze the new results
analyzer = outdoor.BasicModelAnalyzer(model_output)
# create the flow sheets of the superstructure and the optimized flow sheet
analyzer.create_flowsheet(path=savePathPLots,
                          saveName='Single_Optimization_design')

# save the results in a pickle file
fileName = 'single_optimization.pkl'
model_output.save_with_pickel(path=saveDirOutput, saveName=fileName)


