import pickle
import os
import outdoor
from outdoor.outdoor_core.input_classes.superstructure import Superstructure

# Load the data from the file
# get current working directory
current_path = os.getcwd()
# add the file name Aurelie_peptide_production_superstructure.pkl to the current working directory
path = os.path.join(current_path, "Tomato_Pomace_superstructure_superstructure.pkl")
with open(path, 'rb') as file:
    superstructureObj = pickle.load(file)

savePath = current_path
# outdoor.create_superstructure_flowsheet(superstructure=superstructureObj,
#                                         path=savePath,
#                                         saveName='Figure_superstructure')


# solve the optimization problem
solverObject = outdoor.SuperstructureProblem(parser_type='Superstructure')
solverOptions = {"IntFeasTol": 1e-8,  # tolerance for integer feasibility
                 "NumericFocus": 0}   # 0: balanced, 1: feasibility, 2: optimality, 3: feasibility and optimality

multi_objective_options = {"objective1": "EBIT",
                           "objective2": "NPE",
                           "paretoPoints": 10}

model_output = solverObject.solve_optimization_problem(input_data=superstructureObj,
                                                       optimization_mode='multi-objective',
                                                       multi_objective_options=multi_objective_options,
                                                       solver='gurobi',
                                                       interface='local',
                                                       calculation_VSS=False,
                                                       calculation_EVPI=False,
                                                       options=solverOptions,)

# get the analyzer
analyzer = outdoor.AdvancedMultiModelAnalyzer(model_output)
analyzer.create_all_flowsheets(path=savePath)
analyzer.plot_pareto_front(path=savePath,
                           saveName='Test_pareto_front')

