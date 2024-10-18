import pickle

from PyQt5.QtWidgets import QTabWidget, QApplication, QMainWindow, QAction, QFileDialog

import sys

from data.CentralDataManager import CentralDataManager

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


class MainWindow(QMainWindow):  # Inherit from QMainWindow

    """
    This class creates the main window for the application and sets up the menu bar and tabbed interface.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("OUTDOOR 2.0 - Open Source Process Simulator")
        self.setGeometry(100, 100, 1200, 800)
        self.ProjectName = ""
        self.ProjectPath = ""
        self.centralDataManager = CentralDataManager()  # Initialize the data manager
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
        try:
            #if filepath.accept():
            self.ProjectPath = filepath.selectedFiles()[0]
            self.ProjectName = self.ProjectPath.split('/')[-1].split('.')[0]
            with open(self.ProjectPath, 'rb') as file:
                self.centralDataManager = pickle.load(file)
            self.centralDataManager.data["PROJECT_NAME"] = self.ProjectName
            self.centralDataManager.loadConfigs()
            self.initTabs()
            self.enableSave()
            print("Opened File: ", self.ProjectPath)
        except Exception as e:
            print("File opening likely cancelled: ", e)

    def saveFile(self):
        with open(self.ProjectPath, 'wb') as file:
            pickle.dump(self.centralDataManager, file)
        print("Saved File: ", self.ProjectPath)
        self.centralDataManager.data["PROJECT_NAME"] = self.ProjectName

    def saveAsFile(self):
        try:
            self.ProjectPath = QFileDialog.getSaveFileName(self, 'Save As', filter='*.outdr', directory='data/frames')[
                0]
            self.ProjectName = self.ProjectPath.split('/')[-1].split('.')[0]
            with open(self.ProjectPath, 'wb') as file:
                pickle.dump(self.centralDataManager, file)
            self.setWindowTitle(self.ProjectName)
            self.enableSave()
            print("Saved File: ", self.ProjectPath)
            self.centralDataManager.data["PROJECT_NAME"] = self.ProjectName
        except Exception as e:
            print("Save cancelled.", e)

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
        componentsTab = ComponentsTab(centralDataManager=self.centralDataManager)
        generalSystemDataTab = GeneralSystemDataTab(centralDataManager=self.centralDataManager)
        utilityTab = UtilityTab(centralDataManager=self.centralDataManager)
        superstructureMappingTab = SuperstructureMappingTab(centralDataManager=self.centralDataManager)
        reactionsTab = ReactionsTab(centralDataManager=self.centralDataManager)

        # todo add a tab, so users can type a description of the project

        # Add tabs to the QTabWidget
        tabWidget.addTab(createWelcomeTab, "Welcome")
        tabWidget.addTab(generalSystemDataTab, "General System Data")
        tabWidget.addTab(componentsTab, "Chemical Components")
        tabWidget.addTab(reactionsTab, "Reactions")
        tabWidget.addTab(utilityTab, "Utilities")
        tabWidget.addTab(superstructureMappingTab, "Superstructure Mapping")
        if self.ProjectName != '':
            self.setWindowTitle(f'OUTDOOR 2.0 - {self.ProjectName}')


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
