import sys
import os
import tracemalloc
import time
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import pickle

# start the timer
startTime = time.time()

# start the memory profiler
tracemalloc.start()
scrPath = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src'))
sys.path.insert(0, scrPath)

import outdoor
from outdoor import MultiModelOutput
from outdoor import AdvancedMultiModelAnalyzer

# file name that contains the results
fileName = 'model_selected.pkl'
currentDirectory = os.path.dirname(os.path.abspath(__file__))
saveLocation = os.path.join(currentDirectory, 'multiObj_aggregated')
pickleFilePath = os.path.join(saveLocation, fileName)

interestedCategories = ['global warming potential (GWP100)',
                        'terrestrial ecotoxicity potential (TETP)',
                        'freshwater ecotoxicity potential (FETP)',
                        'human toxicity potential (HTPnc)'
                        ]
excludeUints = ['Collector', 'Passing Unit']

# load the modelOutput
ModelOutput = MultiModelOutput.load_from_pickle(path=pickleFilePath)

# ModelOutput.get_results(path=saveLocation,
#                              saveName='txt_results_selected')

#
ModelOutput.sub_plots_stacked_impacts_per_category(impact_categories=interestedCategories, # data=dataSelected,
                                                        exclude_units=[], path=saveLocation,
                                                        saveName='contribution_analysis_stacked_units_selected',
                                                        bar_width=0.3, fontSizeLabs=16)  # sources=['Electricity', 'Heat', 'Waste'])

ModelOutput.sub_plots_stacked_impacts_per_category(impact_categories=interestedCategories,
                                                             exclude_units=[], path=saveLocation,
                                                             saveName='contribution_analysis_utilities_stacked_streams',
                                                             bar_width=0.3, stack_mode_units=False, fontSizeLabs=16)  # sources=['Electricity', 'Heat', 'Waste'])


#########  shortest distance to Pareto front:


# Points on the line
x1, y1 = -0.09, 90.92
x2, y2 = 0.833, -570.24

# Point of interest
x0, y0 = 1.989, -15.61

# Vector form of the line AB and point AP
A = np.array([x1, y1])
B = np.array([x2, y2])
P = np.array([x0, y0])

AB = B - A
AP = P - A

# Project AP onto AB
t = np.dot(AP, AB) / np.dot(AB, AB)

# Closest point on the infinite line
closest_point = A + t * AB

# Distance from P to the closest point
distance = np.linalg.norm(P - closest_point)

print(f"The closest point on the line: {closest_point}")
print(f"The shortest distance is: {distance:.4f}")


############################## per
rm = ModelOutput._data['RM_COST_TOT']/1000
capex = ModelOutput._data['CAPEX']
opex = ModelOutput._data['OPEX']

percentRMcosts = rm/(capex+opex)

print('The fraction raw material of total costs is:', percentRMcosts)
