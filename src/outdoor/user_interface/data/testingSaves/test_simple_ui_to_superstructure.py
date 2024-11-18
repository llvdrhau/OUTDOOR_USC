
# test suit for loading in a .outdr file from the outdoor package and running the optimization
# the optimization is run with the gurobi solver

# create a superstruture object

import pickle
import os


# get current directory
current_script_dir = os.path.dirname(os.path.abspath(__file__))
# path to the .outdr file
outdrUIFile = os.path.join(current_script_dir, 'simpleTest.outdr')
# open using pickle
with open(outdrUIFile, 'rb') as file:
    centralDataManager = pickle.load(file)


print('')
