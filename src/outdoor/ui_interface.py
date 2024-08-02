import pandas
from outdoor_core.input_classes.superstructure import Superstructure
## Step one, create a Superstructure object based on wrapp_SystemData

"""
Superstructure object has the following sections:
- GeneralData
- Utilitylist 
- Componentlist
- TemperatureIntervals
- ReactionsList
- ReactantsList
- TemperaturePrice

Right now these are selected by effectively highlighting ranges within an excel sheet
and copying them into dataframes. We're gonna try to find a way to make objects that
represent these that can be converted to dataframes that meet the final output format.

"""

class UiInterface:
    def __init__(self) -> None:
        self.current_structure = None

    def loadSavedStructure(self, structure: str):
        #set self.current_structure to an imported struct object
        pass

    def generateSuperstructure():
        #take input data and make a superstructure object
        pass

    def saveSuperstructure():
        #serialize superstructure object and write to file.
        pass