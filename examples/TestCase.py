import sys
import os


import tracemalloc
tracemalloc.start()

a = os.path.dirname(__file__)
a = os.path.dirname(a)


b = a + '/src'
sys.path.append(b)


import outdoor

#Solver_Path = 'C:/Users/swbkeph/Desktop/OUTDOOR - Kopie/src/outdoor/solver_executables/cbc/bin/cbc.exe'

Excel_Path = "Test_small_V2.xlsm"

# Results_Path = os.path.dirname(a) + "/examples/results/"
Results_Path = r"C:\Users\Lucas\PycharmProjects\OUTDOOR_V2\examples\results"

Data_Path = os.path.dirname(a) + '/outdoor_examples/data/'

superstructure_instance = outdoor.get_DataFromExcel(Excel_Path)



# solve the optimization problem
Opt = outdoor.SuperstructureProblem(parser_type='Superstructure')
model_output = Opt.solve_optimization_problem(input_data=superstructure_instance,
                                              solver='gurobi',
                                              interface='local',
                                              optimization_mode= "single")


current, peak = tracemalloc.get_traced_memory()
print(f"Current memory usage is {current / 10**6}MB; Peak was {peak / 10**6}MB")


model_output.get_results(savePath=Results_Path) # if you want to save the results as a txt file, you have to specify the path


# save and analyze the results
analyzer = outdoor.BasicModelAnalyzer(model_output)


# create the flow sheets of the superstructure and the optimised flow sheet
outdoor.create_superstructure_flowsheet(superstructure_instance, Results_Path) # todo would be better if the flowsheet could be produced prior to the optimization
analyzer.create_flowsheet(Results_Path)


# #analyzer._save_results(path=Results_Path, data=superstructure_instance)
# #analyzer._print_results()
# #analyzer._save_results(path=Results_Path, data=superstructure_instance)
# #analyzer._print_results(model_output)
# analyzer.techno_economic_analysis()
