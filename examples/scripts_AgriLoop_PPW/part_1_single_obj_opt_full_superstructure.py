"""
Author: Lucas Van der Hauwaert, 07/2024

PART 1 of the case-study on potato peel residue for the project AGRILOOP.

Optimization mode: "Single run optimization", the assumed parameter values are used to solve the optimization
problem. and find the best possible flow sheet design.

Objective: EBIT (maximize the profit)
Optimization mode: single
Excel file: potato_peel_case_study.xlsm and potato_peel_case_study_no_starch.xlsm

Generated files:
- results/Part_1_single_optimization_overview.txt: the results of the optimization run
- results/Part_1_Full_Superstructure.png: the superstructure design space
- results/Part_1_Single_Optimization_design.png: the optimized flow sheet
- saved_files/Part_1_single_optimization.pkl: the results of the optimization run saved in a pickle file

"""

import sys
import os
import tracemalloc


# start the memory profiler
# tracemalloc.start()
# add the path to the src folder to the system path
scrPath = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src'))
sys.path.insert(0, scrPath)

import outdoor


# define the paths to the Excel file and the results directories
Excel_Path = "../Excel_files/potato_peel_case_study.xlsm"

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
outdoor.create_superstructure_flowsheet(superstructure_Data,
                                        path=savePathPLots,
                                        saveName='Part_1_Full_Superstructure')

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

# print the optimality gap:
print("The optimality gap is:", model_output._optimality_gap)

print('\n Single optimization problem run')
# save the results as a txt file, you have to specify the path
model_output.get_results(path=results_dir,
                         saveName='Part_1_single_optimization_overview')
# save and analyze the new results
analyzer = outdoor.BasicModelAnalyzer(model_output)
# create the flow sheets of the superstructure and the optimized flow sheet
analyzer.create_flowsheet(path=savePathPLots,
                          saveName='Part_1_Single_Optimization_design')

# save the results in a pickle file
fileName = 'Part_1_single_optimization.pkl'
#model_output.save_with_pickel(path=saveDirOutput, saveName=fileName)


print('\033[92m' + '------success---------' + '\033[0m')
