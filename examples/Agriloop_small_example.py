import sys
import os
import tracemalloc
from delete_function import delete_all_files_in_directory
from PIL import Image
from IPython.display import display

# start the memory profiler
tracemalloc.start()
# add the path to the src folder to the system path
a = os.path.dirname(__file__)
a = os.path.dirname(a)
b = a + '/src'
sys.path.append(b)


import outdoor

# define the paths to the excel file and the results directory
Excel_Path = "Test_small_AgriLoop.xlsm"
Results_Path = r"C:\Users\Lucas\PycharmProjects\OUTDOOR_USC\examples\results\Agriloop_test"

# delete old file in the results directory, so it does not pile up
delete_all_files_in_directory(Results_Path)

# create the superstructure data from the Excel file and
superstructure_Data = outdoor.get_DataFromExcel(Excel_Path)

# check the variables that are not defined in the Excel file, to filter out typos or errors from the Excel
# NoneVars = superstructure_Data.CheckNoneVariables
# print(NoneVars)

# create the superstructure flowsheet
outdoor.create_superstructure_flowsheet(superstructure_Data, Results_Path)

# display the superstructure flowsheet to check if everything is correct
# Open image file
# imgagePath = Results_Path + '/superstructure_flowsheet.png'
# with Image.open(imgagePath) as img:
#     # Display image
#     display(img)


# solve the optimization problem
abstract_model = outdoor.SuperstructureProblem(parser_type='Superstructure')
# todo would it not be better to use the superstructure_Data object here?
#  that way we could check the model for inconsistencies before solving it

model_output = abstract_model.solve_optimization_problem(input_data=superstructure_Data,
                                                         solver='gurobi',
                                                         interface='local')

current, peak = tracemalloc.get_traced_memory()
print(f"Current memory usage is {current / 10**6}MB; Peak was {peak / 10**6}MB")


model_output.get_results(savePath=Results_Path) # if you want to save the results as a txt file, you have to specify the path


# save and analyze the new results
analyzer = outdoor.BasicModelAnalyzer(model_output)

# create the flow sheets of the superstructure and the optimised flow sheet
analyzer.create_flowsheet(Results_Path)

