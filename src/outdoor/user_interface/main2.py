
from PyQt5.QtWidgets import QTabWidget, QApplication, QMainWindow, QAction

import sys

from data.CentralDataManager import CentralDataManager

import os
# Get the current working directory
current_path = os.getcwd()
# Print the current working directory
print(f"Current working directory: {current_path}")


from outdoor.user_interface.WelcomeTab import WelcomeTab
from tabs.ComponentsTab import ComponentsTab
from tabs.GeneralSystemDataTab import GeneralSystemDataTab
from tabs.UtilityTab import UtilityTab
from tabs.SuperstructureMappingTab import SuperstructureMappingTab


class MainWindow(QMainWindow):  # Inherit from QMainWindow

    """
    This class creates the main window for the application and sets up the menu bar and tabbed interface.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OUTDOOR 2.0 - Open Source Process Simulator")
        self.setGeometry(100, 100, 800, 600)
        self.centralDataManager = CentralDataManager()  # Initialize the data manager
        self.initUI()

    def initUI(self):

        # Creating the menu bar
        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('File')

        # Creating actions for the 'File' menu
        openAction = QAction('Open', self)
        saveAction = QAction('Save', self)
        saveAsAction = QAction('Save As', self)

        # Adding actions to the 'File' menu
        fileMenu.addAction(openAction)
        fileMenu.addAction(saveAction)
        fileMenu.addAction(saveAsAction)

        # Connect actions to methods here (you'll implement these methods)
        openAction.triggered.connect(self.openFile)
        saveAction.triggered.connect(self.saveFile)
        saveAsAction.triggered.connect(self.saveAsFile)

        # Create a QTabWidget and set it as the central widget
        tabWidget = QTabWidget()
        self.setCentralWidget(tabWidget)

        # Create the tabs
        createWelcomeTab = WelcomeTab(centralDataManager=self.centralDataManager)
        componentsTab = ComponentsTab(centralDataManager=self.centralDataManager)

        generalSystemDataTab = GeneralSystemDataTab(centralDataManager=self.centralDataManager)
        utilityTab = UtilityTab(centralDataManager=self.centralDataManager)
        superstructureMappingTab = SuperstructureMappingTab(centralDataManager=self.centralDataManager)
        # todo add a tab, so users can type a description of the project

        # Add tabs to the QTabWidget
        tabWidget.addTab(createWelcomeTab, "Welcome")
        tabWidget.addTab(componentsTab, "Chemical Components")
        tabWidget.addTab(generalSystemDataTab, "General System Data")
        tabWidget.addTab(utilityTab, "Utilities")
        tabWidget.addTab(superstructureMappingTab, "Superstructure Mapping")

    # Placeholder methods for the file actions
    def openFile(self):
        print("Open File")

    def saveFile(self):
        print("Save File")

    def saveAsFile(self):
        print("Save As File")

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
