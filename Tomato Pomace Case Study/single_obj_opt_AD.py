import pickle
import os
import outdoor
from outdoor.outdoor_core.input_classes.superstructure import Superstructure
# Load the data from the file
# get current working directory
current_path = os.getcwd()
# add the file name Aurelie_peptide_production_superstructure.pkl to the current working directory
path = os.path.join(current_path, "TP_case_study_force_AD_superstructure.pkl") # TP_case_study_superstructure  or tp_test_superstructure
with open(path, 'rb') as file:
    superstructureObj = pickle.load(file)

savePath = os.path.join(current_path, "singleOpt_AD")
outdoor.create_superstructure_flowsheet(superstructure=superstructureObj,
                                        path=savePath,
                                        saveName='Figure_superstructure')

# solve the optimization problem
abstract_model = outdoor.SuperstructureProblem(parser_type='Superstructure')
solverOptions = {"IntFeasTol": 1e-8,  # tolerance for integer feasibility
                 "NumericFocus": 0,
                 }   # 0: balanced, 1: feasibility, 2: optimality, 3: feasibility and optimality

model_output = abstract_model.solve_optimization_problem(input_data=superstructureObj,
                                                         optimization_mode='single',
                                                         solver='gurobi',
                                                         interface='local',
                                                         calculation_VSS=False,
                                                         calculation_EVPI=False,
                                                         options=solverOptions,)

# save the results as a txt file, you have to specify the path
model_output.get_results(path=savePath,
                         saveName='txt_results_AD')
# save and analyze the new results
analyzer = outdoor.BasicModelAnalyzer(model_output)
# create the flow sheets of the superstructure and the optimized flow sheet
analyzer.create_flowsheet(path=savePath,
                          saveName='Figure_flowsheet_AD')

analyzer.create_bar_plot_opex(path=savePath, barwidth=0.1, saveName='opex_AD')
#
DF_LCA, _ = model_output.get_detailed_LCA_results()
print(DF_LCA)

# # analyzer.LCA_analysis_plot('global warming potential (GWP100)', saveName='LCA_test', log_scale=True)
# model_output.plot_impacts_per_unit(impact_category='global warming potential (GWP100)',
#                                    exclude_units=['Collector', 'Passing Unit'], path=savePath,
#                                    saveName='contribution_analysis_AD', barWidth=0.3, sources=['Electricity', 'Heat'])

interestedCategories = ['global warming potential (GWP100)',
                        'terrestrial ecotoxicity potential (TETP)',
                        'freshwater ecotoxicity potential (FETP)',
                        'human toxicity potential (HTPnc)'
                        ]

model_output.sub_plots_stacked_impacts_per_category(impact_categories=interestedCategories,
                                               exclude_units=['Collector', 'Passing Unit'], path=savePath,
                                               saveName='contribution_analysis_AD_stacked_units', bar_width=0.3,
                                                    fontSizeLabs=16) #sources=['Electricity', 'Heat', 'Waste'])


model_output.plot_stacked_impacts_per_category(impact_categories=interestedCategories,
                                                exclude_units=['Collector', 'Passing Unit'], path=savePath,
                                                saveName='contribution_analysis_AD_stacked_streams', bar_width=0.3,
                                               stack_mode_units=False) #sources=['Electricity', 'Heat', 'Waste'])


# print('')
# model_output.heat_balance_analysis()

# possible keys ['waste_impact_fac', 'impact_inFlow_components', 'util_impact_factors']
# impactFacDict = model_output.get_impact_factors()
# for key in impactFacDict.keys():
#     print('----------', key)
#     print(impactFacDict[key])
#     print('')
#
# model_output.find_negative_impacts()

#model_output.model_instance.HeatBalance_3.pprint()
