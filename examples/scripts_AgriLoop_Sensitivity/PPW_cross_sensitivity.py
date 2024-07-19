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

# define parameters for the cross sensitivity analysis
cross_sensitivity_parameters_1 = {
    "Parameter_Type": ["Price (ProductPrice)_1", "Price (ProductPrice)_2"],
    "Unit_Number": [9700, 2000],
    "Component": ["n.a.", "n.a."],
    "Target_Unit": ["n.a.", "n.a."],
    "Reaction_Number": ["n.a.", "n.a."],
    "Lower_Bound": [1200, 500],
    "Upper_Bound": [1800, 1000],
    "Number_of_steps": [5, 5]
}

cross_sensitivity_parameters_2 = {
    "Parameter_Type": ["Price (ProductPrice)", "Electricity price (delta_ut)"],
    "Unit_Number": [9700, "n.a."],
    "Component": ["n.a.", "n.a."],
    "Target_Unit": ["n.a.", "n.a."],
    "Reaction_Number": ["n.a.", "n.a."],
    "Lower_Bound": [1200, 70],
    "Upper_Bound": [1800, 180],
    "Number_of_steps": [5, 5]
}


cross_sensitivity_parameters_3 = {
    "Parameter_Type": ["Split factors (myu)", "Price (ProductPrice)"],
    "Unit_Number": [300, 3000],
    "Component": ["Phenolics", "n.a."],
    "Target_Unit": ["320", "n.a."],
    "Reaction_Number": ["n.a.", "n.a."],
    "Lower_Bound": [0.2, 3000],
    "Upper_Bound": [0.8, 8000],
    "Number_of_steps": [5, 5]
}

cross_sensitivity_parameters_4= {
    "Parameter_Type": ["Stoichiometric factor (gamma)", "Conversion factor (theta)"],
    "Unit_Number": [400, 200],
    "Component": ["VFA", "Cellulose "], # don't forget the space... dangerous mistake possible, fix in Excel
    "Target_Unit": ["n.a.", "n.a."],
    "Reaction_Number": [13, 14],
    "Lower_Bound": [0.35, 0.5],
    "Upper_Bound": [0.75, 0.8],
    "Number_of_steps": [5, 5]
}




Excel_Path = "../Excel_files/potato_peel_case_study.xlsm"
Results_Path_cross_sensitivity = r"/examples/results/potato_peel_case_study/cross_sensitivity"

# make a list of all the dicts
saveNames = ['VFA_vs_Cellulose'] # 'EthoH_vs_MP', 'EthoH_vs_Elec', 'Phenolics_vs_MP',
cross_sensitivity_parameters = [ cross_sensitivity_parameters_4] #cross_sensitivity_parameters_1, cross_sensitivity_parameters_2, cross_sensitivity_parameters_3,

optimization_mode = 'cross-parameter sensitivity'



for i, cross_sensitivity_parameter in enumerate(cross_sensitivity_parameters):
    # create the superstructure data from the Excel file and
    superstructure_Data = outdoor.get_DataFromExcel(Excel_Path,
                                                    optimization_mode=optimization_mode,
                                                    cross_sensitivity_params=cross_sensitivity_parameter)
    # solve the optimization problem
    abstract_model = outdoor.SuperstructureProblem(parser_type='Superstructure')
    solverOptions = {"IntFeasTol": 1e-8,  # tolerance for integer feasibility
                     "NumericFocus": 0}  # 0: balanced, 1: feasibility, 2: optimality, 3: feasibility and optimality

    model_output = abstract_model.solve_optimization_problem(input_data=superstructure_Data,
                                                             optimization_mode='cross-parameter sensitivity',
                                                             solver='gurobi',
                                                             interface='local',
                                                             options=solverOptions,
                                                             cross_sensitivity_parameters=cross_sensitivity_parameter)

    model_output.get_results(savePath=Results_Path_cross_sensitivity, saveName=saveNames[i], pprint=True)
    # save and analyze the new results
    analyzer = outdoor.AdvancedMultiModelAnalyzer(model_output)
    # create figure cross-parameter sensitivity
    analyzer.create_cross_parameter_plot(processList=[2000, 5000, 9700], objective='EBIT',
                                         savePath=Results_Path_cross_sensitivity,
                                         saveName=saveNames[i])







