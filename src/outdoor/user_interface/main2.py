import argparse
import os
import pickle
import sys
import pandas as pd

import coloredlogs
from PyQt5.QtWidgets import QTabWidget, QApplication, QMainWindow, QAction, QFileDialog
from pyparsing import empty

from data.CentralDataManager import CentralDataManager
from data.SignalManager import SignalManager
from data.superstructure_frame import SuperstructureFrame
from data.ConstructSuperstructure import ConstructSuperstructure
from data.TabManager import TabManager

from outdoor.user_interface.dialogs.ConfigEditor import ConfigEditor

from outdoor.user_interface.WelcomeTab import WelcomeTab
from outdoor.user_interface.utils.LCACalculationMachine import LCACalculationMachine
from tabs.ComponentsTab import ComponentsTab
from tabs.GeneralSystemDataTab import GeneralSystemDataTab
from tabs.UtilityTab import UtilityTab
from tabs.SuperstructureMappingTab import SuperstructureMappingTab
from tabs.ReactionTab import ReactionsTab
from tabs.ProjectDescriptionTab import ProjectDescriptionTab
from tabs.UncertaintyTab import UncertaintyTab
from src.outdoor.user_interface.utils.OutdoorLogger import outdoorLogger
from outdoor.user_interface.data.ProcessDTO import ProcessType

import logging

class MainWindow(QMainWindow):  # Inherit from QMainWindow

    """
    This class creates the main window for the application and sets up the menu bar and tabbed interface.
    """

    def __init__(self, **kwargs):
        super().__init__()
        # add the logger
        self.logger = logging.getLogger()
        coloredlogs.install(logger=self.logger, level=kwargs['level'],isatty=True)
        logging.getLogger('peewee').setLevel(logging.ERROR)  # This is to make brightway shut up
        logging.getLogger("bw2calc").setLevel(logging.ERROR)  # This is to make brightway shut up
        logging.getLogger("fsspec").setLevel(logging.ERROR)
        self.setWindowTitle("OUTDOOR 2.0 - Open Source Process Simulator")
        self.setGeometry(100, 100, 1200, 800)
        self.ProjectName = ""
        self.ProjectPath = ""
        self.centralDataManager = CentralDataManager()  # Initialize the data manager
        self.signalManager = SignalManager(self.centralDataManager)  # Initialize the output manager
        self.tabManager = TabManager()  # Initialize the tab manager

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

        structureMenu = menu_bar.addMenu('Superstructure')
        self.superStructureAction = QAction('Generate Superstructure', self)
        self.superStructureAction.triggered.connect(self.generateSuperstructureObject)
        self.calcLCAAction = QAction('Calculate all LCAs', self)
        self.calcLCAAction.triggered.connect(self.calculateAllLCAs)
        structureMenu.addAction(self.superStructureAction)
        structureMenu.addAction(self.calcLCAAction)

        self.initTabs()

    def enableSave(self):
        self.saveAction.setEnabled(True)
        self.editAction.setEnabled(True)

    def openFile(self):
        # There has to be a way to handle "i cancelled the load" that's not this trash
        try:
            filepath = QFileDialog(self, caption='Open Saved Project', filter='*.outdr', directory='data/frames')
            filepath.exec()

            self.ProjectPath = filepath.selectedFiles()[0]
            self.ProjectName = self.ProjectPath.split('/')[-1].split('.')[0]
            with open(self.ProjectPath, 'rb') as file:
                self.centralDataManager = pickle.load(file)
            self.centralDataManager.metadata["PROJECT_NAME"] = self.ProjectName
            self.centralDataManager.loadConfigs()
            self.signalManager = SignalManager(self.centralDataManager)  # Initialize the new output manager
            # check if there are missing attributes in the centralDataManager
            self.checkMissingAttributes()

            self.initTabs()
            self.enableSave()
            self.logger.debug("Opened File: {}".format(self.ProjectPath))
        except Exception as e:
            #Guess the load got cancelled. This has never failed in the past so if it fails now undo whatever you did.
            pass

    def checkMissingAttributes(self):
        """
        During development some new attributes were added to the DTOs, this method checks if the attributes are missing
        and adds them with default values if they are missing
        :return:
        """
        if not hasattr(self.centralDataManager, 'uncertaintyData'):
            self.centralDataManager.uncertaintyData = []
        # had a problem with the material flow in the DTO, this is a temporary fix

        # having a problem with the LCA objects missing a dictionary with key 'exchanges'
        # this is a temporary fix
        data_lists = [
            self.centralDataManager.componentData,
            self.centralDataManager.utilityData,
            self.centralDataManager.wasteData,
            self.centralDataManager.temperatureData
        ]

        ## TOTAL LCA RESET
        for data_list in data_lists:
            for dto in data_list:
                if not hasattr(dto, 'LCA') or not dto.LCA:
                    dto.LCA = {'Results': {}, 'exchanges': {}}
                    dto.calculated = False
                if not hasattr(dto, 'emptyCategories'):
                    dto.emptyCategories = {
                        'terrestrial acidification potential (TAP)': 0,
                        'global warming potential (GWP100)': 0,
                        'freshwater ecotoxicity potential (FETP)': 0,
                        'marine ecotoxicity potential (METP)': 0,
                        'terrestrial ecotoxicity potential (TETP)': 0,
                        'fossil fuel potential (FFP)': 0,
                        'freshwater eutrophication potential (FEP)': 0,
                        'marine eutrophication potential (MEP)': 0,
                        'human toxicity potential (HTPc)': 0,
                        'human toxicity potential (HTPnc)': 0,
                        'ionising radiation potential (IRP)': 0,
                        'agricultural land occupation (LOP)': 0,
                        'surplus ore potential (SOP)': 0,
                        'ozone depletion potential (ODPinfinite)': 0,
                        'particulate matter formation potential (PMFP)': 0,
                        'photochemical oxidant formation potential: humans (HOFP)': 0,
                        'photochemical oxidant formation potential: ecosystems (EOFP)': 0,
                        'water consumption potential (WCP)': 0,
                        'ecosystem quality': 0,
                        'human health': 0,
                        'natural resources': 0
                    }

        # data_lists = [
        #     self.centralDataManager.utilityData,
        #     self.centralDataManager.wasteData,
        # ]
        #
        # for data_list in data_lists:
        #     for dto in data_list:
        #         dto.LCA = {'Results': {}, 'exchanges': {}}
        #         dto.calculated = False


        # # the reason was that outgoing flows were not updated when output units are removed, fixed now
        # if 'c44290e5-10f9-4697-a7f1-79865df8be27' in self.centralDataManager.unitProcessData:
        #     dto2Change = self.centralDataManager.unitProcessData['c44290e5-10f9-4697-a7f1-79865df8be27']
        #     materialFlow = dto2Change.materialFlow
        #     # remove the follwing key from the dictionary: 'e872ef91-2244-4a91-8f35-92b41b3f2735'
        #     for dictStream in materialFlow.values():
        #         if 'e872ef91-2244-4a91-8f35-92b41b3f2735' in dictStream:
        #             dictStream.pop('e872ef91-2244-4a91-8f35-92b41b3f2735')
        #         elif '1d2e7a23-ebd4-43fd-891c-d8f66ffd0249' in dictStream:
        #             dictStream.pop('1d2e7a23-ebd4-43fd-891c-d8f66ffd0249')
        #     self.centralDataManager.unitProcessData['c44290e5-10f9-4697-a7f1-79865df8be27'] = dto2Change

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
        self.logger.info("Saved File: {}".format(self.ProjectPath))
        self.centralDataManager.metadata["PROJECT_NAME"] = self.ProjectName

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
            self.logger.debug("Saved File: ", self.ProjectPath)
            self.centralDataManager.metadata["PROJECT_NAME"] = self.ProjectName

        except Exception as e:
            self.logger.error("Save cancelled.", e)

    def editConfigs(self):
        dialog = ConfigEditor(self.centralDataManager)
        if dialog.exec_():
            pass
        else:
            pass
        self.update()

    def initTabs(self, index=None):
        # Create a QTabWidget and set it as the central widget
        tabWidget = QTabWidget()
        self.setCentralWidget(tabWidget)

        # Create the tabs
        welcomeTab = WelcomeTab(centralDataManager=self.centralDataManager)
        projectDescriptionTab = ProjectDescriptionTab(centralDataManager=self.centralDataManager)
        generalSystemDataTab = GeneralSystemDataTab(centralDataManager=self.centralDataManager,
                                                    signalManager=self.signalManager)
        componentsTab = ComponentsTab(centralDataManager=self.centralDataManager, tabManager=self.tabManager)
        reactionsTab = ReactionsTab(centralDataManager=self.centralDataManager)
        utilityTab = UtilityTab(centralDataManager=self.centralDataManager)
        superstructureMappingTab = SuperstructureMappingTab(centralDataManager=self.centralDataManager,
                                                            signalManager=self.signalManager)
        uncertaintyTab = UncertaintyTab(centralDataManager=self.centralDataManager)

        # Add tabs to the QTabWidget
        tabWidget.addTab(welcomeTab, "Welcome")
        tabWidget.addTab(projectDescriptionTab, "Project Description")
        tabWidget.addTab(generalSystemDataTab, "General System Data")
        tabWidget.addTab(componentsTab, "Chemical Components")
        tabWidget.addTab(reactionsTab, "Reactions")
        tabWidget.addTab(utilityTab, "Utilities")
        tabWidget.addTab(superstructureMappingTab, "Superstructure Mapping")
        tabWidget.addTab(uncertaintyTab, "Uncertainty")
        if self.ProjectName != '':
            self.setWindowTitle(f'OUTDOOR 2.0 - {self.ProjectName}')

    def generateSuperstructureObject(self):
        """
        Generate the superstructure object from the data in the centralDataManager
        :return:
        """

        # before generating the superstructure object,save the project if the save path is established!
        if self.ProjectPath != '':
            self.saveFile()

        constructorSuperstructure = ConstructSuperstructure(self.centralDataManager)
        if constructorSuperstructure.warningMessage:
            self.logger.error(constructorSuperstructure.warningMessage)
            return # if there is a warning, do not proceed with the superstructure generation

        superstructure = constructorSuperstructure.get_superstructure()

        # save the object in the same location as the project file
        # with the name of the project file + '_superstructure'
        superstructurePath = self.ProjectPath.split('.')[0] + '_superstructure.pkl'
        with open(superstructurePath, 'wb') as file:
            pickle.dump(superstructure, file)

        self.logger.info("Superstructure Object Saved in: {}".format(superstructurePath))

    def calculateAllLCAs(self):
        """
        Instead of manually calculating LCAs as you model them, this does it all at once.
        :return:
        """
        calculator = LCACalculationMachine(self.centralDataManager)
        calculator.calculateAllLCAs(True)

        self.update()

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


def main(**kwargs):
    app = QApplication(sys.argv)
    main_window = MainWindow(**kwargs)
    main_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--level", type=str, help="log level", default="DEBUG")
    args = parser.parse_args()

    kwargs = vars(args)
    main(**kwargs)
