import copy
import pickle
import os
import outdoor
from outdoor.outdoor_core.input_classes.superstructure import Superstructure

# Load the data from the file
# get current working directory
current_path = os.getcwd()
# add the file name Aurelie_peptide_production_superstructure.pkl to the current working directory
path = os.path.join(current_path, "TP_case_study_superstructure.pkl")
with open(path, 'rb') as file:
    superstructureObj = pickle.load(file)

mainFolder = os.path.join(current_path, "multiObj")


# outdoor.create_superstructure_flowsheet(superstructure=superstructureObj,
#                                         path=savePath,
#                                         saveName='Figure_superstructure')


# solve the optimization problem
solverObject = outdoor.SuperstructureProblem(parser_type='Superstructure')
solverOptions = {"IntFeasTol": 1e-8,  # tolerance for integer feasibility
                 "NumericFocus": 0}   # 0: balanced, 1: feasibility, 2: optimality, 3: feasibility and optimality

objectivePairs = {
    'GWP_NPC':('global warming potential (GWP100)', 'NPC'),
    'TETP_NPC':('terrestrial ecotoxicity potential (TETP)', 'NPC'),
    'FETP_NPC':('freshwater ecotoxicity potential (FETP)', 'NPC'),
    'HTPnc_NPC':('human toxicity potential (HTPnc)', 'NPC'),

    # 'NPC_GWP':('NPC', 'global warming potential (GWP100)'),
    # 'NPC_HTPc':('NPC', 'human toxicity potential (HTPc)'),
    # 'GWP_TETP':('global warming potential (GWP100)', 'terrestrial ecotoxicity potential (TETP)'),
    # 'GWP_FETP':('global warming potential (GWP100)', 'freshwater ecotoxicity potential (FETP)'),
    # 'GWP_HTPc':('global warming potential (GWP100)', 'human toxicity potential (HTPc)'),
    # 'TETP_FETP':('terrestrial ecotoxicity potential (TETP)', 'freshwater ecotoxicity potential (FETP)'),
    # 'TETP_HTPc':('terrestrial ecotoxicity potential (TETP)', 'human toxicity potential (HTPc)'),
    # 'FETP_HTPc':('freshwater ecotoxicity potential (FETP)', 'human toxicity potential (HTPc)')
}
modelOutputList = []
xLabels = ['Global warming potential (kg_CO2_Eq/kg_TP)',
           'terrestrial ecotoxicity potential (kg 1,4-DCB-Eq/kg_TP)',
           'freshwater ecotoxicity potential (kg 1,4-DCB-Eq/kg_TP)',
           'human toxicity potential (kg 1,4-DCB-Eq/kg_TP)']

counter = 0
for fileKey, objectivePair in objectivePairs.items():
    xlab = xLabels[counter]
    counter += 1
    multi_objective_options = { "objective1": objectivePair[0],
                                'bounds_objective1': [None, None],  # [lower_bound, upper_bound]
                                "objective2": objectivePair[1],
                                "paretoPoints": 25}

    model_output = solverObject.solve_optimization_problem(input_data=superstructureObj,
                                                           optimization_mode='multi-objective',
                                                           multi_objective_options=multi_objective_options,
                                                           solver='gurobi',
                                                           interface='local',
                                                           calculation_VSS=False,
                                                           calculation_EVPI=False,
                                                           options=solverOptions,)


    # nSim = len(model_output._results_data)
    # print('Number of simulations: ', nSim)
    # get the analyzer
    # get the correct path to save the results
    savePath = os.path.join(mainFolder, fileKey)
    model_output.get_results(savePath=savePath, pprint=False, saveName=fileKey + '_results')

    analyzer = outdoor.AdvancedMultiModelAnalyzer(model_output)
    analyzer.create_all_flow_sheets_multi_objectives(path=savePath)
    analyzer.plot_pareto_front(path=savePath,
                               saveName=fileKey + '_pareto_front', xLabel=xlab,
                               yLabel='Earning Before Income Taxes (€/ton)', flowTreshold=1e-5)

    modelOutputList.append(copy.deepcopy(model_output))


# make a subplot of all the pareto fronts in one figure
# get the correct path to save the results
#savePath = os.path.join(mainFolder, 'pareto_fronts_sub_plot')
analyzer.sub_plot_pareto_fronts(modelOutputList, path=mainFolder,
                                saveName='pareto_fronts_sub_plot', xLabel=xLabels,
                                yLabel=['Earning Before Income Taxes (€/ton)',
                                        'Earning Before Income Taxes (€/ton)',
                                        'Earning Before Income Taxes (€/ton)',
                                        'Earning Before Income Taxes (€/ton)'],
                                flowTreshold=1e-5)


