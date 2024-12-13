import pickle
import os
import outdoor
from outdoor.outdoor_core.input_classes.superstructure import Superstructure
# Load the data from the file
# get current working directory
current_path = os.getcwd()
# add the file name Aurelie_peptide_production_superstructure.pkl to the current working directory
path = os.path.join(current_path, "Aurelie_peptide_production_superstructure.pkl")
with open(path, 'rb') as file:
    superstructureObj = pickle.load(file)

savePath = current_path #os.path.join(current_path, 'peptide_production_v1')
outdoor.create_superstructure_flowsheet(superstructure=superstructureObj,
                                        path=savePath,
                                        saveName='peptide_production_superstructure')


# solve the optimization problem
abstract_model = outdoor.SuperstructureProblem(parser_type='Superstructure')
solverOptions = {"IntFeasTol": 1e-8,  # tolerance for integer feasibility
                 "NumericFocus": 0}   # 0: balanced, 1: feasibility, 2: optimality, 3: feasibility and optimality

model_output = abstract_model.solve_optimization_problem(input_data=superstructureObj,
                                                         optimization_mode='single',
                                                         solver='gurobi',
                                                         interface='local',
                                                         calculation_VSS=False,
                                                         calculation_EVPI=False,
                                                         options=solverOptions,)

# save the results as a txt file, you have to specify the path
model_output.get_results(path=savePath,
                         saveName='peptide_txt_results')
# save and analyze the new results
analyzer = outdoor.BasicModelAnalyzer(model_output)
# create the flow sheets of the superstructure and the optimized flow sheet
analyzer.create_flowsheet(path=savePath,
                          saveName='flowsheet_peptide_production')
