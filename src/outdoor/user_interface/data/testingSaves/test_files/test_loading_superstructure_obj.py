import pickle
import outdoor
from outdoor.outdoor_core.input_classes.superstructure import Superstructure
# Load the data from the file
path = r'/outdoor/user_interface/data/testingSaves/test_files/test_small_superstructure.pkl'
with open(path, 'rb') as file:
    superstructureObj = pickle.load(file)

#
savePathPLots = r'C:\Users\Lucas\PycharmProjects\OUTDOOR_USC\src\outdoor\user_interface\data\testingSaves'
outdoor.create_superstructure_flowsheet(superstructure=superstructureObj,
                                        path=savePathPLots,
                                        saveName='test_small_fig')


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
model_output.get_results(path=savePathPLots,
                         saveName='test_small_output')
# save and analyze the new results
analyzer = outdoor.BasicModelAnalyzer(model_output)
# create the flow sheets of the superstructure and the optimized flow sheet
analyzer.create_flowsheet(path=savePathPLots,
                          saveName='test_small_outputFig')
