"""
This is the case-study of the potato peel residue for the project AGRILOOP.
Made by Philippe adapted by Lucas

Possible optimization modes: "Single run optimization", "Multi-criteria optimization", "Sensitivity analysis",
"Cross-parameter sensitivity", and "Single 2-stage recourse optimization"
"""

import sys
import os
import tracemalloc
from delete_function import delete_all_files_in_directory


# start the memory profiler
tracemalloc.start()
# add the path to the src folder to the system path
a = os.path.dirname(__file__)
a = os.path.dirname(a)
b = a + '/src'
sys.path.append(b)

import outdoor



# define the paths to the Excel file and the results directories
Excel_Path = "Excel_files/pha_production.xlsm"
path_ss_fig = r"C:\Users\Lucas\PycharmProjects\OUTDOOR_USC\examples\results\test_zone"
Results_Path = r"C:\Users\Lucas\PycharmProjects\OUTDOOR_USC\examples\results\test_zone\pha_production"

# create the superstructure data from the Excel file and
superstructure_Data = outdoor.get_DataFromExcel(Excel_Path)

# create the superstructure flowsheet
outdoor.create_superstructure_flowsheet(superstructure_Data, path_ss_fig)

# solve the optimization problem
abstract_model = outdoor.SuperstructureProblem(parser_type='Superstructure')
solverOptions = {"IntFeasTol": 1e-7,  # tolerance for integer feasibility
                 "NumericFocus": 0}   # 0: balanced, 1: feasibility, 2: optimality, 3: feasibility and optimality

model_output = abstract_model.solve_optimization_problem(input_data=superstructure_Data,
                                                         solver='gurobi',
                                                         interface='local',
                                                         calculation_VSS=False,
                                                         calculation_EVPI=False,
                                                         options=solverOptions,)

current, peak = tracemalloc.get_traced_memory()
print(f"Current memory usage is {current / 10 ** 6}MB; Peak was {peak / 10 ** 6}MB")

if model_output._optimization_mode == "single":  # single run optimization
    print('Single optimization problem run')
    # delete old file in the results directory, so it does not pile up
    delete_all_files_in_directory(Results_Path)
    # save the results as a txt file, you have to specify the path
    model_output.get_results(savePath=Results_Path)
    # save and analyze the new results
    analyzer = outdoor.BasicModelAnalyzer(model_output)
    # create the flow sheets of the superstructure and the optimized flow sheet
    analyzer.create_flowsheet(Results_Path)
#
