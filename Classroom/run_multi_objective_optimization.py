import copy
import pickle
import os
import outdoor
from outdoor.outdoor_core.input_classes.superstructure import Superstructure

# get the current working directory
current_path = os.getcwd()

# add the relevant file name to the current working directory
path = os.path.join(current_path, "test_superstructure.pkl")

# open the file and load the superstructure object
with open(path, 'rb') as file:
    superstructureObj = pickle.load(file)

# define the save location for the results
savePath = os.path.join(current_path, 'results_multi_objective')

### uncomment the following line if you want to create the superstructure
outdoor.create_superstructure_flowsheet(superstructure=superstructureObj,
                                        path=savePath,
                                        saveName='Figure_superstructure')

# create the solver object
solverObject = outdoor.SuperstructureProblem(parser_type='Superstructure')

# set solver options, you can change the options according to your needs
solverOptions = {"IntFeasTol": 1e-8,  # tolerance for integer feasibility
                 "NumericFocus": 0}   # 0: balanced, 1: feasibility, 2: optimality, 3: feasibility and optimality

# define the objective pairs and their labels
objectivePair = ('global warming potential (GWP100)', 'NPC')

# create the options for the multi-objective optimization
multi_objective_options = { "objective1": 'NPC',  # first objective
                            'bounds_objective1': [None, None],  # [lower_bound, upper_bound]
                            "objective2": 'global warming potential (GWP100)', # second objective
                            "paretoPoints": 25} # number of points in the Pareto front

# FIXME instead of writing NPC use "-EBIT" which switches the objective to NPC


# solve the multi-objective optimization problem
model_output = solverObject.solve_optimization_problem(input_data=superstructureObj,
                                                       optimization_mode='multi-objective',
                                                       multi_objective_options=multi_objective_options,
                                                       solver='gurobi',
                                                       interface='local',
                                                       options=solverOptions,)

# difine a file key for saving the results
fileKey = 'GWP_NPC'

# get results and save them
model_output.get_results(savePath=savePath, pprint=False, saveName=fileKey + '_results')
analyzer = outdoor.AdvancedMultiModelAnalyzer(model_output)
analyzer.create_all_flow_sheets_multi_objectives(path=savePath)
analyzer.plot_pareto_front(path=savePath,
                           saveName=fileKey + '_pareto_front',
                           xLabel='global warming potential (kg_CO2_Eq/kg_TP)',
                           # carefull to name the xLabel correctly according to objective 1
                           yLabel='Earning Before Income Taxes (€/ton)',
                           # carefull to name the yLabel correctly, according to objective 2
                           flowTreshold=1e-5)




# objectivePairs = {
#     'GWP_NPC':('global warming potential (GWP100)', 'NPC'),
#     'TETP_NPC':('terrestrial ecotoxicity potential (TETP)', 'NPC'),
#     'FETP_NPC':('freshwater ecotoxicity potential (FETP)', 'NPC'),
#     'HTPnc_NPC':('human toxicity potential (HTPnc)', 'NPC'),
#     'NPC_GWP':('NPC', 'global warming potential (GWP100)'),
#     'NPC_HTPc':('NPC', 'human toxicity potential (HTPc)'),
#     'GWP_TETP':('global warming potential (GWP100)', 'terrestrial ecotoxicity potential (TETP)'),
#     'GWP_FETP':('global warming potential (GWP100)', 'freshwater ecotoxicity potential (FETP)'),
#     'GWP_HTPc':('global warming potential (GWP100)', 'human toxicity potential (HTPc)'),
#     'TETP_FETP':('terrestrial ecotoxicity potential (TETP)', 'freshwater ecotoxicity potential (FETP)'),
#     'TETP_HTPc':('terrestrial ecotoxicity potential (TETP)', 'human toxicity potential (HTPc)'),
#     'FETP_HTPc':('freshwater ecotoxicity potential (FETP)', 'human toxicity potential (HTPc)')
# }

