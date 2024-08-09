# ------------------------
# Central data manager
# ------------------------
# Central data manager for all data related to icons and associated dialogs
import csv
import glob
import pickle

#from .outdoor.user_interface.data.superstructure_frame import SuperstructureFrame
from data.superstructure_frame import SuperstructureFrame

class CentralDataManager:
    """
    A class to manage all data related to the icons and data from other tabs and their associated dialogs.
    This class stores the data
    """

    def __init__(self):
        self.data = {}  # Dictionary to store data indexed by icon ID #TODO Make this more structured
        self.namesChemicalComponents = []  # list to store chemical components data
        self.enabledTabs: list[str] = []
        self.enabledSuperstructureTabs: list[str] = []
        self.calculationTypes: dict[str, str] = {}
        self._loadConfigs()
        self.generalData = {}
        self.struct = SuperstructureFrame()

    def addData(self, field, data):
        self.data[field] = data
        match field:
            case "chemicalComponentsData":
                for species in data:
                    if species[0] not in self.namesChemicalComponents:
                        self.namesChemicalComponents.append(
                            species[0])  # Add the species name to the list of chemical components
            case "generalData":
                self.saveGeneral(data)

    def getChemicalComponentNames(self):
        return self.namesChemicalComponents

    def addComponentData(self, data):
        """
        Handels the data form the components tab (see class XXX todo give name of class)
        """
        self.data['componentData'] = data

    def updateIconData(self, iconId, newData):
        if iconId in self.data:
            self.data[iconId].update(newData)

    def getIconData(self, iconId):
        return self.data.get(iconId, None)

    def removeIconData(self, iconId):
        if iconId in self.data:
            del self.data[iconId]

    def addConnection(self, startPort, endPort, startPosition, endPosition, currentLine):
        #portType, startIconID, endIconID, starPosition, endPosition):
        # Add a connection between two icons

        startIconID = startPort.iconID,
        endIconID = endPort.iconID

        # check if data[startIconID]['connection'] exists, if not create it
        if startIconID not in self.data or 'connectionsTo' not in self.data[startIconID]:
            self.data.update({startIconID:
                                  {'connectionsTo': [],
                                   'entryPorts': [],
                                   'exitPorts': [],
                                   'connectionLines': []
                                   }
                              })

        # add the connection to the data dict
        self.data[startIconID]['connectionsTo'].append(endIconID)
        self.data[startIconID]['entryPorts'].append(endPort)
        self.data[startIconID]['exitPorts'].append(startPort)
        self.data[startIconID]['connectionLines'].append(currentLine)
        print(self.data)

        # self.data.update({startIconID:
        #                       {'connectionsTo': [],
        #                        'connectionLineEntry2Exit': {},
        #                        'connectionLineExit2Entry': {},
        #                        'positionEntryPortIcon': None,
        #                        'positionExitPortIcon': None
        #                        }
        #                   })

        # if endIconID not in self.data or 'connectionsTo' not in self.data[startIconID]:
        #     self.data.update({endIconID:
        #                           {'connectionsTo': [],
        #                            'connectionLineEntry2Exit': {}, # what is leaving the entry port and entering the exit port
        #                            'connectionLineExit2Entry': {}, # what is leaving the exit port and entering the entry port
        #                            'positionEntryPortIcon': None,
        #                            'positionExitPortIcon': None
        #                            }
        #                       })
        #
        # # info you can fill in of the icon where lines are leaving that is from startIconID
        # # +-------+                    line                    +--------+
        # # | icon' | (startPos) EXIT ----------> (endPos) Entry | icon'' |
        # # +-------+                                            +--------+
        # #self.data[startIconID]['connectionsTo'].append(endIconID)
        # self.data[startIconID]['connectionLineExit2Entry'].update({endIconID: (startPosition, endPosition, currentLine)})
        # self.data[startIconID]['positionExitPortIcon'] = startPosition
        #
        # # info you can fill in of the icon where lines are leaving that is from startIconID
        # # +-------+                     line                   +--------+
        # # | icon' | (startPos) EXIT <---------- (endPos) Entry | icon'' |
        # # +-------+                                            +--------+
        # self.data[endIconID]['connectionLineEntry2Exit'].update({startIconID: (startPosition, endPosition, currentLine)})
        # self.data[endIconID]['positionEntryPortIcon'] = endPosition

    def updateConnectionDictPositions(self, portMethode, line):
        # Update the position of the connected ports when Icons are moved around on the canvas

        # {'connectionsTo': [],
        #  'connectionLineEntry2Exit': {},  # what is leaving the entry port and entering the exit port
        #  'connectionLineExit2Entry': {},  # what is leaving the exit port and entering the entry port
        #  'positionEntryPortIcon': None,
        #  'positionExitPortIcon': None

        iconID = portMethode.iconID
        portType = portMethode.portType
        if portType == 'exit':
            self.data[iconID]['connectionLineExit2Entry'].update(
                {'endIconID': (line.line().p1(), line.line().p2,
                               line)})  # todo I need to find a way to pass on endIconID... place holder for now
            self.data[iconID]['positionExitPortIcon'] = line.line().p1()
        else:
            self.data[iconID]['connectionLineEntry2Exit'].update(
                {'endIconID': (
                    line.line().p1(), line.line().p2, line)})  # todo I need to find a way to pass on endIconID...
            self.data[iconID]['positionExitPortIcon'] = line.line().p1()

        print(self.data[iconID]['connectionLineExit2Entry'])

    def _loadConfigs(self):
        with open('data/configs.csv') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for row in reader:
                self.calculationTypes[row[0]] = row[1]

    def calc_configs(self) -> dict[str, str]:
        return self.calculationTypes

    def updateConfigs(self, update: dict[str, str]):
        self.calculationTypes = update
        with open('data/configs.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            for key, value in self.calculationTypes.items():
                writer.writerow([key, value])

    def dataDump(self):
        print(self.data)

    def saveAll(self):
        self.struct.save_frame()

    def saveGeneral(self, gendata):
        self.struct.ModelName = gendata["projectName"]
        self.struct.Objective = gendata["objective"]
        self.struct.MainProduct = gendata["mainProduct"]
        self.struct.ProductLoad = gendata["productLoad"]
        self.struct.productDriver = gendata["productDriver"]
        self.struct.OptimizationMode = gendata["optimizationMode"]

    def reloadProject(self, project_name):
        target = project_name
        with open(target, 'rb') as file:
            self.struct = pickle.load(file)

        print(self.struct)
