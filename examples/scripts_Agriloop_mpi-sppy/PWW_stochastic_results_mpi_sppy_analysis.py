'''
the script reads in the pickel file and analyzes the results of the stochastic optimization problem
'''

import sys
import os
import time
scrPath = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src'))
sys.path.insert(0, scrPath)
import outdoor

n_scenarios = 11

startTime = time.time()

# define file name that contains the results
fileName = "stochastic_mpi_sppy_{}sc.pkl".format(n_scenarios)
# define the name of the data to save
saveName = "flowsheet_{}sc".format('test11')


# define save locations
current_script_dir = os.path.dirname(os.path.abspath(__file__))
results_dir = os.path.join(current_script_dir, 'results')
filePath = os.path.join(current_script_dir, 'saveFiles') + '\\' + fileName
savePathPLots = results_dir


outputObject = outdoor.StochasticModelOutput_mpi_sppy.load_from_pickle(path=filePath)

# outputObject.load_from_pickle(path=filePath)

# # Initialise the analyser object
analyzer = outdoor.BasicModelAnalyzer(outputObject)
# create the flow sheets of the superstructure and the optimized flow sheet
analyzer.create_flowsheet(path=savePathPLots,
                          saveName=saveName)

endTime = time.time()

print("Time elapsed: ", endTime - startTime)
