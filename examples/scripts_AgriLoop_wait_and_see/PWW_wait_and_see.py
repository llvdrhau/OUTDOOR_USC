"""
This is the case-study of the potato peel residue for the project AGRILOOP.
Made by Philippe Kenkle adapted by Lucas Van der Hauwaert

optimization mode: wait and see
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
#Excel_Path = '../../examples/Excel_files/potato_peel_case_study.xlsm'
Excel_Path = '../../examples/Excel_files/potato_peel_case_study_reduced.xlsm'
Results_Path = r'C:\Users\Lucas\PycharmProjects\OUTDOOR_USC\examples\scripts_AgriLoop_wait_and_see\results'


# set optimization mode
optimization_mode = 'wait and see'

# create the superstructure data from the Excel file
superstructure_Data = outdoor.get_DataFromExcel(Excel_Path, optimization_mode=optimization_mode)

# create the superstructure flowsheet
outdoor.create_superstructure_flowsheet(superstructure_Data, Results_Path)

# solve the optimization problem
abstract_model = outdoor.SuperstructureProblem(parser_type='Superstructure')
solverOptions = {"IntFeasTol": 1e-8,  # tolerance for integer feasibility
                 "NumericFocus": 0}   # 0: balanced, 1: feasibility, 2: optimality, 3: feasibility and optimality

model_output = abstract_model.solve_optimization_problem(input_data=superstructure_Data,
                                                         optimization_mode=optimization_mode,
                                                         solver='gurobi',
                                                         interface='local',
                                                         options=solverOptions,)

# current, peak = tracemalloc.get_traced_memory()
# print(f"Current memory usage is {current / 10 ** 6}MB; Peak was {peak / 10 ** 6}MB")

saveName = 'WaS_100_sc.pkl'
Saved_data_Path = r'C:\Users\Lucas\PycharmProjects\OUTDOOR_USC\examples\scripts_AgriLoop_wait_and_see\saved_data'
model_output.save_with_pickel(path=Saved_data_Path, saveName=saveName)


# print in green
print('\033[92m' + '------sucess---------')


