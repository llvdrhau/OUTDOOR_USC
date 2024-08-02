
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QWidget, QTabWidget, QApplication, QMainWindow, QHBoxLayout, QGroupBox, QAction
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap, QFontDatabase

import sys

from data import CentralDataManager
from tabs.ComponentsTab import ComponentsTab
from tabs.DraggableIcon import DraggableIcon
from tabs.GeneralSystemDataTab import GeneralSystemDataTab
from tabs.UtilityTab import UtilityTab
from interactives.Canvas import Canvas

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
        createWelcomeTab = self.createWelcomeTab()
        componentsTab = ComponentsTab(centralDataManager=self.centralDataManager)
        generalSystemDataTab = GeneralSystemDataTab(centralDataManager=self.centralDataManager)
        utilityTab = UtilityTab(centralDataManager=self.centralDataManager)
        superstructureMappingTab = self.createSuperstructureMappingTab()
        # todo add a tab, so users can type a description of the project

        # Add tabs to the QTabWidget
        tabWidget.addTab(createWelcomeTab, "Welcome")
        tabWidget.addTab(componentsTab, "Chemical Components")
        tabWidget.addTab(generalSystemDataTab, "General System Data")
        tabWidget.addTab(utilityTab, "Utilities")
        tabWidget.addTab(superstructureMappingTab, "Superstructure Mapping")

    def createWelcomeTab(self):
        """
        This method creates the Welcome tab with a title, logo, and description of the application
        :return: QWidget for the Welcome tab
        """
        # Create a new QWidget for the Welcome tab
        welcomeWidget = QWidget()
        layout = QVBoxLayout(welcomeWidget)

        # Add a custom font from a file
        fontId = QFontDatabase.addApplicationFont("src/outdoor/user_interface/Merienda-VariableFont_wght.ttf")
        fontFamily = QFontDatabase.applicationFontFamilies(fontId)[0]
        titleFont = QFont(fontFamily, 44, QFont.Bold)

        # Set the title with a larger font
        titleLabel = QLabel("OUTDOOR")
        titleLabel.setFont(titleFont)
        titleLabel.setAlignment(Qt.AlignCenter)  # Center the title

        # Load and display the logo image
        logoLabel = QLabel()
        logoPixmap = QPixmap("src/outdoor/user_interface/logo.png")
        # Resize the pixmap to the desired size while maintaining aspect ratio
        scaledLogoPixmap = logoPixmap.scaled(500, 500, Qt.KeepAspectRatio,
                                             Qt.SmoothTransformation)  # Adjust (200, 200) to desired dimensions
        logoLabel.setPixmap(scaledLogoPixmap)
        logoLabel.setAlignment(Qt.AlignCenter)  # Center the logo

        # Set some descriptive text with a regular font
        descFont = QFont("Arial", 10)
        descLabel = QLabel("Welcome to OUTDOOR, your open source process simulator. "
                           "Here you can create, simulate, and optimize your industrial processes with ease.")
        descLabel.setFont(descFont)
        descLabel.setWordWrap(True)
        descLabel.setAlignment(Qt.AlignCenter)  # Center the text

        # Add widgets to the layout
        layout.addWidget(titleLabel)
        layout.addWidget(logoLabel)
        layout.addWidget(descLabel)

        # Set the layout on the welcomeWidget
        welcomeWidget.setLayout(layout)

        return welcomeWidget

    def createSuperstructureMappingTab(self):
        """
        This method creates the tab for the superstructure mapping where the user can drag and drop icons to create the
        superstructure
        :return: QWidget for the superstructure mapping tab
        """
        # Main layout
        mainLayout = QHBoxLayout()

        # Left panel for icons divided into sections
        leftPanel = QVBoxLayout()

        # Section 1: Input-Output
        inputOutputGroup = QGroupBox("Input-Output")
        inputOutputLayout = QVBoxLayout()
        iconInOutLabels = ['Input', 'Output']
        for i in iconInOutLabels:  # Adding 2 icons for Input-Output
            button = DraggableIcon(i)
            inputOutputLayout.addWidget(button)

        inputOutputGroup.setLayout(inputOutputLayout)
        leftPanel.addWidget(inputOutputGroup)

        # Section 2: Unit Processes
        unitProcessesGroup = QGroupBox("Unit Processes")
        unitProcessesLayout = QVBoxLayout()

        unitProcessLabels = ['Physical process',
                             'Stoichiometric reactor',
                             'Yield reactor',
                             'Generator (elec)',
                             'Generator (heat)']



        for i in unitProcessLabels:  # Adding 4 icons for Unit Processes
            button = DraggableIcon(i)
            unitProcessesLayout.addWidget(button)

        unitProcessesGroup.setLayout(unitProcessesLayout)
        leftPanel.addWidget(unitProcessesGroup)

        # Section 3: Distributors
        distributorsGroup = QGroupBox("Distributors")
        distributorsLayout = QVBoxLayout()
        distributorLabels = ['Boolean split', 'Defined split 2', 'Undefined split']
        for i in distributorLabels:  # Adding 3 icons for Distributors
            button = DraggableIcon(i)
            distributorsLayout.addWidget(button)
        distributorsGroup.setLayout(distributorsLayout)
        # create the left panel
        leftPanel.addWidget(distributorsGroup)

        # store all the labels of the Icons
        iconLabels = unitProcessLabels + distributorLabels + iconInOutLabels

        # Right panel as canvas (placeholder for now)
        rightPanel = Canvas(centralDataManager=self.centralDataManager, iconLabels=iconLabels)
        rightPanel.setStyleSheet("background-color: white;")

        # Adding panels to the main layout
        mainLayout.addLayout(leftPanel, 1)  # Add left panel with a ratio
        mainLayout.addWidget(rightPanel, 4)  # Add right panel with a larger ratio

        # Setting the central widget
        superstrucutreWidget = QWidget()
        superstrucutreWidget.setLayout(mainLayout)
        # self.setSuperstrucutreWidget(superstrucutreWidget)
        return superstrucutreWidget

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
