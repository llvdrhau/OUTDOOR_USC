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
Excel_Path = "Excel_files/potato_peel_case_study_reduced.xlsm"
Results_Path_stochatic = r"C:\Users\Lucas\PycharmProjects\OUTDOOR_USC\examples\results\potato_peel_case_study\stochastic\reduced_stochastic"
savePathPLots = Results_Path_stochatic + "/plots"

# set optimization mode
optimization_mode = "2-stage-recourse"

# create the superstructure data from the Excel file and
superstructure_Data = outdoor.get_DataFromExcel(Excel_Path, optimization_mode=optimization_mode)

# create the superstructure flowsheet
outdoor.create_superstructure_flowsheet(superstructure_Data, savePathPLots)

# solve the optimization problem
abstract_model = outdoor.SuperstructureProblem(parser_type='Superstructure')
solverOptions = {"IntFeasTol": 1e-8,  # tolerance for integer feasibility
                 "NumericFocus": 0}   # 0: balanced, 1: feasibility, 2: optimality, 3: feasibility and optimality

model_output = abstract_model.solve_optimization_problem(input_data=superstructure_Data,
                                                         optimization_mode=optimization_mode,
                                                         solver='gurobi',
                                                         interface='local',
                                                         calculation_VSS=True,
                                                         calculation_EVPI=True,
                                                         options=solverOptions,)

current, peak = tracemalloc.get_traced_memory()
print(f"Current memory usage is {current / 10 ** 6}MB; Peak was {peak / 10 ** 6}MB")

if model_output._optimization_mode == "2-stage-recourse":  # stochastic optimization
    # delete old file in the results directory, so it does not pile up
    delete_all_files_in_directory(directory_path=Results_Path_stochatic)
    # save the results as a txt file, you have to specify the path
    model_output.get_results(savePath=Results_Path_stochatic, pprint=True)
    # make a plot of the results

    # ------------- plot the results of the optimization problem -----------------

    # # probabilty density function of the EBIT
    model_output.plot_scenario_analysis_PDF(variable="OPEX", savePath=savePathPLots, xlabel="OPEX (M€/a)"
                                                  ,saveName="OPEX")
    kde = model_output.plot_scenario_analysis_PDF(variable="EBIT", savePath=savePathPLots, xlabel="EBIT (M€/a)"
                                                  , saveName="EBIT")
    prob = model_output.calculate_odds_in_range(kde=kde, range_start=2, range_end=2.5)
    print(prob)
    #
    # # probabilty density function of the energy demand of the drying unit
    # variable = {"Variable":"ENERGY_DEMAND_TOT",
    #            "UT": "Electricity",} # Drying of pulp
    #
    # kde2 = model_output.plot_scenario_analysis_PDF(variable=variable, savePath=savePathPLots, xlabel="EBIT (M€/a)")

    # model_output.plot_scenario_analysis_histogram(variable="EBIT", savePath=savePathPLots, xlabel="EBIT (M€/a)")

    # polt the capex distribution of all the unit operations in the final flowsheet
    model_output.plot_capex_pie_chart(savePath=savePathPLots)

    #  --------------------------------------------------------------------------------------------------------------
    # ----------------------------------------------------------------------------------------------------------------

    # save and analyze the new results
    analyzer = outdoor.BasicModelAnalyzer(model_output)
    # create the flow sheets of the superstructure and the optimized flow sheet
    analyzer.create_flowsheet(path=Results_Path_stochatic)
