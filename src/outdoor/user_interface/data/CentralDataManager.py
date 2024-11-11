# ------------------------
# Central data manager
# ------------------------
# Central data manager for all data related to icons and associated dialogs
import csv
import glob
import os.path
import pickle

from PyQt5.QtCore import QObject, pyqtSignal  # needed to emmit signals

from outdoor.user_interface.data.ComponentDTO import ComponentDTO
from outdoor.user_interface.data.ProcessDTO import ProcessDTO
from outdoor.user_interface.data.ReactionDTO import ReactionDTO
from outdoor.user_interface.data.UtilityDTO import UtilityDTO
from outdoor.user_interface.data.superstructure_frame import SuperstructureFrame


class CentralDataManager:
    """
    A class to manage all data related to the icons and data from other tabs and their associated dialogs.
    This class stores the data
    """

    def __init__(self):
        super().__init__()

        self.projectDescription = ""

        self.unitProcessData: dict[str, ProcessDTO] = {}  # Dictionary to store data indexed by icon ID

        self.namesChemicalComponents = []  # list to store chemical components data
        self.enabledTabs: list[str] = []
        self.enabledSuperstructureTabs: list[str] = []
        self.configs = {}
        self.loadConfigs()
        self.generalData = {}
        self.utilityData = UtilityDTO()
        self.componentData: list[ComponentDTO] = []
        self.reactionData: list[ReactionDTO] = []
        self.struct = SuperstructureFrame()
        self._outputList: list[str] = []

        self.metadata = {}  # Stores project metadata like the name. TODO move configs into this

    def addData(self, field, data):
        """
        Adds data to the central data manager
        :param field: str, the field that the data belongs to
        :param data: the data to be added gererally a DTO
        :return:
        """
        match field:
            case "chemicalComponentsData":
                for species in data:
                    if species[0] not in self.namesChemicalComponents:
                        # Add the species name to the list of chemical components
                        self.namesChemicalComponents.append(species[0])

            case "generalData":
                self.saveGeneral(data)

            case "reactionData":
                self.reactionData.append(data)

            case _:
                # print in red
                print("\033[91m" + "Error: Field not recognized" + "\033[0m")
                print("\033[91m" + "Adding data to the Central data manager for field: {}".format(field) + "\033[0m")

    def getChemicalComponentNames(self):
        return self.namesChemicalComponents

    def addReactionData(self, data):
        """
        Adds Reactions to the ReactionsData
        :param data:
        :return:
        """
        self.componentData.append(data)

    def updateData(self, dataType: str, row: int):
        """
        Updates the specified data lists when a reaction, chemical component... is deleted

        :param dataType: str, the type of data that is to be altered
        :param row: int, this is the row i.e., the indices in the list that corresponds to the element that is to be
        deleted
        :return: updated data component
        """

        match dataType:
            case "reactionData":
                # delete the row with the data for that reaction
                self.reactionData.pop(row)
                sizeReactionList = len(self.reactionData)

                if row != sizeReactionList:  # if it's the last element in the list don't adjust the indices
                    for i in range(row, sizeReactionList):
                        data = self.reactionData[i]
                        data.upadateField("rowPosition", i)

            case "componentData":
                # delete the row with the data for that component
                self.componentData.pop(row)
                sizeComponentList = len(self.componentData)

                if row != sizeComponentList:  # if it's the last element in the list don't adjust the indices
                    for i in range(row, sizeComponentList):
                        data = self.componentData[i]
                        data.updateRow()

    def updateIconData(self, iconId, newData):
        if iconId in self.unitProcessData:
            self.unitProcessData[iconId].update(newData)

    def getIconData(self, iconId):
        return self.unitProcessData.get(iconId, None)

    def removeIconData(self, iconId):
        if iconId in self.unitProcessData:
            del self.unitProcessData[iconId]

    def loadConfigs(self):
        print("Loading configs...")
        self.configs["calcConfigs"] = {}
        self.configs["componentConfigs"] = {}
        try:
            if not os.path.isdir(f'data/configs/{self.metadata["PROJECT_NAME"]}/'):
                raise Exception("Project folder doesn't exist.")
            for file in glob.glob(f'data/configs/{self.metadata["PROJECT_NAME"]}/*.csv'):
                with open(file) as csvfile:
                    reader = csv.reader(csvfile, delimiter=',')
                    if file.split('\\')[-1].split('.')[0] == 'calcConfigs':
                        calcconfs = {}
                        for row in reader:
                            calcconfs[row[0]] = row[1]
                        self.configs['calcConfigs'] = calcconfs
                    if file.split('\\')[-1].split('.')[0] == 'componentConfigs':
                        compconfs = {}
                        for row in reader:
                            compconfs[row[0]] = row[1]
                        self.configs['componentConfigs'] = compconfs
        except Exception as e:
            print("Error reloading configs file, initializing with defaults.")
            self._loadDefaults()

    def _loadDefaults(self):
        for file in glob.glob(f'data/configs/defaults/*.csv'):
            with open(file) as csvfile:
                reader = csv.reader(csvfile, delimiter=',')
                if file.split('\\')[-1].split('.')[0] == 'calcConfigs':
                    calcconfs = {}
                    for row in reader:
                        calcconfs[row[0]] = row[1]
                    self.configs['calcConfigs'] = calcconfs
                if file.split('\\')[-1].split('.')[0] == 'componentConfigs':
                    compconfs = {}
                    for row in reader:
                        compconfs[row[0]] = row[1]
                    self.configs['componentConfigs'] = compconfs

    def updateConfigs(self, update: dict[str, dict]):
        self.configs = update
        if not os.path.isdir(f'data/configs/{self.metadata["PROJECT_NAME"]}/'):
            os.mkdir(f'data/configs/{self.metadata["PROJECT_NAME"]}/')
        for name, dic in update.items():
            filename = f'data/configs/{self.metadata["PROJECT_NAME"]}/{name}.csv'
            with open(filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile, delimiter=',')
                for key, value in dic.items():
                    writer.writerow([key, value])

    def dataDump(self):
        print(self.metadata)

    def saveAll(self):
        self.struct.save_frame()

    def saveGeneral(self, gendata):
        self.struct.ModelName = gendata["projectName"]
        self.struct.Objective = gendata["objective"].split(":")[0]
        self.struct.MainProduct = gendata["mainProduct"]
        self.struct.ProductLoad = gendata["productLoad"]
        self.struct.productDriver = gendata["productDriver"].lower()
        self.struct.OptimizationMode = gendata["optimizationMode"].lower()

    def reloadProject(self, project_name):
        target = project_name
        with open(target, 'rb') as file:
            self.struct = pickle.load(file)

        print(self.struct)


class OutputManager(QObject):
    # Signal that is emitted when outputList changes
    outputListUpdated = pyqtSignal()

    def __init__(self):
        super().__init__()

        self._outputList: list[str] = []

    @property
    def outputList(self):
        return self._outputList

    @outputList.setter
    def outputList(self, new_list):
        self._outputList = new_list
        # Emit the signal to indicate that the list has been updated
        self.outputListUpdated.emit()
