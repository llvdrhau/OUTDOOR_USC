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
}


for fileKey, objectivePair in objectivePairs.items():
    multi_objective_options = { "objective1": objectivePair[0],
                                'bounds_objective1': [None, None], # [lower_bound, upper_bound]
                                "objective2": objectivePair[1],
                                "paretoPoints": 5,
                                # options for the design space if applicable
                                "design_space_mode": True,
                                "sample_size": 100, # 100 better
                                "design_space_bounds": {'min_obj1': None,  # GWP
                                                        'max_obj1': 6,    # GWP
                                                        'min_obj2': None,  # NPC
                                                        'max_obj2': 200},  # NPC
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

    analyzer.plot_pareto_front(path=savePath, saveName=fileKey + '_pareto_front', flowTreshold=1e-5,
                               xLabel='Global warming potential (kg_CO2_eq/kg)',
                               yLabel='Earning Before Income Taxes (€/t)',
                               nProductLimit=3, productExclusionList=['Protein', 'Peptides', 'Cutin2'])

    analyzer.plot_LCA_correlations(path=savePath, saveName='LCA_correlations',
                                   catagories=['global warming potential (GWP100)',
                                               'terrestrial ecotoxicity potential (TETP)',
                                               'freshwater ecotoxicity potential (FETP)',
                                               'human toxicity potential (HTPc)',
                                               'fossil fuel potential (FFP)',])




# find the data your interested in
min = 0
dataSelected = None
excludedUnits = ['Collector', 'RO', 'Prot. Digest.', 'Passing Unit' ]

for key, dataOutput in model_output._results_data.items():
    data = dataOutput._data
    flowSheet = dataOutput.return_chosen()
    outputsFlowSheet = analyzer.find_outputs_flowsheet(flowSheet, data)
    # Combine flowsheet names into a single key so you get unique keys
    outputKey = "_".join(outputsFlowSheet)

    if outputKey ==  'Compost_Pectin':
        if (data['IMPACT_TOT']['global warming potential (GWP100)'] > 3 and
           data['IMPACT_TOT']['global warming potential (GWP100)'] < 3.3):   #data['EBIT'] < min:
            dataSelected = data
            model_output_selected = dataOutput
        else:
            continue
    else:
        continue

if dataSelected is None:
    # print red
    print('\033[91m' +
          'No data for specified outputs found'
          + '\033[0m')
else:
    model_output_selected.get_results(path=savePath,
                             saveName='txt_results_selected')

    model_output.plot_impacts_per_unit(impact_category='global warming potential (GWP100)',
                                       data=dataSelected, path=savePath, saveName='contribution_analysis_Selected',
                                       exclude_units=excludedUnits, sources=['Electricity', 'Heat'])

    analyzer.create_flowsheet(path=savePath,
                              saveName='Figure_flowsheet_selected', dataScenario=dataSelected)

    analyzer.create_bar_plot_opex(path=savePath, modelData=dataSelected,
                                  saveName='bar_plot_opex_selected', barwidth=0.1)




