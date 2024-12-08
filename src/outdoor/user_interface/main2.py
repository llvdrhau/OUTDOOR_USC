import os
import pickle
import sys
import pandas as pd

import coloredlogs
from PyQt5.QtWidgets import QTabWidget, QApplication, QMainWindow, QAction, QFileDialog

from data.CentralDataManager import CentralDataManager
from data.CentralDataManager import OutputManager
from data.superstructure_frame import SuperstructureFrame
from data.ConstructSuperstructure import ConstructSuperstructure

from outdoor.user_interface.dialogs.ConfigEditor import ConfigEditor

from outdoor.user_interface.WelcomeTab import WelcomeTab
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

# Get the current working directory
current_path = os.getcwd()
# Print the current working directory
print(f"Current working directory: {current_path}")


class MainWindow(QMainWindow):  # Inherit from QMainWindow

    """
    This class creates the main window for the application and sets up the menu bar and tabbed interface.
    """

    def __init__(self):
        super().__init__()

        # add the logger
        self.logger = logging.getLogger()
        coloredlogs.install(logger=self.logger, level='DEBUG')

        self.setWindowTitle("OUTDOOR 2.0 - Open Source Process Simulator")
        self.setGeometry(100, 100, 1200, 800)
        self.ProjectName = ""
        self.ProjectPath = ""
        self.centralDataManager = CentralDataManager()  # Initialize the data manager
        self.outputManager = OutputManager()  # Initialize the output manager

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
        structureMenu.addAction(self.superStructureAction)

        self.initTabs()

    def enableSave(self):
        self.saveAction.setEnabled(True)
        self.editAction.setEnabled(True)

    def openFile(self):
        # There has to be a way to handle "i cancelled the load" that's not this trash
        filepath = QFileDialog(self, caption='Open Saved Project', filter='*.outdr', directory='data/frames')
        filepath.exec()

        self.ProjectPath = filepath.selectedFiles()[0]
        self.ProjectName = self.ProjectPath.split('/')[-1].split('.')[0]
        with open(self.ProjectPath, 'rb') as file:
            self.centralDataManager = pickle.load(file)
        self.centralDataManager.metadata["PROJECT_NAME"] = self.ProjectName
        self.centralDataManager.loadConfigs()
        self.initTabs()
        self.enableSave()
        self.logger.info("Opened File: {}".format(self.ProjectPath))

        # todo: set this in appropiate place (save methods), just for ease of use for now to test the superstructure
        # self._makeSuperstructureObject()

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
            print("Saved File: ", self.ProjectPath)
            self.centralDataManager.metadata["PROJECT_NAME"] = self.ProjectName

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
        uncertaintyTab = UncertaintyTab(centralDataManager=self.centralDataManager)

        # Add tabs to the QTabWidget
        tabWidget.addTab(createWelcomeTab, "Welcome")
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
