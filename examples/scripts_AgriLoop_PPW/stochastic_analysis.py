'''
the script reads in the pickel file and analyzes the results of the stochastic optimization problem
'''

import sys
import os
import time
scrPath = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src'))
sys.path.insert(0, scrPath)
import outdoor


startTime = time.time()

# define file name that contains the results
n_scenarios = 100
fileName = "stochastic_mpi_sppy_{}sc.pkl".format(n_scenarios)
# define the name of the data to save
saveName = "flowsheet_{}sc".format(n_scenarios)


# define save locations of results and plots
current_script_dir = os.path.dirname(os.path.abspath(__file__))
results_dir = os.path.join(current_script_dir, 'results')
savePathPLots = results_dir


filePath = os.path.join(current_script_dir, 'saved_files') + '\\' + fileName
outputObject = outdoor.StochasticModelOutput_mpi_sppy.load_from_pickle(path=filePath)

# # Initialise the analyser object
analyzer = outdoor.BasicModelAnalyzer(outputObject)

# create the flow sheets of the superstructure and the optimized flow sheet
print('')
print("\033[95m Creating optimized flowsheet \033[00m")
analyzer.create_flowsheet(path=savePathPLots,
                          saveName=saveName)


endTime = time.time()

print("Time elapsed: ", endTime - startTime)
print('File saved at: ', savePathPLots)
print('File name: ', saveName)
