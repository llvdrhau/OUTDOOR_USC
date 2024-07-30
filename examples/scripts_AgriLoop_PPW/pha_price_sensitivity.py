'''
Runs a price sensitivity analysis for the PHA production in the AgriLoop case study.
Run a sensitivity analysis for the PHA price and look when it become profitable to produce PHA.
'''

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
ExcelPath = '../../examples/Excel_files/potato_peel_case_study.xlsm'
currentScriptDir = os.path.dirname(__file__)
resultsPath = os.path.join(currentScriptDir, 'results')
saveOutputObjectDir = os.path.join(currentScriptDir, 'saved_files')


# set optimization mode
optimization_mode= 'sensitivity'

# create the superstructure data from the Excel file and
superstructure_Data = outdoor.get_DataFromExcel(path=ExcelPath,
                                                optimization_mode=optimization_mode)

# create the superstructure flowsheet
outdoor.create_superstructure_flowsheet(superstructure=superstructure_Data,
                                        path=resultsPath,
                                        saveName='full_superstructure')

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

current, peak = tracemalloc.get_traced_memory()
print(f"Current memory usage is {current / 10 ** 6}MB; Peak was {peak / 10 ** 6}MB")


analyzer = outdoor.AdvancedMultiModelAnalyzer(model_output)
fig = analyzer.create_sensitivity_graph(savePath=resultsPath,
                                            saveName="sensitivity_pha_price",
                                            figureMode="single")


