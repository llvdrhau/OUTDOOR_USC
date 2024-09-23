"""
Author: Lucas Van der Hauwaert, 07/2024

Part 4.2 PHA production costs and profitability analysis. What are the production costs of PHA. Or in other words what
is the price you need to sell PHA to break even. Singles out the processing pathway of PHA production routes in the PPW
case study, with single objective optimization.

Questions to anwser:
- What price do you need to sell PHA to break even?
- analyzes costs and revenues of the PHA production
- determines the profitability of the PHA production

Objective: NPC (minimize Net Production Cost)
Optimization mode: Single
Excel file: potato_peel_case_PHA_production.xlsm

Generated files:
- results/Part_4_2_pha_superstructure.png: the sensitivity analysis plot
- results/Part_4_2_pha_optimized_flowsheet.png: the optimized flowsheet
- results/Part_4_2_pha_production_optimization_results.txt: the optimization results
- see Notes for the results from the console
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
Excel_Path = "../Excel_files/potato_peel_case_PHA_route.xlsm"

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
                                        saveName='Part_4_2_PHA_production_superstructure')


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



#model_output._data
print('Single optimization problem run')
# save the results as a txt file, you have to specify the path
model_output.get_results(pprint=True)

# save and analyze the new results
analyzer = outdoor.BasicModelAnalyzer(model_output)
# create the flow sheets of the superstructure and the optimized flow sheet
analyzer.create_flowsheet(path=savePathPLots,
                          saveName='Part_4_2_PHA_production_optimized_flowsheet')
print('\033[92m' + '------sucess---------'+ '\033[0m')
