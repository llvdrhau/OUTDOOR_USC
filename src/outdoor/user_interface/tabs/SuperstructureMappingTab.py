from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QPushButton, QLabel, QTableWidgetItem, QHBoxLayout, \
    QGroupBox
from PyQt5.QtCore import Qt

from outdoor.user_interface.dialogs.CalculationWarning import CalculationWarning
from outdoor.user_interface.interactives.Canvas import Canvas
from outdoor.user_interface.interactives.DraggableIcon import DraggableIcon


class SuperstructureMappingTab(QWidget):
    def __init__(self, centralDataManager, parent=None):
        """
        This method creates the tab for the superstructure mapping where the user can drag and drop icons to create the
        superstructure
        :return: QWidget for the superstructure mapping tab
        """
        # Main layout
        super().__init__(parent)
        self.centralDataManager = centralDataManager
        self.mainLayout = QHBoxLayout()
        self.configs = centralDataManager.configs["componentConfigs"]
        # Left panel for icons divided into sections
        self.leftPanel = QVBoxLayout()

        # Section 1: Input-Output
        self.inputOutputGroup = QGroupBox("Input-Output")
        self.inputOutputLayout = QVBoxLayout()
        self.iconInOutLabels = ['Input', 'Output']
        for i in self.iconInOutLabels:  # Adding 2 icons for Input-Output
            button = DraggableIcon(i)
            self.inputOutputLayout.addWidget(button)

        self.inputOutputGroup.setLayout(self.inputOutputLayout)
        self.leftPanel.addWidget(self.inputOutputGroup)

        # Section 2: Unit Processes
        self.unitProcessesGroup = QGroupBox("Unit Processes")
        self.unitProcessesLayout = QVBoxLayout()
        self.unitProcessLabels = []

        for key, value in self.configs.items():
            if value == "True":
                self.unitProcessLabels.append(key)

        # self.unitProcessLabels = ['Physical Process',
        #                      'Stoichiometric Reactor',
        #                      'Yield Reactor',
        #                      'Generator (Elec)',
        #                      'Generator (Heat)',
        #                           'LCA']

        for i in self.unitProcessLabels:  # Adding icons for Unit Processes
            button = DraggableIcon(i)
            self.unitProcessesLayout.addWidget(button)

        self.unitProcessesGroup.setLayout(self.unitProcessesLayout)
        self.leftPanel.addWidget(self.unitProcessesGroup)

        # Section 3: Distributors
        self.distributorsGroup = QGroupBox("Distributors")
        self.distributorsLayout = QVBoxLayout()
        self.distributorLabels = ['Boolean split', 'Defined split 2', 'Undefined split']
        for i in self.distributorLabels:  # Adding 3 icons for Distributors
            button = DraggableIcon(i)
            self.distributorsLayout.addWidget(button)
        self.distributorsGroup.setLayout(self.distributorsLayout)
        # create the left panel
        self.leftPanel.addWidget(self.distributorsGroup)
        self.go_button = QPushButton("Calculate")
        self.go_button.clicked.connect(self.calculateWarning)
        self.leftPanel.addWidget(self.go_button)
        # store all the labels of the Icons
        self.iconLabels = self.unitProcessLabels + self.distributorLabels + self.iconInOutLabels

        # Right panel as canvas (placeholder for now)
        self.rightPanel = Canvas(centralDataManager=self.centralDataManager, iconLabels=self.iconLabels)
        self.rightPanel.setStyleSheet("background-color: white;")

        # Adding panels to the main layout
        self.mainLayout.addLayout(self.leftPanel, 1)  # Add left panel with a ratio
        self.mainLayout.addWidget(self.rightPanel, 4)  # Add right panel with a larger ratio

        # Setting the central widget

        self.setLayout(self.mainLayout)
        # self.setSuperstructureWidget(superstructureWidget)

    def calculateWarning(self):
        dialog = CalculationWarning(self.centralDataManager)

        if dialog.exec_():

            print("{} Dialog accepted")
        else:
            print("{} Dialog canceled")
