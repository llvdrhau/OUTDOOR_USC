"""
This is the case-study of the potato peel residue for the project AGRILOOP.
Made by Philippe Kenkle adapted by Lucas Van der Hauwaert

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
Excel_Path = "Excel_files/potato_peel_case_study.xlsm"
Results_Path = r"C:\Users\Lucas\PycharmProjects\OUTDOOR_USC\examples\results\potato_peel_case_study"
Results_Path_single = r"C:\Users\Lucas\PycharmProjects\OUTDOOR_USC\examples\results\potato_peel_case_study\single"
Results_Path_sensitivity = r"C:\Users\Lucas\PycharmProjects\OUTDOOR_USC\examples\results\potato_peel_case_study\sensitivity"
Results_Path_cross_sensitivity = r"C:\Users\Lucas\PycharmProjects\OUTDOOR_USC\examples\results\potato_peel_case_study\cross_sensitivity"
Results_Path_stochatic = r"C:\Users\Lucas\PycharmProjects\OUTDOOR_USC\examples\results\potato_peel_case_study\stochastic"


# set optimization mode
#optimization_mode = 'single'
#optimization_mode= 'sensitivity'
#optimization_mode = 'cross-parameter sensitivity'
optimization_mode = "2-stage-recourse"



# create the superstructure data from the Excel file and
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
                                                         calculation_VSS=False,
                                                         calculation_EVPI=False,
                                                         options=solverOptions,)

current, peak = tracemalloc.get_traced_memory()
print(f"Current memory usage is {current / 10 ** 6}MB; Peak was {peak / 10 ** 6}MB")

if model_output._optimization_mode == "single":  # single run optimization
    print('Single optimization problem run')
    # delete old file in the results directory, so it does not pile up
    delete_all_files_in_directory(Results_Path_single)
    # save the results as a txt file, you have to specify the path
    model_output.get_results(savePath=Results_Path_single)
    # save and analyze the new results
    analyzer = outdoor.BasicModelAnalyzer(model_output)
    # create the flow sheets of the superstructure and the optimized flow sheet
    analyzer.create_flowsheet(Results_Path_single)

elif model_output._optimization_mode == "sensitivity":  # single run optimization

    model_output.get_results(savePath=Results_Path_sensitivity, pprint=False)
    # make an analysis of the results by creating the analysis object and calling the method
    analyzer = outdoor.AdvancedMultiModelAnalyzer(model_output)
    fig = analyzer.create_sensitivity_graph(savePath=Results_Path_sensitivity,
                                            saveName="sensitivity_part2",
                                            figureMode="single")

elif model_output._optimization_mode == "cross-parameter sensitivity":
    # delete old file in the results directory, so it does not pile up
    # save the results as a txt file, you have to specify the path
    model_output.get_results(savePath=Results_Path_cross_sensitivity, pprint=True)
    # save and analyze the new results
    analyzer = outdoor.AdvancedMultiModelAnalyzer(model_output)
    # create figure cross-parameter sensitivity
    analyzer.create_cross_parameter_plot(processList=[2000, 5000, 9700, 7000], objective='EBIT',
                                         savePath=Results_Path_cross_sensitivity,
                                         saveName="MP_yield_vs_Starch_comp.png")

#
elif model_output._optimization_mode == "2-stage-recourse":  # single run optimization
     # delete old file in the results directory, so it does not pile up
     #delete_all_files_in_directory(directory_path=Results_Path_stochatic)
     # save the results as a txt file, you have to specify the path
     model_output.get_results(savePath=Results_Path_stochatic, pprint=True)
     # save and analyze the new results
     analyzer = outdoor.BasicModelAnalyzer(model_output)
     # create the flow sheets of the superstructure and the optimized flow sheet
     analyzer.create_flowsheet(path=Results_Path_stochatic)





# for key, val in self.theta:
#     if val != 0:
#         print(f"theta_{key} = {val}")
