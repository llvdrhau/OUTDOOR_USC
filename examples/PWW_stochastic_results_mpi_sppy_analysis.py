'''
the script reads in the json file and analyzes the results of the stochastic optimization problem
'''

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
import outdoor

# read in the json file

filePath = r"C:\Users\Lucas\PycharmProjects\OUTDOOR_USC\examples\results\potato_peel_case_study_mpi-sppy\model_output_test.json"
resultsPath = r"C:\Users\Lucas\PycharmProjects\OUTDOOR_USC\examples\results\potato_peel_case_study_mpi-sppy"

outputObject = outdoor.StochasticModelOutput_mpi_sppy()
outputObject.load_from_json(savedLocation=filePath)

print(outputObject.dataFile)

# todo check the flow distribution of the results do they match previous optimisation?
