
# test suit for loading in a .outdr file from the outdoor package and running the optimization
# the optimization is run with the gurobi solver

# create a superstruture object

from outdoor import Superstructure
import pickle

# path to the .outdr file
outdrUIFile = r'C:\Users\Lucas\PycharmProjects\OUTDOOR_USC\examples\test_ui\simpleExample.outdr'
# open using pickle
with open(outdrUIFile, 'rb') as file:
    centralDataManager = pickle.load(file)


print('')
