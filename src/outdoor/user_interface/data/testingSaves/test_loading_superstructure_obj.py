import pickle
import outdoor
from outdoor.outdoor_core.input_classes.superstructure import Superstructure
# Load the data from the file
path = r'C:\Users\Lucas\PycharmProjects\OUTDOOR_USC\src\outdoor\user_interface\data\testingSaves\test2_superstructure.pkl'
with open(path, 'rb') as file:
    data = pickle.load(file)

# Print the data
print(data.__dict__)
