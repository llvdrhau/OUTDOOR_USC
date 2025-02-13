import pickle
import os
import outdoor
from outdoor.outdoor_core.input_classes.superstructure import Superstructure

# Load the data from the file
# get current working directory
current_path = os.getcwd()
# add the file name to the current working directory
path = os.path.join(current_path, "TP_case_study_superstructure.pkl")
with open(path, 'rb') as file:
    superstructureObj = pickle.load(file)

#savePath = current_path
savePath = os.path.join(current_path, "aggreated_test")


# solve the optimization problem
solverObject = outdoor.SuperstructureProblem(parser_type='Superstructure')
solverOptions = {"IntFeasTol": 1e-8,  # tolerance for integer feasibility
                 "NumericFocus": 0}   # 0: balanced, 1: feasibility, 2: optimality, 3: feasibility and optimality

objectivePairs = {
    'GWP_NPC_aggregated':('global warming potential (GWP100)', 'NPC'),
    # 'NPC_GWP':('NPC', 'global warming potential (GWP100)'),
    # 'TETP_NPC':('terrestrial ecotoxicity potential (TETP)', 'NPC'),
    # 'FETP_NPC':('freshwater ecotoxicity potential (FETP)', 'NPC'),
    # 'HTPc_NPC':('human toxicity potential (HTPc)', 'NPC'),
    # 'NPC_HTPc':('NPC', 'human toxicity potential (HTPc)'),
    # 'GWP_TETP':('global warming potential (GWP100)', 'terrestrial ecotoxicity potential (TETP)'),
    # 'GWP_FETP':('global warming potential (GWP100)', 'freshwater ecotoxicity potential (FETP)'),
    # 'GWP_HTPc':('global warming potential (GWP100)', 'human toxicity potential (HTPc)'),
    # 'TETP_FETP':('terrestrial ecotoxicity potential (TETP)', 'freshwater ecotoxicity potential (FETP)'),
    # 'TETP_HTPc':('terrestrial ecotoxicity potential (TETP)', 'human toxicity potential (HTPc)'),
    # 'FETP_HTPc':('freshwater ecotoxicity potential (FETP)', 'human toxicity potential (HTPc)')
}


for fileKey, objectivePair in objectivePairs.items():
    multi_objective_options = { "objective1": objectivePair[0],
                                'bounds_objective1': [None, None], # [lower_bound, upper_bound]
                                "objective2": objectivePair[1],
                                "paretoPoints": 5,
                                # options for the design space if applicable
                                "design_space_mode": True,
                                "sample_size": 200,
                                "design_space_bounds": {'min_obj1': None,
                                                        'max_obj1': 65,
                                                        'min_obj2': None,
                                                        'max_obj2': 400},
                                }

    model_output = solverObject.solve_optimization_problem(input_data=superstructureObj,
                                                           optimization_mode='multi-objective',
                                                           multi_objective_options=multi_objective_options,
                                                           solver='gurobi',
                                                           interface='local',
                                                           calculation_VSS=False,
                                                           calculation_EVPI=False,
                                                           options=solverOptions,)

    analyzer = outdoor.AdvancedMultiModelAnalyzer(model_output)
    #savePath = os.path.join(current_path, fileKey)
    analyzer.plot_pareto_front(path=savePath, saveName=fileKey + '_pareto_front', flowTreshold=1e-5)





