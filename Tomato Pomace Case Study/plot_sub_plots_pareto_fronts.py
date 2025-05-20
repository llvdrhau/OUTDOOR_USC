import copy
import pickle
import os
import outdoor
from outdoor.outdoor_core.input_classes.superstructure import Superstructure
from outdoor.outdoor_core.output_classes.analyzers.advanced_multi_analyzer import AdvancedMultiModelAnalyzer

# Load the data from the file pickle
# get current working directory
current_path = os.getcwd()
# add the relevant file name to the current working directory
path = os.path.join(current_path, "modelOutputList.pkl")
with open(path, 'rb') as file:
    modelOutputList = pickle.load(file)

analyzer = AdvancedMultiModelAnalyzer(modelOutputList[0])

xLabels = ['Global warming potential (kg_CO2_Eq/kg)',
           'Terrestrial ecotoxicity potential (kg 1,4-DCB-Eq/kg)',
           'Freshwater ecotoxicity potential (kg 1,4-DCB-Eq/kg)',
           'Human toxicity potential (kg 1,4-DCB-Eq/kg)']

save_path = os.path.join(current_path, "multiObj")
analyzer.sub_plot_pareto_fronts(modelOutputList, path=save_path,
                                saveName='pareto_fronts_sub_plot', xLabel=xLabels,
                                yLabel=['Earning Before Income Taxes (€/ton)',
                                        'Earning Before Income Taxes (€/ton)',
                                        'Earning Before Income Taxes (€/ton)',
                                        'Earning Before Income Taxes (€/ton)'],
                                flowTreshold=1e-5)

