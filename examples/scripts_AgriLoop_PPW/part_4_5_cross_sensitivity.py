import sys
import os
import tracemalloc

scrPath = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src'))
sys.path.insert(0, scrPath)
import outdoor


levels = 20

# define parameters for the cross sensitivity analysis
cross_sensitivity_parameters_1 = {
    "Parameter_Type": ["Stoichiometric factor (gamma)", "Split factors (myu)"],
    "Unit_Number": [435, 438],
    "Component": ["PHA", "PHA"],
    "Target_Unit": ["n.a.", 440],
    "Reaction_Number": [11, "n.a."],
    "Lower_Bound": [0.4, 0.4],
    "Upper_Bound": [0.9, 0.9],
    "Number_of_steps": [levels, levels]
}

# define parameters for the cross sensitivity analysis
cross_sensitivity_parameters_2 = {
    "Parameter_Type": ["Price (ProductPrice)", "Split factors (myu)"],
    "Unit_Number": [6000, 438],
    "Component": ["n.a.", "PHA"],
    "Target_Unit": ["n.a.", 440],
    "Reaction_Number": ["n.a.", "n.a."],
    "Lower_Bound": [4500, 0.4],
    "Upper_Bound": [7000, 0.95],
    "Number_of_steps": [levels, levels]
}

cross_sensitivity_parameters_3 = {
    "Parameter_Type": ["Price (ProductPrice)", "Stoichiometric factor (gamma)"],
    "Unit_Number": [6000, 435],
    "Component": ["n.a.", "PHA"],
    "Target_Unit": ["n.a.", "n.a."],
    "Reaction_Number": ["n.a.", 11],
    "Lower_Bound": [4500, 0.4],
    "Upper_Bound": [7000, 0.95],
    "Number_of_steps": [levels, levels]
}




Excel_Path = "../Excel_files/potato_peel_case_PHA_uncertainty.xlsm"
# define save locations
current_script_dir = os.path.dirname(os.path.abspath(__file__))
results_dir = os.path.join(current_script_dir, 'results')
savePathPLots = results_dir


# make a list of all the dicts
saveNames = ['Part_4_4 cross sensitivity myu_gamma',
             'Part_4_4 cross sensitivity price_gamma',
             'Part_4_4 cross sensitivity price_myu']

cross_sensitivity_parameters = [cross_sensitivity_parameters_1,
                                cross_sensitivity_parameters_2,
                                cross_sensitivity_parameters_3]

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

    model_output.get_results(savePath=results_dir, saveName=saveNames[i], pprint=True)
    # save and analyze the new results
    analyzer = outdoor.AdvancedMultiModelAnalyzer(model_output)
    # create figure cross-parameter sensitivity
    analyzer.create_cross_parameter_plot(processList=[6000, 410], objective='EBIT',
                                         savePath=results_dir,
                                         saveName=saveNames[i],
                                         simpleContour=True,
                                         levels=levels,)







