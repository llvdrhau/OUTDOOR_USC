"""
This is a test case for the outdoor package applied to AGRILOOP. It is used to test the functionality of the package.
Made by Philippe  adapted by Lucas

possible optimisation modes: "Single run optimization", "Multi-criteria optimization", "Sensitivity analysis",
"Cross-parameter sensitivity" , and "Single 2-stage recourse optimization"
"""

import sys
import os
import tracemalloc
from delete_function import delete_all_files_in_directory


#from outdoor import get_DataFromExcel, create_superstructure_flowsheet

# start the memory profiler
tracemalloc.start()
# add the path to the src folder to the system path
a = os.path.dirname(__file__)
a = os.path.dirname(a)
b = a + '/src'
sys.path.append(b)

import outdoor



# define the paths to the Excel file and the results directories
Excel_Path = "ESCAPE34_case_study.xlsm"
Results_Path = r"C:\Users\Lucas\PycharmProjects\OUTDOOR_USC\examples\results\ESCAPE34_case_study"
Results_Path_single = r"C:\Users\Lucas\PycharmProjects\OUTDOOR_USC\examples\results\ESCAPE34_case_study\single"
Results_Path_stochatic = r"C:\Users\Lucas\PycharmProjects\OUTDOOR_USC\examples\results\ESCAPE34_case_study\stochastic"

# create the superstructure data from the Excel file and
superstructure_Data = outdoor.get_DataFromExcel(Excel_Path)
#superstructure_Data = get_DataFromExcel(Excel_Path)

# create the superstructure flowsheet
outdoor.create_superstructure_flowsheet(superstructure_Data, Results_Path)
#create_superstructure_flowsheet(superstructure_Data, Results_Path)

# solve the optimization problem
abstract_model = outdoor.SuperstructureProblem(parser_type='Superstructure')

solverOptions = {"IntFeasTol": 1e-8,  # tolerance for integer feasibility
                 "NumericFocus": 0}   # 0: balanced, 1: feasibility, 2: optimality, 3: feasibility and optimality

model_output = abstract_model.solve_optimization_problem(input_data=superstructure_Data,
                                                         solver='gurobi',
                                                         interface='local',
                                                         calculation_EVPI=False,
                                                         calculation_VSS=False,
                                                         options=solverOptions,)

current, peak = tracemalloc.get_traced_memory()
print(f"Current memory usage is {current / 10 ** 6}MB; Peak was {peak / 10 ** 6}MB")

if model_output._optimization_mode == "Single run optimization":  # single run optimization
    # delete old file in the results directory, so it does not pile up
    delete_all_files_in_directory(Results_Path_single)
    # save the results as a txt file, you have to specify the path
    model_output.get_results(savePath=Results_Path_single)
    # save and analyze the new results
    analyzer = outdoor.BasicModelAnalyzer(model_output)
    # create the flow sheets of the superstructure and the optimized flow sheet
    analyzer.create_flowsheet(Results_Path_single)

elif model_output._optimization_mode == "Single 2-stage recourse optimization":  # stochastic optimization
    # delete old file in the results directory, so it does not pile up
    delete_all_files_in_directory(directory_path=Results_Path_stochatic)
    # save the results as a txt file, you have to specify the path
    model_output.get_results(savePath=Results_Path_stochatic, pprint=True)
    # make a plot of the results

    # # probabilty density function of the EBIT
    # kde = model_output.plot_scenario_analysis_PDF(variable="EBIT", savePath=Results_Path_stochatic, xlabel="EBIT (M€/a)")
    # prob = model_output.calculate_odds_in_range(kde=kde, range_start=0, range_end=3.9)
    # print(prob)

    # probabilty density function of the energy demand of the drying unit
    variable = {"Variable":"ENERGY_DEMAND_TOT",
               "UnitNr": 110,} # Drying of pulp

    kde100 = model_output.plot_scenario_analysis_PDF(variable=variable, savePath=Results_Path_stochatic, xlabel="EBIT (M€/a)")

    #model_output.plot_scenario_analysis_histogram(variable="EBIT", savePath=Results_Path_stochatic, xlabel="EBIT (M€/a)")

    # save and analyze the new results
    analyzer = outdoor.BasicModelAnalyzer(model_output)
    # create the flow sheets of the superstructure and the optimized flow sheet
    analyzer.create_flowsheet(path=Results_Path_stochatic)
