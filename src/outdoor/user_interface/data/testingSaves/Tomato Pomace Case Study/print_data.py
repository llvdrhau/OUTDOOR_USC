import pickle
import os
import outdoor
from outdoor.outdoor_core.input_classes.superstructure import Superstructure
from outdoor.user_interface.data.CreateTabelsOfData import LatTexTableCreator

# Load the data from the file
# get current working directory
current_path = os.getcwd()
# add the file name Aurelie_peptide_production_superstructure.pkl to the current working directory
path = os.path.join(current_path, "TP_case_study_superstructure.pkl") # TP_case_study_superstructure  or tp_test_superstructure
with open(path, 'rb') as file:
    superstructureObj = pickle.load(file)

tabelGenerator = LatTexTableCreator(superstructureObj)
tabelGenerator.create_table()
print('DONE')
