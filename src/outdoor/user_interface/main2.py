import pickle

from PyQt5.QtWidgets import QTabWidget, QApplication, QMainWindow, QAction, QFileDialog

import sys

from data.CentralDataManager import CentralDataManager
from data.CentralDataManager import OutputManager
from data.superstructure_frame import SuperstructureFrame
from src.outdoor.outdoor_core.input_classes.superstructure import Superstructure

import os

from outdoor.user_interface.dialogs.ConfigEditor import ConfigEditor

# Get the current working directory
current_path = os.getcwd()
# Print the current working directory
print(f"Current working directory: {current_path}")


from outdoor.user_interface.WelcomeTab import WelcomeTab
from tabs.ComponentsTab import ComponentsTab
from tabs.GeneralSystemDataTab import GeneralSystemDataTab
from tabs.UtilityTab import UtilityTab
from tabs.SuperstructureMappingTab import SuperstructureMappingTab
from tabs.ReactionTab import ReactionsTab
from tabs.ProjectDescriptionTab import ProjectDescriptionTab
from src.outdoor.user_interface.utils.OutdoorLogger import outdoorLogger
import logging

class MainWindow(QMainWindow):  # Inherit from QMainWindow

    """
    This class creates the main window for the application and sets up the menu bar and tabbed interface.
    """

    def __init__(self):
        super().__init__()

        # add the logger
        self.logger = outdoorLogger(name='outdoor_logger', level=logging.DEBUG)

        self.setWindowTitle("OUTDOOR 2.0 - Open Source Process Simulator")
        self.setGeometry(100, 100, 1200, 800)
        self.ProjectName = ""
        self.ProjectPath = ""
        self.centralDataManager = CentralDataManager()  # Initialize the data manager
        self.outputManager = OutputManager() # Initialize the output manager

        menu_bar = self.menuBar()
        fileMenu = menu_bar.addMenu('File')

        # Creating actions for the 'File' menu
        openAction = QAction('Open', self)
        self.saveAction = QAction('Save', self)
        if self.ProjectName == '':
            self.saveAction.setDisabled(True)
        saveAsAction = QAction('Save As', self)

        # Adding actions to the 'File' menu
        fileMenu.addAction(openAction)
        fileMenu.addAction(self.saveAction)
        fileMenu.addAction(saveAsAction)

        # Connect actions to methods here (you'll implement these methods)
        openAction.triggered.connect(self.openFile)
        self.saveAction.triggered.connect(self.saveFile)
        saveAsAction.triggered.connect(self.saveAsFile)

        editMenu = menu_bar.addMenu('Edit')
        self.editAction = QAction('Configuration', self)
        if self.ProjectName == '':
            self.editAction.setDisabled(True)
        self.editAction.triggered.connect(self.editConfigs)
        editMenu.addAction(self.editAction)
        self.initTabs()

    def enableSave(self):
        self.saveAction.setEnabled(True)
        self.editAction.setEnabled(True)


    def openFile(self):
        #There has to be a way to handle "i cancelled the load" that's not this trash
        filepath = QFileDialog(self, caption='Open Saved Project', filter='*.outdr', directory='data/frames')
        filepath.exec()

        self.ProjectPath = filepath.selectedFiles()[0]
        self.ProjectName = self.ProjectPath.split('/')[-1].split('.')[0]
        with open(self.ProjectPath, 'rb') as file:
            self.centralDataManager = pickle.load(file)
        self.centralDataManager.data["PROJECT_NAME"] = self.ProjectName
        self.centralDataManager.loadConfigs()
        self.initTabs()
        self.enableSave()
        self.logger.info("Opened File: {}".format(self.ProjectPath))

        # comment for now to make bebugging easier
        # try:
        #     #if filepath.accept():
        #     self.ProjectPath = filepath.selectedFiles()[0]
        #     self.ProjectName = self.ProjectPath.split('/')[-1].split('.')[0]
        #     with open(self.ProjectPath, 'rb') as file:
        #         self.centralDataManager = pickle.load(file)
        #     self.centralDataManager.data["PROJECT_NAME"] = self.ProjectName
        #     self.centralDataManager.loadConfigs()
        #     self.initTabs()
        #     self.enableSave()
        #     self.logger.info("Opened File: {}".format(self.ProjectPath))
        # except Exception as e:
        #     self.logger.error("File opening cancelled: {}".format(e))

    def saveFile(self):
        """
        Save the current project to the file path specified in self.ProjectPath
        :return:
        """
        for unitDTO in self.centralDataManager.unitProcessData.values():
            unitDTO.exitPorts = []
            unitDTO.entryPorts = []

        with open(self.ProjectPath, 'wb') as file:
            pickle.dump(self.centralDataManager, file)
        print("Saved File: ", self.ProjectPath)
        self.centralDataManager.data["PROJECT_NAME"] = self.ProjectName

        # generate the superstructure frame
        #Frame = SuperstructureFrame()
        #Frame.constructSuperstructureFrame(self.centralDataManager)


    def saveAsFile(self):
        """
        Save the current project to a new file path
        :return:
        """
        try:
            self.ProjectPath = QFileDialog.getSaveFileName(self, 'Save As', filter='*.outdr', directory='data/frames')[
                0]
            self.ProjectName = self.ProjectPath.split('/')[-1].split('.')[0]

            # temporary fix for a bug during saving: can not pickle QT objects!!
            # I'm not using the DTO to acess the ports so this is relatively safe for now
            for unitDTO in self.centralDataManager.unitProcessData.values():
                unitDTO.exitPorts = []
                unitDTO.entryPorts = []

            with open(self.ProjectPath, 'wb') as file:
                pickle.dump(self.centralDataManager, file)
            self.setWindowTitle(self.ProjectName)
            self.enableSave()
            print("Saved File: ", self.ProjectPath)
            self.centralDataManager.data["PROJECT_NAME"] = self.ProjectName

        except Exception as e:
            self.logger.error("Save cancelled.", e)

    def editConfigs(self):
        dialog = ConfigEditor(self.centralDataManager)
        if dialog.exec_():
            print("Editing configs")
        else:
            print("Editing configs concluded.")
        self.initTabs()

    def initTabs(self):
        # Create a QTabWidget and set it as the central widget
        tabWidget = QTabWidget()
        self.setCentralWidget(tabWidget)

        # Create the tabs
        createWelcomeTab = WelcomeTab(centralDataManager=self.centralDataManager)
        projectDescriptionTab = ProjectDescriptionTab(centralDataManager=self.centralDataManager)
        generalSystemDataTab = GeneralSystemDataTab(centralDataManager=self.centralDataManager,
                                                    outputManager=self.outputManager)
        componentsTab = ComponentsTab(centralDataManager=self.centralDataManager)
        reactionsTab = ReactionsTab(centralDataManager=self.centralDataManager)
        utilityTab = UtilityTab(centralDataManager=self.centralDataManager)
        superstructureMappingTab = SuperstructureMappingTab(centralDataManager=self.centralDataManager,
                                                             outputManager=self.outputManager)

        # Add tabs to the QTabWidget
        tabWidget.addTab(createWelcomeTab, "Welcome")
        tabWidget.addTab(projectDescriptionTab, "Project Description")
        tabWidget.addTab(generalSystemDataTab, "General System Data")
        tabWidget.addTab(componentsTab, "Chemical Components")
        tabWidget.addTab(reactionsTab, "Reactions")
        tabWidget.addTab(utilityTab, "Utilities")
        tabWidget.addTab(superstructureMappingTab, "Superstructure Mapping")
        if self.ProjectName != '':
            self.setWindowTitle(f'OUTDOOR 2.0 - {self.ProjectName}')

    def _makeSuperstructureObject(self):
        """
        This methode makes the superstructure object used to run to OUTDOOR in the
        back end. The old funcitons used to wrapp the data from excel to the superstructure object should come here
        :return:
        """

        # make the inicial object:
        superstructureObject = Superstructure()

    def _setGeneralData(self):
        """
        Initiates the superstructure object and fills in general data

        :return: Superstructure Object
        """
        # model name
        modelName = self.centralDataManager.generalData['projectName']

        # retrieve the objective
        objectiveFull = self.centralDataManager.generalData['objective']
        objectiveMap = {'EBIT: Earnings Before Income Taxes': 'EBIT',
                        "NPC: Net Production Costs": "NPC",
                        "NPE: Net Produced CO2 Emissions": "NPE",
                        "FWD: Freshwater Demand": "FWD"}

        objective = objectiveMap[objectiveFull]

        productDriven = self.centralDataManager.generalData['productDriver']

        mainProduct = self.centralDataManager.generalData['mainProduct']
        if mainProduct == '':
            mainProduct = 'None'
        productLoad = self.centralDataManager.generalData['productLoad']

        if productLoad == '':
            productLoad = None

        optimizationMode = self.centralDataManager.generalData['optimizationMode']

        obj = Superstructure(ModelName=modelName,
                             Objective= objective,
                             productDriver=productDriven,
                             MainProduct=mainProduct,
                             ProductLoad= productLoad,
                             OptimizationMode=optimizationMode)

        opH = self.centralDataManager.generalData['operatingHours']
        obj.set_operatingHours(opH)

        obj.set_cecpi(self.centralDataManager.generalData['yearOfStudy'])

        obj.set_interestRate(self.centralDataManager.generalData['interestRate'])

        obj.set_linearizationDetail()

        obj.set_omFactor(0.04) # as default, nornally it is specified per unit process

        # Heat Pump values
        heatPumpSwitch = self.centralDataManager.generalData['heatPumpSwitch']
        if heatPumpSwitch == 'Yes':
            COP = self.centralDataManager.generalData['COP']
            Costs = self.centralDataManager.generalData['cost']
            Lifetime = self.centralDataManager.generalData['lifetime']

            T_IN = self.centralDataManager.generalData['TIN']
            T_OUT = self.centralDataManager.generalData['TOUT']
            if T_IN == '' or T_OUT == '':
                self.logger.error("Temperatures for the Heat Pump are not set.")
            obj.set_heatPump(Costs,
                             Lifetime,
                             COP,
                             T_IN,
                             T_OUT
                             )

        # ADD LISTS OF COMPONENTS, ETC.
        # ----------------------------
        liste = WF.read_list(df2, 0)
        obj.add_utilities(liste)

        liste = WF.read_list(df3, 0)
        obj.add_components(liste)

        liste = WF.read_list(df6, 0)
        obj.add_reactions(liste)

        liste = WF.read_list(df7, 0)
        obj.add_reactants(liste)

        dict1 = WF.read_type1(df3, 0, 1)
        obj.set_lhv(dict1)

        dict2 = WF.read_type1(df3, 0, 3)
        obj.set_mw(dict2)

        dict3 = WF.read_type1(df3, 0, 2)
        obj.set_cp(dict3)

        # ADD OTHER PARAMETERS
        # ---------------------

        dict1 = WF.read_type1(df2, 0, 2)
        obj.set_utilityEmissionsFactor(dict1)

        dict1 = WF.read_type1(df2, 0, 3)
        obj.set_utilityFreshWaterFator(dict1)

        liste = WF.read_type1(df3, 0, 4)
        obj.set_componentEmissionsFactor(liste)

        obj.set_deltaCool(df8.iloc[4, 1])

        liste1 = WF.read_list(df8, 0)
        liste2 = WF.read_list(df8, 1)
        # TODO: I think this dict shit here isn't used by anything. Please verify.
        dictTemperaturePrices = {'super': df8.iloc[0, 1],
                                 'high': df8.iloc[1, 1],
                                 'medium': df8.iloc[2, 1],
                                 'low': df8.iloc[3, 1]}

        obj.temperaturePricesDict = dictTemperaturePrices
        obj.set_heatUtilities(liste1, liste2)

        dict3 = WF.read_type1(df2, 0, 1)
        obj.set_deltaUt(dict3)

        return obj


def checkFocus():
    """
     for debugging purposes, check which widget currently has the focus.
    """
    currentFocusWidget = QApplication.instance().focusWidget()
    if currentFocusWidget:
        print(f"Current focus widget: {currentFocusWidget.objectName()}")
    else:
        print("No widget currently has the focus.")
        currentFocusWidget = []
    return currentFocusWidget


def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
