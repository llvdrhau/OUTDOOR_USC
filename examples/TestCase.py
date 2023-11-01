"""
This is a test case for the outdoor package. It is used to test the functionality of the package.
Made by Philippe original adapted by Lucas

possible optimisation modes: "Single run optimization", "Multi-criteria optimization", "Sensitivity analysis",
"Cross-parameter sensitivity" , and "Single 2-stage recourse optimization"
"""
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

# define the paths
Excel_Path = "Test_small_V2.xlsm"
Results_Path = r"C:\Users\Lucas\PycharmProjects\OUTDOOR_USC\examples\results\philipp_test\single"
Results_Path_multi = r"C:\Users\Lucas\PycharmProjects\OUTDOOR_USC\examples\results\philipp_test\multi"
Results_Path_sensitivity = r"C:\Users\Lucas\PycharmProjects\OUTDOOR_USC\examples\results\philipp_test\sensitivity"
Results_Path_cross_sensitivity = r"C:\Users\Lucas\PycharmProjects\OUTDOOR_USC\examples\results\philipp_test\cross_sensitivity"

Data_Path = os.path.dirname(a) + '/outdoor_examples/data/'

superstructure_instance = outdoor.get_DataFromExcel(Excel_Path)

# check the super structure flow sheet for errors
pathSuperstructureFigure = r"C:\Users\Lucas\PycharmProjects\OUTDOOR_USC\examples\results\philipp_test"
outdoor.create_superstructure_flowsheet(superstructure_instance, pathSuperstructureFigure)

# solve the optimization problem
Opt = outdoor.SuperstructureProblem(parser_type='Superstructure')
model_output = Opt.solve_optimization_problem(input_data=superstructure_instance,
                                              solver='gurobi', # gurobi
                                              interface='local')


current, peak = tracemalloc.get_traced_memory()
print(f"Current memory usage is {current / 10**6}MB; Peak was {peak / 10**6}MB")

# specific place to save the results

if model_output._optimization_mode == "Single run optimization": # single run optimization
    # delete old file in the results directory, so it does not pile up
    delete_all_files_in_directory(Results_Path)

    # if you want to save the results as a txt file, you have to specify the path
    model_output.get_results(savePath=Results_Path)

    # make an analysis of the results by creating the analysis object and calling the method
    analyzer = outdoor.BasicModelAnalyzer(model_output)

    # create the flow sheets of the superstructure and the optimised flow sheet
    analyzer.create_flowsheet(Results_Path)
    # analyzer.techno_economic_analysis() # Todo fix this, does not work

elif model_output._optimization_mode == 'Multi-criteria optimization':
    # if you want to save the results as a txt file, you have to specify the path
    model_output.get_results(savePath=Results_Path_multi)
    # make an analysis of the results by creating the analysis object and calling the method
    analyzer = outdoor.AdvancedMultiModelAnalyzer(model_output)
    analyzer.create_mcda_table(table_type= 'relative closeness')

elif model_output._optimization_mode == 'Sensitivity analysis':
    # if you want to save the results as a txt file, you have to specify the path
    model_output.get_results(savePath=Results_Path_sensitivity)
    # make an analysis of the results by creating the analysis object and calling the method
    analyzer = outdoor.AdvancedMultiModelAnalyzer(model_output)
    fig = analyzer.create_sensitivity_graph(savePath=Results_Path_sensitivity)
    fig.show()

elif model_output._optimization_mode == 'Cross-parameter sensitivity':
    # if you want to save the results as a txt file, you have to specify the path
    model_output.get_results(savePath=Results_Path_cross_sensitivity)
    # make an analysis of the results by creating the analysis object and calling the method
    analyzer = outdoor.AdvancedMultiModelAnalyzer(model_output)
    # analyzer.create_crossparameter_graph()







