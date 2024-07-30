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


n_scenarios = 100

saveName = 'WaS_{}_sc.pkl'.format(n_scenarios)

Saved_data_Path = r'C:\Users\Lucas\PycharmProjects\OUTDOOR_USC\examples\scripts_AgriLoop_PPW\saved_files'
# define the paths to the Excel file and the results directories
#Excel_Path = '../../examples/Excel_files/potato_peel_case_study.xlsm'
Excel_Path = '../../examples/Excel_files/potato_peel_case_study_reduced.xlsm'
Results_Path = r'C:\Users\Lucas\PycharmProjects\OUTDOOR_USC\examples\scripts_AgriLoop_PPW\results'


# set optimization mode
optimization_mode = 'wait and see'

# create the superstructure data from the Excel file
superstructure_Object = outdoor.get_DataFromExcel(Excel_Path,
                                                  optimization_mode=optimization_mode,
                                                  scenario_size=n_scenarios,
                                                  seed=45)

# check if the uncertainty data is correct
superstructure_Object.check_uncertainty_data()

# create the superstructure flowsheet
outdoor.create_superstructure_flowsheet(superstructure_Object, Results_Path)

# solve the optimization problem
abstract_model = outdoor.SuperstructureProblem(parser_type='Superstructure')
solverOptions = {"IntFeasTol": 1e-8,  # tolerance for integer feasibility
                 "NumericFocus": 0}   # 0: balanced, 1: feasibility, 2: optimality, 3: feasibility and optimality

model_output = abstract_model.solve_optimization_problem(input_data=superstructure_Object,
                                                         optimization_mode=optimization_mode,
                                                         solver='gurobi',
                                                         interface='local',
                                                         options=solverOptions,)

# save the results in a pickle file for further analysis
model_output.save_with_pickel(path=Saved_data_Path, saveName=saveName)


# print in green
print('\033[92m' + '------sucess---------')


