import sys
import os
import tracemalloc
from delete_function import delete_all_files_in_directory

tracemalloc.start()

a = os.path.dirname(__file__)
a = os.path.dirname(a)


b = a + '/src'
sys.path.append(b)


import outdoor


Excel_Path = "Test_small_AgriLoop.xlsm"
#Excel_Path = "Test_AgriLoop_recycle.xlsm"

Results_Path = r"C:\Users\Lucas\PycharmProjects\OUTDOOR_USC\examples\results\Agriloop_test"



superstructure_Data = outdoor.get_DataFromExcel(Excel_Path)


# solve the optimization problem
abstract_model = outdoor.SuperstructureProblem(parser_type='Superstructure')
model_output = abstract_model.solve_optimization_problem(input_data=superstructure_Data,
                                                         solver='gurobi',
                                                         interface='local',
                                                         optimization_mode= "single")


current, peak = tracemalloc.get_traced_memory()
print(f"Current memory usage is {current / 10**6}MB; Peak was {peak / 10**6}MB")


model_output.get_results(savePath=Results_Path) # if you want to save the results as a txt file, you have to specify the path

# delete old file in the results directory
delete_all_files_in_directory(Results_Path)

# save and analyze the new results
analyzer = outdoor.BasicModelAnalyzer(model_output)


# create the flow sheets of the superstructure and the optimised flow sheet
outdoor.create_superstructure_flowsheet(superstructure_Data, Results_Path) # todo would be better if the flowsheet could be produced prior to the optimization
analyzer.create_flowsheet(Results_Path)

