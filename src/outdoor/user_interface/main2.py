import uuid

from PyQt5.QtWidgets import (QApplication, QMainWindow, QHBoxLayout,
                             QGroupBox, QAction, QTableWidgetItem, QMessageBox, QFormLayout, QGraphicsView,
                             QGraphicsScene, QGraphicsObject, QGraphicsItem, QGraphicsEllipseItem,
                             QGraphicsPathItem, QComboBox, QFrame, QStyledItemDelegate, QToolTip, QLayout)
from PyQt5.QtCore import QMimeData, QRectF, QPointF, Qt
from PyQt5.QtGui import QDrag, QDoubleValidator, QFont, QPainterPath, QPainterPathStroker, QPixmap, \
    QFontDatabase, QCursor, QIntValidator

from PyQt5.QtWidgets import QWidget, QTabWidget
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QTableWidget, QPushButton, QLabel

import sys




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

class ComponentsTab(QWidget):
    """
    This class creates a tab for the chemical components and related data (e.g., molar weight, LHV, heat capacity, etc.)
    This is the tab that defines each chemical component and its properties used throught the flow sheet.
    """
    def __init__(self, centralDataManager, parent=None):
        super().__init__(parent)
        self.centralDataManager = centralDataManager

        self.layout = QVBoxLayout(self)

        # Title for the component tab
        self.title = QLabel("Components and related Data")
        self.title.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.title)

        # Table for the component data
        self.componentsTable = QTableWidget()
        self.componentsTable.setColumnCount(5)
        self.componentsTable.setHorizontalHeaderLabels([
            "Component", "Lower heating Value (MWh/t)",
            "Heat capacity (kJ/kg/K)", "Molecular weight (g/mol)",
            "CO2 - Equivalent"
        ])

        # adjust the width of the columns
        self.componentsTable.setColumnWidth(0, 150)
        self.componentsTable.setColumnWidth(1, 230)
        self.componentsTable.setColumnWidth(2, 180)
        self.componentsTable.setColumnWidth(3, 210)
        self.componentsTable.setColumnWidth(4, 150)

        # Set validators for the numeric columns using a custom delegate class
        self.doubleDelegate = DoubleDelegate(self.componentsTable)
        #self.doubleValidator = QDoubleValidator(0.0, 9999.99, 4)

        # add two empty rows to the table
        self.addComponentRow(data=["Ethanol", "7.44", "2.44", "46.07", ""])
        self.addComponentRow()

        # Add the table to the layout
        self.layout.addWidget(self.componentsTable)
        # Add Row Button
        self.addRowButton = QPushButton("Add Row")
        self.addRowButton.clicked.connect(self.addComponentRow)
        self.layout.addWidget(self.addRowButton)


        # Save button setup
        self.okButton = QPushButton("Save")
        self.okButton.clicked.connect(self.saveData)
        self.layout.addWidget(self.okButton)

        # Ensure the widget can receive focus to detect key presses
        self.setFocusPolicy(Qt.StrongFocus)
        self.setLayout(self.layout)

    def addComponentRow(self, data=None):
        rowPosition = self.componentsTable.rowCount()
        self.componentsTable.insertRow(rowPosition)

        if data is None or isinstance(data, bool):
            data = ["", "0", "", "", "0"]

        for i in range(self.componentsTable.columnCount()):
            item = QTableWidgetItem(data[i])
            self.componentsTable.setItem(rowPosition, i, item)
            if i > 0:  # Set the validator for numeric columns
                # Set the delegate for the column where only double values are allowed
                self.componentsTable.setItemDelegateForColumn(i, self.doubleDelegate)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Backspace:
            selectedItems = self.componentsTable.selectedItems()
            if selectedItems:
                selectedRow = selectedItems[0].row()  # Get the row of the first selected item
                self.componentsTable.removeRow(selectedRow)
        else:
            super().keyPressEvent(event)

    def saveData(self):

        # Collect data from the table
        tableData = self.collectData()

        # Save the data to the central data manager
        self.centralDataManager.addData("chemicalComponentsData", tableData)

        # Change the border of OK button to green
        # self.okButton.setStyleSheet("border: 2px solid green;")

    def collectData(self):
        # Collect data from the table
        tableData = []
        for row in range(self.componentsTable.rowCount()):
            rowData = []
            for column in range(self.componentsTable.columnCount()):
                item = self.componentsTable.item(row, column)
                rowData.append(item.text() if item else "")
            tableData.append(rowData)
        return tableData

class GeneralSystemDataTab(QWidget):
    """
    This class creates a tab for the general system data
    """
    def __init__(self, centralDataManager, parent=None):
        super().__init__(parent)
        self.centralDataManager = centralDataManager

        # Create a new QWidget for the General System Data tab
        self.layout = QFormLayout(self)
        self.subtitleFont = QFont("Arial", 11, QFont.Bold)
        # Set the background color of the widget
        self.setStyleSheet("background-color: #f5f5f5;")

        # Title for the general system data (centered)
        self.createSectionTitle(text="General System Data", centerAlign=True, color="#C7CEEA")

        self.projectNameLineEdit = QLineEdit()
        self.layout.addRow(QLabel("Project Name:"), self.projectNameLineEdit)

        #self.layout.addRow(QLabel("Project Name:"), QLineEdit(""))
        # layout.addRow(QLabel("Objective:"), QLineEdit("EBIT"))  # define this in the code
        # layout.addRow(QLabel("Optimization mode:"), QLineEdit("2-stage-recourse"))  # define this in the code

        # Title for the specific production of a product
        self.createSectionTitle(text="Specific Production", color="#B5EAD7")

        # Create a dropdown for "Product driven"
        self.productDrivenDropdown = QComboBox()
        self.productDrivenDropdown.addItems(["yes", "no"])  # Add options to the dropdown
        self.layout.addRow(QLabel("Product driven:"), self.productDrivenDropdown)

        self.productSelection = QComboBox()
        self.productSelection.addItems(["Product 1", "Product 2"])  # Add options to the dropdown
        self.layout.addRow(QLabel("Main product:"), self.productSelection)

        self.productLoadLineEdit = QLineEdit()
        self.productLoadLineEdit.setValidator(
            QDoubleValidator(0.00, 999999.99, 2))  # Set validator to restrict to floating-point numbers
        self.layout.addRow(QLabel("Product load:"), self.productLoadLineEdit)  # only floating numbers allowed as input

        # Connect the signal to the slot function
        self.productDrivenDropdown.currentIndexChanged.connect(lambda: self.productDrivenSwitch())

        # make title "general CAPEX parameters"
        self.createSectionTitle(text="General CAPEX parameters", color="#E2F0CB")

        # Add fields for the general CAPEX parameters
        self.operatingHoursLineEdit = QLineEdit("8000")
        self.layout.addRow(QLabel("Operating Hours:"), self.operatingHoursLineEdit)

        self.yearOfStudyLineEdit = QLineEdit("2018")
        self.layout.addRow(QLabel("Year of Study:"), self.yearOfStudyLineEdit)

        self.interestRateLineEdit = QLineEdit("0.05")
        self.layout.addRow(QLabel("Interest rate:"), self.interestRateLineEdit)

        self.detailLevelLineEdit = QComboBox()
        self.detailLevelLineEdit.addItems(["real", "fine", "rough", "average"])  # Add options to the dropdown
        self.layout.addRow(QLabel("Detail level of linearization of CAPEX:"), self.detailLevelLineEdit)

        self.indirectCostsLineEdit = QLineEdit("1.44")
        self.layout.addRow(QLabel("Indirect costs:"), self.indirectCostsLineEdit)

        self.DirectCostsLineEdit = QLineEdit("2.6")
        self.layout.addRow(QLabel("Direct costs:"), self.DirectCostsLineEdit)

        # todo: add different standard Direct and indirect costs factors for different processing plant types
        #  i.e., Solid, solid-liquid and liquid processing plants
        costFactors = {
            "Solid": {"Direct": 2.6, "Indirect": 1.44},
            "Solid-liquid": {"Direct": 2.6, "Indirect": 1.44},
            "Liquid": {"Direct": 2.6, "Indirect": 1.44}
        }
        # reference: p251 Table 6-9 of the book "Plant Design and Economics for Chemical Engineers, fith edition"


        # self.omFactorLineEdit = QLineEdit("0.04")
        # self.layout.addRow(QLabel("O&M Factor:"), self.omFactorLineEdit)


        # Heat pump parameters
        # Title for the Heat pump parameters section
        self.createSectionTitle("Heat pump parameters", color="#FFDAC1")

        # Add fields for the heat pump parameters
        self.heatPumpDropdown = QComboBox()
        self.heatPumpDropdown.addItems(["yes", "no"])  # Add options to the dropdown
        self.layout.addRow(QLabel("Heat pump switch:"), self.heatPumpDropdown)

        # Add fields for the heat pump parameters
        self.COPLineEdit = QLineEdit("2.5")
        self.COPLineEdit.setValidator(
            QDoubleValidator(0.00, 999999.99, 2))  # Set validator to restrict to floating-point numbers
        self.layout.addRow(QLabel("Coefficient of performance (COP):"), self.COPLineEdit)

        self.costLineEdit = QLineEdit("450")
        self.costLineEdit.setValidator(
            QDoubleValidator(0.00, 999999.99, 2))  # Set validator to restrict to floating-point numbers
        self.layout.addRow(QLabel("Cost per kW installed:"), self.costLineEdit)

        self.lifetimeLineEdit = QLineEdit("15")
        self.lifetimeLineEdit.setValidator(
            QDoubleValidator(1990, 2018, 0))  # Set validator to restrict to floating-point numbers
        self.layout.addRow(QLabel("Lifetime:"), self.lifetimeLineEdit)

        self.TINLineEdit = QLineEdit()
        self.TINLineEdit.setValidator(
            QDoubleValidator(0.00, 999999.99, 2))  # Set validator to restrict to floating-point numbers
        self.layout.addRow(QLabel("Inlet Temperature °C:"), self.TINLineEdit)

        self.TOUTLineEdit = QLineEdit()
        self.TOUTLineEdit.setValidator(
            QDoubleValidator(0.00, 999999.99, 2))  # Set validator to restrict to floating-point numbers
        self.layout.addRow(QLabel("Outlet Temperature °C:"), self.TOUTLineEdit)

        # Connect the signal to the slot function
        self.heatPumpDropdown.currentIndexChanged.connect(lambda: self.heatPumpSwitch())

        # Save button setup
        self.okButton = QPushButton("Save")
        self.okButton.clicked.connect(self.saveData)
        self.layout.addWidget(self.okButton)

        # layout widgets:
        # Customize the appearance of line edits and combo boxes
        lineEditStyleSheet = "QLineEdit { border-radius: 5px; padding: 5px; background-color: #ffffff; }"
        comboBoxStyleSheet = "QComboBox { border-radius: 5px; padding: 3px; background-color: #ffffff; }"
        pushButtonStyleSheet = "QPushButton { border-radius: 5px; padding: 5px; background-color: #FFAAEE; }"

        # Apply the stylesheets to the form layout's children
        for row in range(self.layout.rowCount()):
            for index in range(self.layout.rowCount()):
                widget = self.layout.itemAt(index, QFormLayout.FieldRole).widget()
                if isinstance(widget, QLineEdit):
                    widget.setStyleSheet(lineEditStyleSheet)
                elif isinstance(widget, QComboBox):
                    widget.setStyleSheet(comboBoxStyleSheet)
                elif isinstance(widget, QPushButton):
                    widget.setStyleSheet(pushButtonStyleSheet)

        # Set the layout on the generalSystemDataWidget
        self.setLayout(self.layout)

    def createSectionTitle(self, text, color="#e1e1e1", centerAlign=False):
        title = QLabel(text)
        title.setFont(self.subtitleFont)
        title.setStyleSheet(f"background-color: {color}; padding: 3px;")
        if centerAlign:
            title.setAlignment(Qt.AlignCenter)
        frame = QFrame()
        frame.setFrameShape(QFrame.HLine)
        frame.setFrameShadow(QFrame.Sunken)
        self.layout.addRow(title)
        self.layout.addRow(frame)

    def productDrivenSwitch(self):
        if self.productDrivenDropdown.currentText() == "no":
            # If "No" is selected, make the other fields not editable
            self.productSelection.setDisabled(True)
            self.productLoadLineEdit.setDisabled(True)
        else:
            # If "Yes" is selected, make the other fields editable
            self.productSelection.setDisabled(False)
            self.productLoadLineEdit.setDisabled(False)

    def heatPumpSwitch(self):
        if self.heatPumpDropdown.currentText() == "no":
            # If "No" is selected, make the other fields not editable
            self.COPLineEdit.setDisabled(True)
            self.costLineEdit.setDisabled(True)
            self.lifetimeLineEdit.setDisabled(True)
            self.TINLineEdit.setDisabled(True)
            self.TOUTLineEdit.setDisabled(True)
        else:
            # If "Yes" is selected, make the other fields editable
            self.COPLineEdit.setDisabled(False)
            self.costLineEdit.setDisabled(False)
            self.lifetimeLineEdit.setDisabled(False)
            self.TINLineEdit.setDisabled(False)
            self.TOUTLineEdit.setDisabled(False)


    def saveData(self):

        # Collect data from the table
        generalData = self.collectData()

        # Save the data to the central data manager
        self.centralDataManager.addData("generalData", generalData)
        print("data saved")
        print(generalData)

        # Change the border of OK button to green
        # self.okButton.setStyleSheet("border: 2px solid green;")

    def collectData(self):
        # Collect data from the Widget fields
        data = {
            "projectName": self.projectNameLineEdit.text(),
            "productDriven": self.productDrivenDropdown.currentText(),
            "mainProduct": self.productSelection.currentText(),
            "productLoad": self.productLoadLineEdit.text(),
            "operatingHours": self.operatingHoursLineEdit.text(),
            "yearOfStudy": self.yearOfStudyLineEdit.text(),
            "interestRate": self.interestRateLineEdit.text(),
            "detailLevel": self.detailLevelLineEdit.currentText(),
            # "omFactor": self.omFactorLineEdit.text(), => not used in the code is unit specific and not general
            "heatPumpSwitch": self.heatPumpDropdown.currentText(),
            "COP": self.COPLineEdit.text(),
            "cost": self.costLineEdit.text(),
            "lifetime": self.lifetimeLineEdit.text(),
            "TIN": self.TINLineEdit.text(),
            "TOUT": self.TOUTLineEdit.text(),
        }
        return data

class UtilityTab(QWidget):
    def __init__(self, centralDataManager, parent=None):
        super().__init__(parent)
        self.centralDataManager = centralDataManager

        # Main layout for the tab
        layout = QVBoxLayout(self)

        # Upper table for general utilities
        self.utilitiesTable = QTableWidget(3, 3)  # 3 rows for utilities, 4 columns for data
        self.utilitiesTable.setHorizontalHeaderLabels(["Costs (€/MWh)", "CO2 Emissions (t/MWh)", "Fresh water depletion (t/MWh)"])
        self.utilitiesTable.setVerticalHeaderLabels(["Electricity", "Heat", "Chilling"])
        # set the width of the columns to be bigger so it fits the column names
        self.utilitiesTable.setColumnWidth(0, 120)
        self.utilitiesTable.setColumnWidth(1, 180)
        self.utilitiesTable.setColumnWidth(2, 230)
        self._populateUtilitiesTable()
        # Set validators for the numeric columns using a custom delegate class
        self.doubleDelegateUtility = DoubleDelegate(self.utilitiesTable)
        for i in range(0, self.utilitiesTable.columnCount()):
            self.utilitiesTable.setItemDelegateForColumn(i, self.doubleDelegateUtility)


        # Lower table for temperature levels
        self.temperatureTable = QTableWidget(5, 2)  # 5 rows for temperature levels, 3 columns for data
        self.temperatureTable.setHorizontalHeaderLabels(["Temperature (°C) ", "Costs (€/MWh)"])
        self.temperatureTable.setVerticalHeaderLabels(["Superheated steam", "High pressure steam", "Medium pressure steam", "Low pressure steam", "Cooling water"])
        self.temperatureTable.setColumnWidth(0, 140)
        self.temperatureTable.setColumnWidth(1, 120)
        self._populateTemperatureTable()
        # Set validators for the numeric columns using a custom delegate class
        self.doubleDelegateTemperature = DoubleDelegate(self.temperatureTable)
        for i in range(0, self.temperatureTable.columnCount()):
            self.temperatureTable.setItemDelegateForColumn(i, self.doubleDelegateTemperature)

        # Add tables to the layout
        layout.addWidget(QLabel("Utilities"))
        layout.addWidget(self.utilitiesTable)
        layout.addWidget(QLabel("Cost of heat"))
        layout.addWidget(self.temperatureTable)

        # Save button
        saveButton = QPushButton("Save Data")
        saveButton.clicked.connect(self._saveData)
        layout.addWidget(saveButton)

    def _populateUtilitiesTable(self):
        # Fill in the utilities table with example data
        utilitiesData = [
            [87, 0.014, 0],
            ['', 0.248, 0],
            [35, 0.1,   0]
        ]

        for i, row in enumerate(utilitiesData):
            for j, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                self.utilitiesTable.setItem(i, j, item)
                # make the width of the columns bigger
                if value =='':  # Costs column has float values
                    # item.setFlags(item.flags() | Qt.ItemIsEditable)
                    self.utilitiesTable.item(i, j).setFlags(self.utilitiesTable.item(i, j).flags() & ~Qt.ItemIsEditable)

    def _populateTemperatureTable(self):
        # Fill in the temperature table with example data
        temperatureData = [
            [600, 34],
            [330, 32],
            [220, 30],
            [130, 29],
            [15, 0.22]
        ]

        for i, (temp, cost) in enumerate(temperatureData):
            # make the temperature column
            self.temperatureTable.setItem(i, 0, QTableWidgetItem(str(temp)))  # Temperature column
            # make the temperature column uneditable
            #self.temperatureTable.item(i, 0).setFlags(self.temperatureTable.item(i, 0).flags() & ~Qt.ItemIsEditable)

            # make the cost column
            costItem = QTableWidgetItem(str(cost))
            costItem.setFlags(costItem.flags() | Qt.ItemIsEditable)  # Make cost editable
            self.temperatureTable.setItem(i, 1, costItem)  # Cost column

    def _saveData(self):
        """
        Save the data from the tables to the central data manager
        """
        utilitiesData = self._collectUtilitiesData()
        temperatureData = self._collectTemperatureData()

        self.centralDataManager.addData("utilitiesData", utilitiesData)
        self.centralDataManager.addData("temperatureData", temperatureData)
        print("Data saved")


    def _collectUtilitiesData(self):
        utilitiesData = []
        for row in range(self.utilitiesTable.rowCount()):
            rowData = []
            for column in range(self.utilitiesTable.columnCount()):
                item = self.utilitiesTable.item(row, column)
                rowData.append(item.text() if item else "")
            utilitiesData.append(rowData)
        return utilitiesData

    def _collectTemperatureData(self):
        temperatureData = []
        for row in range(self.temperatureTable.rowCount()):
            temp = self.temperatureTable.item(row, 0).text()
            cost = self.temperatureTable.item(row, 1).text()
            temperatureData.append([temp, cost])
        return temperatureData


class DraggableIcon(QPushButton):
    """
    A QPushButton subclass that allows the button to be dragged and dropped into the canvas. The button text is used to
    identify the icon type. This class is used to create the icons in the left panel of superstructureMapping Widget.

    """
    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.setCheckable(True)

    def mouseMoveEvent(self, e):
        if e.buttons() != Qt.LeftButton:
            return

        # Start a drag operation when the mouse moves with the left button held down
        drag = QDrag(self)
        mimeData = QMimeData()

        # Use the button's text as the data to be dragged
        mimeData.setText(self.text())
        drag.setMimeData(mimeData)

        drag.exec_(Qt.MoveAction)

class Canvas(QGraphicsView):
    """
    A widget (QGraphicsView) for the right panel where icons can be dropped onto it. Here is where the user can create
    the superstructure by dragging and dropping icons from the left panel. This class also handles the connections between
    the icons.
    """
    def __init__(self, centralDataManager, iconLabels):
        super().__init__()
        # Store the icon data manager for use in the widget
        self.centralDataManager = centralDataManager
        # store the icon labels
        self.iconLabels = iconLabels
        # Set up the scene for scalable graphics
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)  # For better visual quality
        # Enable drag and drop events
        self.setAcceptDrops(True)
        # To keep a reference to the currently selected icon
        self.selectedElement = None



        self.setStyleSheet("background-color: white;")
        self.iconData = {}  # Add this line to store dialog data
        # add index to icons according to the type of icon:
        # use UUIDs for the indexs!
        self.index_input = []
        self.index_process = []
        self.index_split = []
        self.index_output = []
        self.UUID = None


        # track the start and end points of the line
        self.startPoint = None
        self.endPoint = None
        self.currentLine = None
        self.drawingLine = False
        self.endPort = None
        self.startPort = None

        self.setMouseTracking(True)  # Enable mouse tracking

        # Define scale factors for zooming
        self.zoomInFactor = 1.25  # Zoom in factor (25% larger)
        self.zoomOutFactor = 1 / self.zoomInFactor  # Zoom out factor (inverse of zoom in)
        self.scaleFactor = 1.0  # Initial scale factor

    def wheelEvent(self, event):
        # Get the angle delta of the wheel event
        angleDelta = event.angleDelta().y()
        if angleDelta > 0:
            # Wheel scrolled up, zoom in
            self.scaleView(self.zoomInFactor)
        else:
            # Wheel scrolled down, zoom out
            self.scaleView(self.zoomOutFactor)

    def scaleView(self, scaleFactor):
        # Apply the scale factor to the view
        factor = self.transform().scale(scaleFactor, scaleFactor).mapRect(QRectF(0, 0, 1, 1)).width()
        if factor < 0.07 or factor > 100:
            # Prevent zooming out too much or zooming in too much
            return

        self.scale(scaleFactor, scaleFactor)
        self.scaleFactor *= scaleFactor

    def dragEnterEvent(self, e):
        print('Iniciate dragging icon')
        e.accept()

    def dragMoveEvent(self, event):
        #print("Drag Move Event")
        event.accept()

    def dropEvent(self, event):
        print('dropped icon')
        mimeData = event.mimeData()
        if mimeData.hasText():
            # Extract the necessary information from the MIME data
            text = mimeData.text()
            position = event.pos()
            scenePos = self.mapToScene(position)
            # get the correct icon type based on the text
            icon = self.createMovableIcon(text, event.pos())

            # Set the icon's position to the mouse cursor's position
            icon.setPos(scenePos)
            self.scene.addItem(icon)  # Add the created icon to the scene
            event.accept()

    def createMovableIcon(self, text, position):
        """
        This method should create a new instance of MovableIcon or similar class based on the text
        :param text: (string) The text of the icon to identify the type
        :param position: QPoint position of the mouse click
        :return:
        """

        # Mapping of text to icon_type and index
        icon_map = {
            "Boolean split": ("bool_split", self.index_split),
            "Defined split 2": ("defined_split", self.index_split),
            "Undefined split": ("undefined_split", self.index_split),

            "Input": ("input", self.index_input),
            "Output": ("output", self.index_output),

            "Physical process": ("physical_process", self.index_process),
            "Stoichiometric reactor": ("stoichiometric_reactor", self.index_process),
            "Yield reactor": ("yield_reactor", self.index_process),

            "Generator (elec)": ("generator_elec", self.index_process),
            "Generator (heat)": ("generator_heat", self.index_process),
        }



        # Check if the text is in the icon_map
        if text in icon_map:
            icon_type, index_list = icon_map[text]
            # Create unique UUID
            UUID = uuid.uuid4()
            index_list.append(UUID)
            # Create MovableIcon
            iconWidget = MovableIcon(text, centralDataManager=self.centralDataManager, iconID=UUID, icon_type=icon_type)
            iconWidget.setPos(self.mapToScene(position))
            return iconWidget
        else:
            # Raise error if the icon type is not recognized
            raise Exception("Icon type not recognized")  # You can handle this error in a more user-friendly way

    def mouseMoveEvent(self, event):
        if self.currentLine is not None:
            # Map the mouse position to scene coordinates
            scenePos = self.mapToScene(event.pos())
            # Update the current line's endpoint to follow the mouse
            # This is where you need to adjust for the InteractiveLine class
            self.currentLine.endPoint = scenePos
            self.currentLine.updateAppearance()  # Redraw the line with the new end point

            # If you have any other behavior when moving the mouse, handle it here
        else:
            # Not drawing a line, so pass the event to the base class
            super().mouseMoveEvent(event)

    def startLine(self, port, pos):
        """
        Start drawing a new line from the given port (function called in the IconPort class)
        :param port: IconPort object or TriangleIconPorts object
        :param pos: Position of the mouse click
        :return:
        """
        if port.occupied:
            # do not start a new line if the port is already connected
            return
        else:
            if 'split' not in port.iconType and port.portType == 'exit' and len(port.connectionLines) > 0:
                # the port of an icon that is not a split icon and is an exit port is now occupied only one
                # stream can leave. The extra if statement is to avoid the case where the line was deleted
                # and no longer exists
                port.occupied = True
                # stop the line drawing process with return statement
                return

            # Start drawing a new line from this port
            print('iniciating start line')
            self.startPort = port
            self.startPoint = pos  # Always corresponds to the exit port
            self.currentLine = InteractiveLine(startPoint=pos, endPoint=pos,
                                               startPort=port)  # QGraphicsLineItem(QLineF(pos, pos))
            port.connectionLines.append(self.currentLine)
            self.scene.addItem(self.currentLine)

    def endLine(self, port, pos):
        """
        End drawing a new line from the given port (function called in the IconPort class)
        :param port: IconPort object or TriangleIconPorts object
        :param pos: Position of the mouse click
        :return:
        """
        # Do not start a new line if the startPort is not set error has occured
        if self.startPort is None:
            return

        # Do not end a new line in a port that is already occupied
        if port.occupied:
            return

        if 'split' in port.iconType and port.portType == 'entry' and len(port.connectionLines) > 0:
            port.occupied = True
            # stop the line drawing process with return statement
            return


        print('initiating end line')
        #port.connectionLines.append(self.currentLine)
        self.endPort = port
        self.endPoint = pos # allways corresponds to the entry port
        # Here you might want to validate if the startPort and endPort can be connected
        print(self.currentLine)
        print(self.startPort != self.endPort)
        if self.currentLine and self.startPort != port:
            self.currentLine.endPoint = pos  # Update the end point
            self.currentLine.endPort = port # Update the end port
            self.currentLine.updateAppearance()  # Update the line appearance based on its current state
            port.connectionLines.append(self.currentLine)
            self.centralDataManager.addConnection(self.startPort, port, self.startPoint, pos, self.currentLine)

        # rest the positions and switches to None
        self.startPoint = None
        self.endPoint = None
        self.currentLine = None
        self.drawingLine = False

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Backspace:
            for item in self.scene.selectedItems():
                if isinstance(item, MovableIcon):
                    for port in item.ports:
                        #port.occupied = False
                        for line in port.connectionLines:
                            # remove the line from the port object
                            line.startPort.connectionLines.remove(line)
                            # update the occupancy of the port to False
                            line.startPort.occupied = False
                            # remove the line from the port object
                            line.endPort.connectionLines.remove(line)
                            # update the occupancy of the port to False
                            line.endPort.occupied = False

                            # remove the line from the scene
                            self.scene.removeItem(line)
                    self.scene.removeItem(item)

                    # TODO, update any necessary data in the centralDataManager here
                    #self.centralDataManager.removeIconData(item.iconID)



        super().keyPressEvent(event)

    def mousePressEvent(self, event):
        """
        This method is called when the mouse is pressed in the canvas. It is used to deselect icons and lines when
        pressing on an empty space in the canvas.
        :param event: click event
        :return: updates the selected element
        """
        item = self.itemAt(event.pos())

        if isinstance(item, MovableIcon):
            if self.selectedElement is not None and self.selectedElement != item:
                # If there is a previously selected icon and it's not the current item, reset its pen
                self.selectedElement.pen = QPen(Qt.black, 1)

                if isinstance(self.selectedElement, InteractiveLine):
                    self.selectedElement.setSelectedLine(False) # switch off visibility of the control point for the line
                    self.selectedElement.updateAppearance()

                else:
                    self.selectedElement.update()

            # Update the currently selected icon
            self.selectedElement = item

        elif isinstance(item, InteractiveLine):
            if self.selectedElement is not None and self.selectedElement != item:
                # If there is a previously selected icon and it's not the current item, reset its pen
                self.selectedElement.pen = QPen(Qt.black, 1)
                if isinstance(self.selectedElement, InteractiveLine):
                    self.selectedElement.setSelectedLine(False) # switch off visibility of the control point for the line
                    self.selectedElement.updateAppearance()
                else:
                    self.selectedElement.update()

            # Update the currently selected icon
            self.selectedElement = item

        elif isinstance(item, ControlPoint):
            pass

        else: # if the selected element is an icon or a line, reset the pen
            if self.selectedElement is not None:
                # If there is a previously selected line, reset its pen
                self.selectedElement.pen = QPen(Qt.black, 1)

                if isinstance(self.selectedElement, InteractiveLine):
                    self.selectedElement.setSelectedLine(False) # switch off visibility of the control point for the line
                    self.selectedElement.updateAppearance()
                elif isinstance(self.selectedElement, MovableIcon):
                    self.selectedElement.update()

                self.selectedElement = None  # Reset the currently selected icon

        super().mousePressEvent(event)

class IconPort(QGraphicsEllipseItem):
    """
    A QGraphicsEllipseItem subclass to represent the entry and exit ports of the icons. This class handles the connection
    of lines between the ports.
    """
    def __init__(self, parent, portType , iconID, pos=None):
        super().__init__(-5, -5, 10, 10, parent)  # A small circle
        self.portType = portType  # 'entry' or 'exit'
        self.iconID = iconID
        self.setBrush(Qt.black)
        self.connectionLines = []  # List to store the lines connected to this iconPort
        self.occupied = False  # Flag to indicate if the port is already connected to a line
        self.iconType = parent.icon_type

        if pos:
            self.setPos(pos) # Set the position if it was passed (for split icons)
        else:
            # Position the port correctly on the parent icon based on portType
            match portType:
                case 'exit':
                    self.setPos(parent.boundingRect().width(), parent.boundingRect().height() / 2)
                case 'entry':
                    self.setPos(0, parent.boundingRect().height() / 2)


    def mousePressEvent(self, event):
        """
        Clicking on an exit port starts drawing a line from it
        """
        if event.button() == Qt.LeftButton and self.portType == 'exit':
            canvas = self.scene().views()[0]  # Get the first (and likely only) view
            if isinstance(canvas, Canvas):  # Check if it's actually your Canvas class
                canvas.startLine(self, event.scenePos())

    def mouseReleaseEvent(self, event):
        """
        The line is drawn from the exit port to the entry port
        """
        if self.portType == 'entry':
            canvas = self.scene().views()[0]  # Get the first (and likely only) view
            if isinstance(canvas, Canvas):  # Check if it's actually your Canvas class
                canvas.endLine(self, event.scenePos())

    def updateConnectedLines(self, centralDataManager):
        """
        Update the position of the lines connected to this port (function called in the Canvas class) when the port is
        moved. or that is when the icon is moved.
        :param centralDataManager:
        :return:
        """
        if self.connectionLines:
            # Loop through all lines connected to this port
            for line in self.connectionLines:
                # Update the position of the line's start or end, depending on the port's type
                if self.portType == "exit":
                    # If this is an exit port, update the line's start position
                    line.setStartPoint(self.scenePos())
                else:
                    # If this is an entry port, update the line's end position
                    line.setEndPoint(self.scenePos())

                # Redraw the line with its new position
                line.updateAppearance()

                # Optionally, TODO update any necessary data in the centralDataManager here
                # For example, you might update the stored positions of the line's endpoints
                # if you are tracking those for any reason (not shown in this example).

class MovableIcon(QGraphicsObject):
    """
    A QGraphicsObject subclass to represent the icons that can be dragged and dropped onto the canvas. This class also
    handles the ports of the icons. The icon type is used to determine the number and position of the ports. This class
    is used to create the icons in the canvas and makes them draggable, handels their appearance and opens dialogos.
    """
    def __init__(self, text, centralDataManager, icon_type, iconID=None):
        super().__init__()
        self.text = text
        self.icon_type = icon_type
        self.iconID = iconID
        self.centralDataManager = centralDataManager  # to Store and handel dialog data for each icon

        # set the flags for the icon to be movable and selectable
        self.setFlags(QGraphicsObject.ItemIsMovable) # Enable the movable flag
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)  # Enable item change notifications
        self.setFlag(QGraphicsItem.ItemIsSelectable)  # Enable the selectable flag

        self.dragStartPosition = None
        self.nExitPorts = 2  # initial Number of exit ports for split icons


        self.pen = QPen(Qt.black, 1)  # Default pen for drawing the border
        #self.penBoarder = QPen(Qt.NoPen)
        # define the ports:
        self.ports = []
        match icon_type:
            case 'input':
                self.ports.append(IconPort(self, portType='exit', iconID=iconID))
            case 'output':
                self.ports.append(IconPort(self, portType='entry', iconID=iconID))
            case 'bool_split':
                self.addSplitPorts()
            case 'defined_split':
                self.addSplitPorts()
            case 'undefined_split':
                self.addSplitPorts()
            # otherwise give port for entry and exit
            case _:
                self.ports.append(IconPort(self, portType='exit', iconID=iconID))
                self.ports.append(IconPort(self, portType='entry', iconID=iconID))

    def addSplitPorts(self):
        # Add an entry port
        entryPort = IconPort(self, portType='entry', iconID=self.iconID,
                             pos=QPointF(0, self.boundingRect().height() / 2))
        self.ports.append(entryPort)

        # Add exit ports
        exitPort = IconPort(self, pos=QPointF(self.boundingRect().width(), self.boundingRect().height() / 2),
                            portType='exit', iconID=self.iconID)
        self.ports.append(exitPort)

        # code for multiple exit ports, deleet if you're not going to use it
        # hightTriangle = self.boundingRect().height()
        # step = hightTriangle / (self.nExitPorts + 1)  # +1 to distribute evenly
        # for n in range(self.nExitPorts):
        #     hightPosition = step * (n + 1)  # +1 because n starts at 0
        #     exitPort = IconPort(self, pos=QPointF(self.boundingRect().width(), hightPosition),
        #                                  portType='exit', iconID=self.iconID)
        #     self.ports.append(exitPort)

    def updateExitPorts(self, nExitPortsNew):
        # Calculate the new step size
        hightTriangle = self.boundingRect().height()
        step = hightTriangle / (nExitPortsNew + 1)

        if nExitPortsNew > self.nExitPorts:
            # Add new ports if the new count is greater than the existing number of ports
            # Update positions of existing ports
            existingPorts = [port for port in self.childItems() if
                             isinstance(port, IconPort) and port.portType == 'exit']
            minPorts = min(len(existingPorts), nExitPortsNew)
            for i in range(minPorts):
                hightPosition = step * (i + 1)
                existingPorts[i].setPos(QPointF(self.boundingRect().width(), hightPosition))

            # Add new ports if the new count is greater than the existing number of ports
            for i in range(len(existingPorts), nExitPortsNew):
                hightPosition = step * (i + 1)
                newPorts = IconPort(self, QPointF(self.boundingRect().width(), hightPosition), 'exit')
                self.ports.append(newPorts)
            # update the number of exit ports
            self.nExitPorts = nExitPortsNew
        else:
            # Remove ports if the new count is less than the existing number of ports
            # Remove existing exit ports
            for port in self.childItems():
                if isinstance(port, IconPort) and port.portType == 'exit':
                    self.scene().removeItem(port)
                    del port

            # Recalculate positions and add new exit ports
            hightTriangle = self.boundingRect().height()
            step = hightTriangle / (nExitPortsNew + 1)
            for n in range(nExitPortsNew):
                hightPosition = step * (n + 1)
                exitPort = IconPort(self, portType='exit', pos=QPointF(self.boundingRect().width(), hightPosition), iconID=self.iconID)
                self.ports.append(exitPort)

            # update the number of exit ports
            self.nExitPorts = nExitPortsNew
    def boundingRect(self):
        if 'split' in self.icon_type:
            return QRectF(0, 0, 60, 60)
        else:
            return QRectF(0, 0, 120, 40)

    def paint(self, painter, option, widget=None):

        if 'split' in self.icon_type:
            # Set background color based on the icon type
            backgroundColor = QColor(self.getBackgroundColor(self.icon_type))
            painter.setBrush(backgroundColor)

            # Create a QPainterPath object
            path = QPainterPath()
            path.moveTo(0, 30)
            path.lineTo(60, 60)
            path.lineTo(60, 0)
            path.closeSubpath()

            # Draw the triangle
            painter.fillPath(path, painter.brush())
            painter.setPen(self.pen)
        else:
            # Set background color based on the icon type
            backgroundColor = QColor(self.getBackgroundColor(self.icon_type))
            painter.setBrush(backgroundColor)
            painter.setPen(self.pen)
            painter.drawRoundedRect(self.boundingRect(), 10, 10)

            painter.setPen(Qt.black)
            font = QFont("Arial", 10)
            painter.setFont(font)
            painter.drawText(self.boundingRect(), Qt.AlignCenter, self.text)

    def getBackgroundColor(self, icon_type):
        if icon_type == 'input':
            return "#c6e2e9"
        elif icon_type == 'output':
            return "#ffcaaf"
        elif icon_type == 'physical_process':
            return "#a7bed3"
        elif icon_type == 'bool_split':
            # the color dark red
            return '#8B0000'
        elif icon_type == 'defined_split':
            # the color dark green
            return '#006400'
        elif icon_type == 'undefined_split':
            # the color dark blue
            return '#00008B'
        # if none of the above return a gray color
        return "#D3D3D3"

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Change the pen color to indicate the icon is selected black
            self.pen = QPen(QColor("red"), 2)  # 3 is the width of the pen
            self.update()  # Update the icon's appearance
            self.setCursor(Qt.ClosedHandCursor)
            self.dragStartPosition = event.pos()

        super().mousePressEvent(event)  # Ensure the event is propagated

    def mouseMoveEvent(self, event):
        if not self.dragStartPosition:
            return
        dragDistance = (event.pos() - self.dragStartPosition).manhattanLength()
        if dragDistance >= QApplication.startDragDistance():
            # Calculate the new position
            newPos = event.scenePos() - self.dragStartPosition
            self.setPos(newPos)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.setCursor(Qt.OpenHandCursor)
        self.dragStartPosition = None
        super().mouseReleaseEvent(event)  # Ensure the event is propagated

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            if 'split' in self.icon_type:
                self.openSplittingDialog()
            else:
                self.openParametersDialog()

    # methods to manage the positions of lines between the icons
    def itemChange(self, change, value):
        if change == QGraphicsObject.ItemPositionHasChanged:
            for port in self.childItems():
                if hasattr(port, 'updateConnectedLines'):
                    port.updateConnectedLines(self.centralDataManager)
        return super().itemChange(change, value)

    def openSplittingDialog(self):
        # Retrieve existing data for this icon, if the iconID is not in the dict, return an empty dict
        existingData = self.centralDataManager.data.get(self.iconID, {})

        # open the dialog and handle the data entered by the user after pressing OK
        dialog = SplittingDialog(initialData=existingData)
        nonesentialParameters = ["Splitting Ratio:"]  # 1 nonesentialParameters for this dialog

        # open the dialog and handle the data entered by the user after pressing OK
        if dialog.exec_():
            dataDialog = dialog.collectData()
            dataDialogCopy = dataDialog.copy()

            # delete the elements in dataInputDialog that are not relevant. i.e., minProduction and maxProduction
            for parm in nonesentialParameters:
                dataDialogCopy.pop(parm, None)

            # Validate data before saving
            missing_fields = [key for key, value in dataDialogCopy.items() if not value]
            if missing_fields:
                # save what is already in filled in the widgets so you don't lose it when the dialog is reopened
                self.centralDataManager.data[self.iconID] = dataDialogCopy
                QMessageBox.critical(QApplication.activeWindow(), "Missing Input(s)",
                                     f"Error: {', '.join(missing_fields)} field(s) are missing a value. Please fill them in.")

                self.openSplittingDialog()  # Reopen the dialog for correction
                return

            # I now want to update the exit ports based on the number of exit ports from the dialog
            nExitPorts = int(dataDialog.get('nExitPorts', 2))
            if nExitPorts != self.nExitPorts:
                self.updateExitPorts(nExitPorts)


            # Save the data if all fields are filled
            self.centralDataManager.data[self.iconID] = dataDialog

            print("{} Dialog accepted".format(self.icon_type))
        else:
            print("{} Dialog canceled".format(self.icon_type))
    def openParametersDialog(self):
        """
        Handles the data entered by the user after pressing OK for the icon parameters dialog
        :return:
        """

        # Retrieve existing data for this icon
        existingData = self.centralDataManager.data.get(self.iconID, {}) # if the iconID is not in the dict, return an empty dict


        # choose the dialog to open based on the type of icon that was double clicked
        if self.icon_type == 'input':
            dialog = InputParametersDialog(initialData=existingData)
            nonesentialParameters = []

        elif self.icon_type == 'output':
            dialog = OutputParametersDialog(initialData=existingData)
            nonesentialParameters = ['minProduction', 'maxProduction']

        elif self.icon_type == 'physical_process':
            dialog = PhysicalProcessesDialog(initialData=existingData, centralDataManager=self.centralDataManager)
            nonesentialParameters = []

        elif self.icon_type == 'stoichiometric_reactor':
            dialog = StoichiometricReactorDialog(initialData=existingData, centralDataManager=self.centralDataManager)
            nonesentialParameters = []

        # elif self.icon_type == 'generator_elec':
        #     dialog = GeneratorElecDialog(initialData=existingData)
        #     nonesentialParameters = []

        else:
            pass # place holder for other icon types
            #raise Exception("Icon type not recognized")

        # open the dialog and handle the data entered by the user after pressing OK
        if dialog.exec_():
            dataDialog = dialog.collectData()
            dataDialogCopy = dataDialog.copy()

            # delete the elements in dataInputDialog that are not relevant. i.e., minProduction and maxProduction
            for parm in nonesentialParameters:
                dataDialogCopy.pop(parm, None)

            # Validate data before saving
            missing_fields = [key for key, value in dataDialogCopy.items() if not value]
            if missing_fields:
                # save what is already in filled in the widgets so you don't lose it when the dialog is reopened
                self.centralDataManager.data[self.iconID] = dataDialogCopy
                QMessageBox.critical(QApplication.activeWindow(), "Missing Input(s)",
                                     f"Error: {', '.join(missing_fields)} field(s) are missing a value. Please fill them in.")

                self.openParametersDialog()  # Reopen the dialog for correction
                return

            # rename the box to the source name
            # Check if sourceName was updated and update the MovableIcon's label accordingly
            newSourceName = dataDialog.get('Name', '').strip()
            if newSourceName:
                self.text = newSourceName  # Update the text attribute to reflect the new source name
                self.update()  # Update the icon's appearance i.e., repaint the icon name

            # Save the data if all fields are filled
            self.centralDataManager.data[self.iconID] = dataDialog

            print("{} Dialog accepted".format(self.icon_type))
        else:
            print("{} Dialog canceled".format(self.icon_type))

# ------------------------
# Central data manager
# ------------------------
# Central data manager for all data related to icons and associated dialogs
class CentralDataManager:
    """
    A class to manage all data related to the icons and data from other tabs and their associated dialogs.
    This class stores the data
    """
    def __init__(self):
        self.data = {}  # Dictionary to store data indexed by icon ID
        self.namesChemicalComponents = []  # list to store chemical components data

    def addData(self, field, data):
        self.data[field] = data

        if field == 'chemicalComponentsData':
            for species in data:
                if species[0] not in self.namesChemicalComponents:
                    self.namesChemicalComponents.append(species[0]) # Add the species name to the list of chemical components

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
            {'endIconID': (line.line().p1(), line.line().p2, line)}) # todo I need to find a way to pass on endIconID... place holder for now
            self.data[iconID]['positionExitPortIcon'] = line.line().p1()
        else:
            self.data[iconID]['connectionLineEntry2Exit'].update(
                {'endIconID': (line.line().p1(), line.line().p2, line)}) # todo I need to find a way to pass on endIconID...
            self.data[iconID]['positionExitPortIcon'] = line.line().p1()

        print(self.data[iconID]['connectionLineExit2Entry'])

# --------------------------------
# managing the lines between the icons
# ------------------------
class ControlPoint(QGraphicsEllipseItem):
    """
    A QGraphicsEllipseItem subclass to represent the control point for curved lines. This class is used to create the
    control points when a line is curved and allows the user to adjust the curve by moving the control point.
    """
    def __init__(self, x, y, parent=None):
        super().__init__(-5, -5, 10, 10, parent)  # A small circle as the control point
        self.setBrush(QColor(255, 0, 0))  # Red color
        self.setFlag(QGraphicsEllipseItem.ItemIsMovable)
        self.setFlag(QGraphicsEllipseItem.ItemSendsGeometryChanges)
        self.setFlag(QGraphicsItem.ItemIsFocusable)  # Enable focus

        self.setPos(x, y)  # Set initial position

    def itemChange(self, change, value):
        if change == QGraphicsEllipseItem.ItemPositionHasChanged and self.parentItem():
            self.parentItem().updateAppearance() # Update the line's appearance when the control point is moved, the methode is in the InteractiveLine class (the parent)
        return super().itemChange(change, value)

class InteractiveLine(QGraphicsPathItem):
    """
    This class is used to create the lines between the icons. It allows the user to draw straight or curved lines by
    double-clicking on the line to toggle between the two modes. The control point for curved lines is only shown when
    the line is curved and selected.
    """
    def __init__(self, startPoint, endPoint, startPort=None, endPort=None , parent=None):
        super().__init__(parent)
        self.startPoint = startPoint
        self.endPoint = endPoint
        self.isCurved = False  # Line starts as straight
        self.controlPoint = None  # Control point is not created until needed
        self.startPort = startPort
        self.endPort = endPort

        # set Flags
        # self.setAcceptHoverEvents(True)  # Enable hover events
        # self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsFocusable)  # Enable focus

        self.selected = True  # Track selection state
        self.pen = QPen(Qt.black, 1)  # Default pen for drawing the line
        self.updateAppearance()


    def setStartPoint(self, point):
        self.startPoint = point
        self.updateAppearance()

    def setEndPoint(self, point):
        self.endPoint = point
        self.updateAppearance()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # The user clicked on the line
            self.setSelectedLine(not self.selected)  # Select the line

            if self.selected:
                self.pen = QPen(Qt.red, 1.5)  # Increase line thickness
            else:
                self.pen = QPen(Qt.black, 1)

            self.updateAppearance()  # Update appearance


        super().mousePressEvent(event)


    def mouseDoubleClickEvent(self, event):
        self.isCurved = not self.isCurved  # Toggle between curved and straight line
        if self.isCurved and not self.controlPoint:
            # Create and add the control point only if transitioning to curved for the first time
            midPoint = QPointF((self.startPoint.x() + self.endPoint.x()) / 2,
                               (self.startPoint.y() + self.endPoint.y()) / 2)
            self.controlPoint = ControlPoint(midPoint.x(), midPoint.y(), self)

        self.updateAppearance()
        super().mouseDoubleClickEvent(event)

    def setSelectedLine(self, selected):
        self.selected = selected
        if self.isCurved and self.controlPoint:
            self.controlPoint.setVisible(self.selected)
        elif not self.isCurved and self.controlPoint:
            self.controlPoint.setVisible(False)


    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Backspace and self.selected:
            # Delete the line if the Backspace key is pressed while the line is selected
            self.scene().removeItem(self)
            self.setSelectedLine(False)

            # reset the occupied flag of the start and end port
            self.startPort.occupied = False
            self.endPort.occupied = False

            # deleet the line from the connectionLines list of the ports
            self.startPort.connectionLines.remove(self)
            self.endPort.connectionLines.remove(self)

            # todo remove the line from the data dict as well, from the centralDataManager

        super().keyPressEvent(event)

    def updateAppearance(self):
        path = QPainterPath(self.startPoint)
        if self.isCurved and self.controlPoint:
            # Use the control point's current position for the curve
            controlPos = self.controlPoint.pos()
            path.quadTo(controlPos, self.endPoint)
        else:
            path.lineTo(self.endPoint)

        self.setPath(path)
        self.setPen(self.pen)

    def shape(self):
        # Override shape method to return a wider hitbox
        stroker = QPainterPathStroker()
        stroker.setWidth(10)  # Set the hitbox width to be larger than the line width
        return stroker.createStroke(self.path())


    # def hoverEnterEvent(self, event):
    #     # Show the control point when hovering, but only if the line is curved
    #     if self.isCurved and self.controlPoint:
    #         self.controlPoint.setVisible(True)
    #
    # def hoverLeaveEvent(self, event):
    #     # Hide the control point when not hovering
    #     if self.controlPoint:
    #         self.controlPoint.setVisible(False)

# ---------------------------------------------------
# Dialogs for parameters of different types of icons
# ---------------------------------------------------
class SplittingDialog(QDialog):
    """
    Opens a dialog to set the splitting parameters for the split icon. The dialog allows the user to set the number of
    exit ports and the splitting ratio for each exit port.
    """
    def __init__(self, initialData):
        super().__init__()
        self.setWindowTitle("Splitting Parameters")
        self.setGeometry(100, 100, 400, 300)  # Adjust size as needed

        layout = QVBoxLayout(self)

        # define the amount of exit ports
        layout.addWidget(QLabel("Number of exit ports:"))
        self.nExitPorts = QLineEdit(self)
        layout.addWidget(self.nExitPorts)
        # Set validator to restrict to floating-point numbers
        self.nExitPorts.setValidator(QDoubleValidator(2, 10, 0))

        # Splitting Ratio
        # this is a placeholder for now, you can add more fields as needed,
        # should acttualy be a table with the splitting ratio for each exit port and specifiying the components that are
        # split
        layout.addWidget(QLabel("Splitting Ratio:"))
        self.splittingRatio = QLineEdit(self)
        layout.addWidget(self.splittingRatio)
        # Set validator to restrict to floating-point numbers
        self.splittingRatio.setValidator(QDoubleValidator(0.00, 1.00, 2))

        # OK and Cancel buttons
        buttonsLayout = QHBoxLayout()
        self.okButton = QPushButton("OK", self)
        self.okButton.clicked.connect(self.accept)
        buttonsLayout.addWidget(self.okButton)

        self.cancelButton = QPushButton("Cancel", self)
        self.cancelButton.clicked.connect(self.reject)
        buttonsLayout.addWidget(self.cancelButton)

        layout.addLayout(buttonsLayout)

        if initialData:
            self.populateDialog(initialData)

    def collectData(self):
        """Collect data from all fields to save state."""
        data = {
            'splittingRatio': self.splittingRatio.text(),
            'nExitPorts': self.nExitPorts.text(),
        }
        return data

    def populateDialog(self, data):
        """
        Populate the dialog with the data provided in the dictionary.
        The keys in the dictionary should match the names of the widgets.
        :param data: Dictionary with the data to populate the dialog with
        """
        # Directly settable fields
        if 'splittingRatio' in data:
            self.splittingRatio.setText(data['splittingRatio'])
        if 'nExitPorts' in data:
            self.nExitPorts.setText(data['nExitPorts'])

class InputParametersDialog(QDialog):
    """
    Opens a dialog to set the input parameters for the input icon. The dialog allows the user to set the source name,
    price input, components, CO2 emission factor, lower limit, and upper limit. The components are entered in a table
    format with two columns: Component Name and % Composition. The user can add multiple rows to enter multiple
    components and their composition in the feedstock.
    """
    def __init__(self, initialData):

        super().__init__()
        self.setStyleSheet("""
                                    QDialog {
                                        background-color: #f2f2f2;
                                    }
                                    QLabel {
                                        color: #333333;
                                    }
                                    QLineEdit {
                                        border: 1px solid #cccccc;
                                        border-radius: 2px;
                                        padding: 5px;
                                        background-color: #ffffff;
                                        selection-background-color: #b0daff;
                                    }
                                    QPushButton {
                                        color: #ffffff;
                                        background-color: #5a9;
                                        border-style: outset;
                                        border-width: 2px;
                                        border-radius: 10px;
                                        border-color: beige;
                                        font: bold 14px;
                                        padding: 6px;
                                    }
                                    QPushButton:hover {
                                        background-color: #78d;
                                    }
                                    QPushButton:pressed {
                                        background-color: #569;
                                        border-style: inset;
                                    }
                                    QTableWidget {
                                        border: 1px solid #cccccc;
                                        selection-background-color: #b0daff;
                                    }
                                """)
        self.setWindowTitle("Input Parameters")
        self.setGeometry(100, 100, 400, 300)  # Adjust size as needed

        layout = QVBoxLayout(self)

        # Input name
        layout.addWidget(QLabel("Source Name:"))
        self.sourceName = QLineEdit(self)
        layout.addWidget(self.sourceName)

        # Price input
        layout.addWidget(QLabel("Price Input (euro/t):"))
        self.priceInput = QLineEdit(self)
        layout.addWidget(self.priceInput)
        # Set validator to restrict to floating-point numbers
        self.priceInput.setValidator(QDoubleValidator(0.00, 999999.99, 2))

        # Components table
        layout.addWidget(QLabel("Components:"))
        self.componentsTable = QTableWidget(0, 2, self)  # Initial rows, 2 columns
        self.componentsTable.setHorizontalHeaderLabels(["Component Name", "% Composition"])
        layout.addWidget(self.componentsTable)

        # Add a row to tabel button
        self.addRowButton = QPushButton("Add Row", self)
        self.addRowButton.clicked.connect(self.addRowToComponentsTable)
        layout.addWidget(self.addRowButton)
        # Initialize the table with an example row (optional)
        self.addRowToComponentsTable()


        # CO2 Emission Factor
        layout.addWidget(QLabel("CO2 Emission Factor:"))
        self.co2EmissionFactor = QLineEdit(self)
        layout.addWidget(self.co2EmissionFactor)
        # Set validator to restrict to floating-point numbers
        self.co2EmissionFactor.setValidator(QDoubleValidator(0.00, 999999.99, 2))

        # Lower Limit
        layout.addWidget(QLabel("Lower Limit (t):"))
        self.lowerLimit = QLineEdit(self)
        layout.addWidget(self.lowerLimit)
        # Set validator to restrict to floating-point numbers
        self.lowerLimit.setValidator(QDoubleValidator(0.00, 999999.99, 2))

        # Upper Limit
        layout.addWidget(QLabel("Upper Limit (t):"))
        self.upperLimit = QLineEdit(self)
        layout.addWidget(self.upperLimit)
        # Set validator to restrict to floating-point numbers
        self.upperLimit.setValidator(QDoubleValidator(0.00, 999999.99, 2))

        # OK and Cancel buttons
        self.okButton = QPushButton("OK", self)
        self.okButton.clicked.connect(self.accept)
        layout.addWidget(self.okButton)
        self.cancelButton = QPushButton("Cancel", self)
        self.cancelButton.clicked.connect(self.reject)
        layout.addWidget(self.cancelButton)

        # populate the dialog with existing data (initialData) if it is not empty
        if initialData:
            self.populateInputDialog(initialData)

    def addItemToTable(self, row, col, text):
        item = QTableWidgetItem(text)
        item.setFlags(item.flags() | Qt.ItemIsEditable)  # Ensure the item is editable
        self.componentsTable.setItem(row, col, item)

    def addRowToComponentsTable(self, component_name="", composition=""):
        rowPosition = self.componentsTable.rowCount()
        self.componentsTable.insertRow(rowPosition)
        self.addItemToTable(rowPosition, 0, component_name)  # Component name
        self.addItemToTable(rowPosition, 1, composition)  # % Composition

    def collectData(self):
        """Collect data from all fields to save state."""
        data = {
            'Name': self.sourceName.text(),
            'priceInput': self.priceInput.text(),
            'components': [],
            'co2EmissionFactor': self.co2EmissionFactor.text(),
            'lowerLimit': self.lowerLimit.text(),
            'upperLimit': self.upperLimit.text()
        }

        # Collect data from the components table
        for row in range(self.componentsTable.rowCount()):
            component_name = self.componentsTable.item(row, 0).text() if self.componentsTable.item(row, 0) else ""
            composition = self.componentsTable.item(row, 1).text() if self.componentsTable.item(row, 1) else ""
            data['components'].append((component_name, composition))

        return data

    def populateInputDialog(self, data):
        """
        Populate the dialog with the data provided in the dictionary.
        The keys in the dictionary should match the names of the widgets.
        :param data: Dictionary with the data to populate the dialog with
        """
        # Directly settable fields
        if 'Name' in data:
            self.sourceName.setText(data['Name'])
        if 'priceInput' in data:
            self.priceInput.setText(data['priceInput'])
        if 'co2EmissionFactor' in data:
            self.co2EmissionFactor.setText(data['co2EmissionFactor'])
        if 'lowerLimit' in data:
            self.lowerLimit.setText(data['lowerLimit'])
        if 'upperLimit' in data:
            self.upperLimit.setText(data['upperLimit'])

        # For the component table
        if 'components' in data:
            self.componentsTable.setRowCount(0)  # Clear existing rows
            for component_name, composition in data['components']:
                self.addRowToComponentsTable(component_name, composition)

# Dialog for output parameters
class OutputParametersDialog(QDialog):
    """
    Opens a dialog to set the output parameters for the output icon. The dialog allows the user to set the product name,
    price output, CO2 credits, minimum production, and maximum production. The user can set the price output and CO2
    credits as floating-point numbers, and the minimum and maximum production as floating-point numbers.
    """
    def __init__(self, initialData):
        super().__init__()

        # set style
        self.setStyleSheet("""
                                            QDialog {
                                                background-color: #f2f2f2;
                                            }
                                            QLabel {
                                                color: #333333;
                                            }
                                            QLineEdit {
                                                border: 1px solid #cccccc;
                                                border-radius: 2px;
                                                padding: 5px;
                                                background-color: #ffffff;
                                                selection-background-color: #b0daff;
                                            }
                                            QPushButton {
                                                color: #ffffff;
                                                background-color: #5a9;
                                                border-style: outset;
                                                border-width: 2px;
                                                border-radius: 10px;
                                                border-color: beige;
                                                font: bold 14px;
                                                padding: 6px;
                                            }
                                            QPushButton:hover {
                                                background-color: #78d;
                                            }
                                            QPushButton:pressed {
                                                background-color: #569;
                                                border-style: inset;
                                            }
                                            QTableWidget {
                                                border: 1px solid #cccccc;
                                                selection-background-color: #b0daff;
                                            }
                                        """)

        self.setWindowTitle("Output Parameters")
        self.setGeometry(100, 100, 400, 300)  # Adjust size as needed

        layout = QVBoxLayout(self)

        # Product Type
        self.productName = QLineEdit(self)
        layout.addLayout(self._formRow("Product Name:", self.productName))

        # Price Output
        self.priceOutput = QLineEdit(self)
        layout.addLayout(self._formRow("Price Output (€/t):", self.priceOutput))
        self.priceOutput.setValidator(QDoubleValidator(0.00, 999999.99, 2))

        # CO2 Credits
        self.co2Credits = QLineEdit(self)
        layout.addLayout(self._formRow("CO2 Credits:", self.co2Credits))
        # Set validator to restrict to floating-point numbers
        self.co2Credits.setValidator(QDoubleValidator(0.00, 999999.99, 2))

        # minimum production
        self.minProduction = QLineEdit(self)
        layout.addLayout(self._formRow("Minimum production (t/h):", self.minProduction))
        # Set validator to restrict to floating-point numbers
        self.minProduction.setValidator(QDoubleValidator(0.00, 999999.99, 2))

        # maximum production
        self.maxProduction = QLineEdit(self)
        layout.addLayout(self._formRow("Maximum production (t/h):", self.maxProduction))
        # set validator to restrict to floating-point numbers
        self.maxProduction.setValidator(QDoubleValidator(0.00, 999999.99, 2))

        # OK and Cancel buttons
        buttonsLayout = QHBoxLayout()
        self.okButton = QPushButton("OK", self)
        self.okButton.clicked.connect(self.accept)
        buttonsLayout.addWidget(self.okButton)

        self.cancelButton = QPushButton("Cancel", self)
        self.cancelButton.clicked.connect(self.reject)
        buttonsLayout.addWidget(self.cancelButton)

        layout.addLayout(buttonsLayout)

        # populate the dialog with existing data (initialData) if it is not empty
        if initialData:
            self.populateOutputDialog(initialData)

    def _formRow(self, label, widget):
        """Helper function to create a row in the form."""
        layout = QHBoxLayout()
        layout.addWidget(QLabel(label))
        layout.addWidget(widget)
        return layout

    def collectData(self):
        """Collect data from all fields to save state."""
        data = {
            'Name': self.productName.text(),
            'priceOutput': self.priceOutput.text(),
            'co2Credits': self.co2Credits.text(),
            'minProduction': self.minProduction.text(),
            'maxProduction': self.minProduction.text()
        }
        return data

    def populateOutputDialog(self, data):
        """
        Populate the dialog with the data provided in the dictionary.
        The keys in the dictionary should match the names of the widgets.
        :param data: Dictionary with the data to populate the dialog with
        """
        # Directly settable fields
        if 'Name' in data:
            self.productName.setText(data['Name'])
        if 'priceOutput' in data:
            self.priceOutput.setText(data['priceOutput'])
        if 'co2Credits' in data:
            self.co2Credits.setText(data['co2Credits'])
        if 'minProduction' in data:
            self.minProduction.setText(data['minProduction'])
        if 'maxProduction' in data:
            self.maxProduction.setText(data['maxProduction'])

class PhysicalProcessesDialog(QDialog):
    """
    Opens a dialog to set the physical processes parameters for the physical processes icon. The dialog allows the user to
    set the name, processing group, reference flow, and exponent. The user can set the reference flow and exponent as
    floating-point numbers. The processing group and name are text fields.
    """
    def __init__(self, initialData, centralDataManager):
        super().__init__()
        # Set style (existing style setup is fine and will be applied)
        # set style
        self.setStyleSheet("""
                                                   QDialog {
                                                       background-color: #f2f2f2;
                                                   }
                                                   QLabel {
                                                       color: #333333;
                                                   }
                                                   QLineEdit {
                                                       border: 1px solid #cccccc;
                                                       border-radius: 2px;
                                                       padding: 5px;
                                                       background-color: #ffffff;
                                                       selection-background-color: #b0daff;
                                                   }
                                                   QPushButton {
                                                       color: #ffffff;
                                                       background-color: #5a9;
                                                       border-style: outset;
                                                       border-width: 2px;
                                                       border-radius: 10px;
                                                       border-color: beige;
                                                       font: bold 14px;
                                                       padding: 6px;
                                                   }
                                                   QPushButton:hover {
                                                       background-color: #78d;
                                                   }
                                                   QPushButton:pressed {
                                                       background-color: #569;
                                                       border-style: inset;
                                                   }
                                                   QTableWidget {
                                                       border: 1px solid #cccccc;
                                                       selection-background-color: #b0daff;
                                                   }
                                               """)
        self.centralDataManager = centralDataManager

        self.setWindowTitle("Physical Processes Parameters")
        self.setGeometry(100, 100, 600, 400)  # Adjust size as needed

        self.subtitleFont = QFont("Arial", 9, QFont.Bold)

        tabWidget = QTabWidget(self)
        tabWidget.addTab(self._createGeneralParametersTab(), "General Parameters")
        tabWidget.addTab(self._createCostRelatedFactorsTab(), "Cost Related Parameters")
        tabWidget.addTab(self._createUtilityConsumptionTab(), "Utility Consumption")
        tabWidget.addTab(self._createHeatingConsumptionTab(), "Heating Requirements")
        tabWidget.addTab(self._createConcentrationTab(), "Concentration Factors")
        # You can add more tabs as needed...

        layout = QVBoxLayout(self)
        layout.addWidget(tabWidget)

        # OK and Cancel buttons
        buttonsLayout = QHBoxLayout()
        self.okButton = QPushButton("OK", self)
        self.okButton.clicked.connect(self.accept)
        buttonsLayout.addWidget(self.okButton)

        self.cancelButton = QPushButton("Cancel", self)
        self.cancelButton.clicked.connect(self.reject)
        buttonsLayout.addWidget(self.cancelButton)

        layout.addLayout(buttonsLayout)

        # populate the dialog with existing data (initialData) if it is not empty
        if initialData:
            self.populateDialog(initialData)

        self.setFocusPolicy(Qt.StrongFocus)


    def _createGeneralParametersTab(self):
        # General Factors Tab
        widget = QWidget()
        layout = QFormLayout()

        # ---------------------------------------------------------------
        # General parameters
        # ---------------------------------------------------------------
        self._createSectionTitle(text="General", layout=layout)

        # Name input
        self.nameInput = QLineEdit(self)
        # set object name
        self.nameInput.setObjectName("nameInput")
        self._addRowWithTooltip(layout, "Name:", self.nameInput,
                                "This is the name of the unit process.")

        # Processing Group input
        self.processingGroupInput = QLineEdit(self)
        # set object name
        self.processingGroupInput.setObjectName("processingGroupInput")
        tooltipText = """This parameter is used to group processes together that must be activated if one of the
        technologies from the group is chosen. the group is used to group processes that are mutually exclusive. This
        parameters is indicated by a number."""
        self._addRowWithTooltip(layout, labelText="Processing Group:", widget=self.processingGroupInput,
                                tooltipText=tooltipText)
        self.processingGroupInput.setValidator(QIntValidator(0, 20))

        # Life time Unit process
        self.lifeTimeUnitProcess = QLineEdit(self)
        self.lifeTimeUnitProcess.setText("20")  # Replace "Your Start Value" with the value you want to set
        # set object name
        self.lifeTimeUnitProcess.setObjectName("lifeTimeUnitProcess")
        tooltipText = """The life time of the unit process in years."""
        self._addRowWithTooltip(layout, labelText="Life Time Unit Process (years):", widget=self.lifeTimeUnitProcess,
                                tooltipText=tooltipText)
        # only double values are allowed
        self.lifeTimeUnitProcess.setValidator(QDoubleValidator(0.00, 999999.99, 2))

        # working hours per year
        self.fullLoadingHours = QLineEdit(self)
        self.fullLoadingHours.setText("8000")  # Replace "Your Start Value" with the value you want to set
        self.fullLoadingHours.setObjectName("fullLoadingHours") # set object name
        tooltipText = """The working hours per year of the unit process."""
        self._addRowWithTooltip(layout, labelText="Working Hours per Year:", widget=self.fullLoadingHours, tooltipText=tooltipText)


        # CO2 Emissions for Building
        self.co2EmissionsBuilding = QLineEdit(self)
        self.co2EmissionsBuilding.setText("0.00")  # Replace "Your Start Value" with the value you want to set
        self.co2EmissionsBuilding.setObjectName("co2EmissionsBuilding")         # set object name
        tooltipText = """This is the CO2 emissions for the building housing the unit process."""
        self._addRowWithTooltip(layout, labelText="CO2 Emissions Building:", widget=self.co2EmissionsBuilding,
                                tooltipText=tooltipText)
        # only double values are allowed
        self.co2EmissionsBuilding.setValidator(QDoubleValidator(0.00, 999999.99, 2))

        # ---------------------------------------------------------------
        #  # operating temperatures
        # ---------------------------------------------------------------
        self._createSectionTitle(text="Inlet/Outlet Temperatures", layout=layout)
        # temperature entering the process
        self.temperatureEnteringProcess = QLineEdit(self)
        tooltipText = """The temperature of the mass entering the process."""
        self._addRowWithTooltip(layout, labelText="Temperature in (°C):", widget=self.temperatureEnteringProcess, tooltipText=tooltipText)
        # only double values are allowed
        self.temperatureEnteringProcess.setValidator(QDoubleValidator(0.00, 999999.99, 2))

        # temperature leaving the process
        self.temperatureLeavingProcess = QLineEdit(self)
        tooltipText = """The temperature of the mass leaving the process."""
        self._addRowWithTooltip(layout, labelText="Temperature out (°C):", widget=self.temperatureLeavingProcess,
                                tooltipText=tooltipText)
        # only double values are allowed
        self.temperatureLeavingProcess.setValidator(QDoubleValidator(0.00, 999999.99, 2))

        # temperature entering the unit process 2
        self.temperatureEnteringUnitProcess2 = QLineEdit(self)
        tooltipText = """If you want to conjoin 2 process into one block you can pass on the operation temperatures of
                         the second process."""
        self._addRowWithTooltip(layout, labelText="Temperature in unit process 2 (°C):",
                                widget=self.temperatureEnteringUnitProcess2, tooltipText=tooltipText)
        # only double values are allowed
        self.temperatureEnteringUnitProcess2.setValidator(QDoubleValidator(0.00, 999999.99, 2))

        # temperature leaving the unit process 2
        self.temperatureLeavingUnitProcess2 = QLineEdit(self)
        tooltipText = """If you want to conjoin 2 process into one block you can pass on the operation temperatures of
                            the second process."""
        self._addRowWithTooltip(layout, labelText="Temperature out unit process 2 (°C):",
                                widget=self.temperatureLeavingUnitProcess2, tooltipText=tooltipText)
        # only double values are allowed
        self.temperatureLeavingUnitProcess2.setValidator(QDoubleValidator(0.00, 999999.99, 2))

        # ---------------------------------------------------------------
        #  parameters Annualized Capital Costs
        # ---------------------------------------------------------------

        self._createSectionTitle(text="Annualized Capital Costs", layout=layout)

        # operating and maintenance cost
        self.operatingAndMaintenanceCost = QLineEdit(self)
        self.operatingAndMaintenanceCost.setText("0.04")  #
        tooltipText = """The annual operating and maintenance factor of the process: is a percentage of the fixed capital investment
                                            of that process used to maintain and operate the unit operation per year (give reference!)."""
        labelText = "Operating and Maintenance factor (y\u207B\u00B9):"
        self._addRowWithTooltip(layout, labelText=labelText, widget=self.operatingAndMaintenanceCost,
                                tooltipText=tooltipText)
        # only double values are allowed
        self.operatingAndMaintenanceCost.setValidator(QDoubleValidator(0.00, 999999.99, 2))

        # Direct Cost Factor
        self.directCostFactor = QLineEdit(self)
        self.directCostFactor.setText("2.6")  # Replace "Your Start Value" with the value you want to set
        tooltipText = """Direct costs like installation, electrics etc. based on the approach by Peters et al.
                            This factor is multiplied by the Equipment costs."""
        self._addRowWithTooltip(layout, labelText="Direct Cost Factor:", widget=self.directCostFactor,
                                tooltipText=tooltipText)
        # only double values are allowed
        self.directCostFactor.setValidator(QDoubleValidator(0.00, 999999.99, 2))

        # indirect Cost Factor
        self.indirectCostFactor = QLineEdit(self)
        self.indirectCostFactor.setText("1.44")
        tooltipText = """indirect costs like engineering, legal costs, insurance based on the approach by Peters et al.
                            This factor is multiplied by the Equipment costs."""
        self._addRowWithTooltip(layout, labelText="Indirect Cost Factor:", widget=self.indirectCostFactor,
                                tooltipText=tooltipText)

        # only double values are allowed
        self.indirectCostFactor.setValidator(QDoubleValidator(0.00, 999999.99, 2))

        # ---------------------------------------------------------------
        #  parameters Reoccurring Annualized Capital Costs
        # ---------------------------------------------------------------
        # add a title to the tab
        self._createSectionTitle(text="Annual Reoccurring Capital Costs", layout=layout)

        # Create a QHBoxLayout
        hlayout = QHBoxLayout()

        # turn over time
        self.turnOverTime = QLineEdit(self)
        self.turnOverTime.setValidator(QDoubleValidator(0.00, 999999.99, 2))
        # Create QComboBox
        self.comboBoxUnits = QComboBox(self)
        self.comboBoxUnits.addItem("years")
        self.comboBoxUnits.addItem("hours")
        # Add QLineEdit and QComboBox to the QHBoxLayout
        hlayout.addWidget(self.turnOverTime)
        hlayout.addWidget(self.comboBoxUnits)

        tooltipText = """The turn over time is the time that passes before a component (e.g., membranes) needs to be
        replaced in the unit process """
        self._addRowWithTooltip(layout, labelText="Turn Over Time:", widget=hlayout, tooltipText=tooltipText)


        # Turn over factor
        self.turnOverFactor = QLineEdit(self)
        tooltipText = """Percentage of the raw purchase equipment costs to pay for parts to replace.""" # Cu^(RE) in the thesis of Philpp
        self._addRowWithTooltip(layout, labelText="Turn Over Factor:", widget=self.turnOverFactor, tooltipText=tooltipText)
        # only double values are allowed
        self.turnOverFactor.setValidator(QDoubleValidator(0.00, 0.99, 2))

        widget.setLayout(layout)

        return widget

    def _createCostRelatedFactorsTab(self):
        # Cost Related Factors Tab
        widget = QWidget()
        layout = QFormLayout()

        self._createSectionTitle(text="Parameters for economy of scale", layout=layout)

        # Reference Flow type
        self.referenceFlowType = QComboBox(self)
        # add options to ComboBox
        self.referenceFlowType.addItem("Entering Flow")
        self.referenceFlowType.addItem("Exiting Flow")
        self.referenceFlowType.addItem("Electricity consumption")
        self.referenceFlowType.addItem("Electricity production (generators)")
        self.referenceFlowType.addItem("Heat production (generators)")
        self.referenceFlowType.setObjectName("referenceFlowType")

        tooltipText = """The reference flow type is the type of flow that is used to calculate the Equipment Costs of
                                the unit process. The relevant components need to be defined if mass flow are selected."""

        self._addRowWithTooltip(layout, labelText="Reference Flow Type:", widget=self.referenceFlowType, tooltipText=tooltipText)
        # # Connect the signal to the slot function
        self.referenceFlowType.currentIndexChanged.connect(lambda: self._componentSelectionSwitch(type="Cost"))

        # Reference Flow input
        self.referenceFlowInput = QLineEdit(self)
        self.referenceFlowInput.setValidator(QDoubleValidator(0.00, 999999.99, 2))
        # set object name
        self.referenceFlowInput.setObjectName("referenceFlowInput")
        self.referenceFlowUnit = QLabel(self)
        self.referenceFlowUnit.setText("t/h")  # Replace "Your Start Value" with the value you want to set
        self.referenceFlowUnit.setFixedWidth(50)   # make the lable bigger in width
        self.referenceFlowUnit.setFont(self.subtitleFont)  # make it bold


        hlayout = QHBoxLayout()
        hlayout.addWidget(self.referenceFlowInput)
        hlayout.addWidget(self.referenceFlowUnit)

        tooltipText = """The reference flow is the amount of material that is used to produce the product."""
        self._addRowWithTooltip(layout, labelText="Reference Flow:", widget=hlayout, tooltipText=tooltipText)


        #Components table
        #layout.addWidget(QLabel("Components:"))
        self.componentsTable = QTableWidget(0, 1, self)  # Initial rows, columns
        self.componentsTable.setHorizontalHeaderLabels(["Component Name"])
        self.componentsTable.setColumnWidth(0, 200)  # make column 1 wider

        # add the table to the layout
        tooltipText= """The chemicals species selected are the ones that are used to calculate the Equipment Costs of
                        the unit process based on the mass flow (if Enetering or Exiting flow is the selected Reference flow type)."""
        self._addRowWithTooltip(layout, labelText="Components:", widget=self.componentsTable,
                                tooltipText=tooltipText)

        # make selectable, so rows can be deleted by pressing the delete key
        self.componentsTable.setSelectionBehavior(QTableWidget.SelectRows)  # Row selection
        self.componentsTable.setSelectionMode(QTableWidget.SingleSelection)  # Single row at a time
        self.componentsTable.setObjectName("componentsTable")


        # Add a row to tabel button
        self.addRowButton = QPushButton("Add Component", self)
        self.addRowButton.clicked.connect(self._addRowToTable)
        # set object name
        self.addRowButton.setObjectName("addRowButton")
        layout.addWidget(self.addRowButton)
        # Initialize the table with an example row (optional)
        self._addRowToTable(tabName="cost")


        # reference cost
        self.referenceCost = QLineEdit(self)
        self.referenceCost.setText("0.00")  # Replace "Your Start Value" with the value you want to set
        self.referenceCost.setObjectName("referenceCost")  # set object name
        tooltipText = """The reference cost is the cost of installing the unit with the specified reference flow."""
        self._addRowWithTooltip(layout, labelText="Reference Cost (M€):", widget=self.referenceCost, tooltipText=tooltipText)

        # reference year
        self.referenceYear = QLineEdit(self)
        self.referenceYear.setText("2020")  # Replace "Your Start Value" with the value you want to set
        self.referenceYear.setObjectName("referenceYear")  # set object name
        tooltipText = """The reference year is the year in which the reference cost was calculated."""
        self._addRowWithTooltip(layout, labelText="Reference Year:", widget=self.referenceYear, tooltipText=tooltipText)


        # Exponent input
        self.exponentInput = QLineEdit(self)
        self.exponentInput.setText("0.67")  # preallocate the value, with it's default value
        self.exponentInput.setValidator(QDoubleValidator(0.00, 5.00, 2))
        # set object name
        self.exponentInput.setObjectName("exponentInput")
        tooltipText = """The exponent is used to calculate the Equipment Costs of the unit process according to
                        economies of scale."""
        self._addRowWithTooltip(layout, labelText="Exponent:", widget=self.exponentInput, tooltipText=tooltipText)

        widget.setLayout(layout)
        return widget

    def _createUtilityConsumptionTab(self):
        """
        Create the tab for the utility consumption parameters.
        :return:
        """

        # Create common elements
        def createReferenceFlowTypeComboBox(name):
            """
            Create a combobox for the reference flow type.
            :param name:
            :return:
            """
            comboBox = QComboBox(self)
            comboBox.addItems([
                "Entering mass Flow", "Exiting mass Flow",
                "Entering Molar Flow", "Exiting Molar Flow",
                "Entering Flow Cp", "Exiting Flow Cp"
            ])
            comboBox.setObjectName(name)
            return comboBox


        # Energy Consumption Tab
        widget = QWidget()
        layout = QFormLayout()

        # ----------------------------------------------------------------------------------------------------------
        # Electricity Requirements
        self._createSectionTitle(text="Electricity Requirements", layout=layout)
        # ----------------------------------------------------------------------------------------------------------

        # Reference Flow type Energy
        self.referenceFlowTypeEnergy = createReferenceFlowTypeComboBox("referenceFlowTypeEnergy")
        tooltipText = """The reference flow type is the type of flow that is used to calculate the Energy Consumption of
                            the unit process."""
        self._addRowWithTooltip(layout, labelText="Reference Flow Type:", widget=self.referenceFlowTypeEnergy,
                                tooltipText=tooltipText)
        self.referenceFlowTypeEnergy.currentIndexChanged.connect(lambda: self._componentSelectionSwitch(type="Electricity"))

        # Electricity Consumption parameter
        self.energyConsumption = QLineEdit(self)
        self.energyConsumption.setText("0.00")
        self.energyConsumption.setValidator(QDoubleValidator(0.00, 999999.99, 2))
        self.energyConsumption.setObjectName("energyConsumption")
        tooltipText = """The energy consumption of the unit process."""
        # add a label to the energy consumption units
        self.referenceFlowUnitEnergy = QLabel(self)
        self.referenceFlowUnitEnergy.setText("MWh/t")  # Replace "Your Start Value" with the value you want to set
        self.referenceFlowUnitEnergy.setFixedWidth(120) # make the lable bigger in width
        self.referenceFlowUnitEnergy.setFont(self.subtitleFont)  # make it bold

        # combine the energy consumption and the unit in a horizontal layout
        hlayout = QHBoxLayout()
        hlayout.addWidget(self.energyConsumption)
        hlayout.addWidget(self.referenceFlowUnitEnergy)
        # add the energy consumption to the layout
        self._addRowWithTooltip(layout, labelText="Energy Consumption:", widget=hlayout, tooltipText=tooltipText)

        # Components table
        self.componentsTableEnergy = QTableWidget(0, 1, self)  # Initial rows, columns
        self.componentsTableEnergy.setHorizontalHeaderLabels(["Component Name"])
        self.componentsTableEnergy.setColumnWidth(0, 200)  # make column 1 wider
        #  add the tabel to the widget
        tooltipText = """The chemicals species selected are the ones that are used to calculate the energy consumption of
                                the unit process based on the mass flow (e.g., E_consumption (MW) = F_in (t/h) * Tau (MWh/t) )."""
        self._addRowWithTooltip(layout, labelText="Components:", widget=self.componentsTableEnergy, # add same table to the layout
                                tooltipText=tooltipText)
        self.componentsTableEnergy.setSelectionBehavior(QTableWidget.SelectRows)  # Row selection
        self.componentsTableEnergy.setSelectionMode(QTableWidget.SingleSelection)  # Single row at a time
        self.componentsTableEnergy.setObjectName("componentsTableEnergy")

        # Add a row to tabel button
        self.addRowButtonEnergy = QPushButton("Add Component", self)
        self.addRowButtonEnergy.clicked.connect(self._addRowToTable)
        # set object name
        self.addRowButtonEnergy.setObjectName("addRowButtonEnergy")
        layout.addWidget(self.addRowButtonEnergy)
        # Initialize the table with an example row (optional)
        self._addRowToTable(tabName="energy")

        # ----------------------------------------------------------------------------------------------------------
        # Chilling Requirements
        self._createSectionTitle(text="Chilling Requierments", layout=layout)
        # ----------------------------------------------------------------------------------------------------------

        # Reference Flow type Chilling
        self.referenceFlowTypeChilling = createReferenceFlowTypeComboBox("referenceFlowTypeChilling")
        tooltipText = """The reference flow type is the type of flow that is used to calculate the Energy Consumption of
                            the unit process."""
        self._addRowWithTooltip(layout, labelText="Reference Flow Type:", widget=self.referenceFlowTypeChilling,
                                tooltipText=tooltipText)
        self.referenceFlowTypeChilling.currentIndexChanged.connect(lambda: self._componentSelectionSwitch(type="Chilling"))

        # Chilling Consumption parameter
        self.chillingConsumption = QLineEdit(self)
        self.chillingConsumption.setText("0.00")
        # only double values are allowed
        self.chillingConsumption.setValidator(QDoubleValidator(0.00, 999999.99, 2))
        self.chillingConsumption.setObjectName("chillingConsumption")
        tooltipText = """The chilling consumption of the unit process."""
        # add a label to the chilling consumption units
        self.chillingConsumptionUnit = QLabel(self)
        self.chillingConsumptionUnit.setText("MWh/t")  # Replace "Your Start Value" with the value you want to set
        self.chillingConsumptionUnit.setFixedWidth(120)  # make the lable bigger in width
        self.chillingConsumptionUnit.setFont(self.subtitleFont)  # make it bold
        # combine the chilling consumption and the unit in a horizontal layout
        hlayout = QHBoxLayout()
        hlayout.addWidget(self.chillingConsumption)
        hlayout.addWidget(self.chillingConsumptionUnit)
        # add the chilling consumption to the layout
        self._addRowWithTooltip(layout, labelText="Chilling Consumption:", widget=hlayout, tooltipText=tooltipText)

        # Components table
        self.componentsTableChilling = QTableWidget(0, 1, self)  # Initial rows, columns
        self.componentsTableChilling.setHorizontalHeaderLabels(["Component Name"])
        self.componentsTableChilling.setColumnWidth(0, 200)  # make column 1 wider
        #  add the tabel to the widget
        tooltipText = """The chemicals species selected are the ones that are used to calculate the chilling consumption of
                                the unit process based on the mass flow (e.g., E_consumption (MW) = F_in (t/h) * Tau (MWh/t) )."""
        self._addRowWithTooltip(layout, labelText="Components:", widget=self.componentsTableChilling, # add same table to the layout
                                tooltipText=tooltipText)
        self.componentsTableChilling.setSelectionBehavior(QTableWidget.SelectRows)  # Row selection
        self.componentsTableChilling.setSelectionMode(QTableWidget.SingleSelection)  # Single row at a time
        self.componentsTableChilling.setObjectName("componentsTableChilling")

        # Add a row to tabel button
        self.addRowButtonChilling = QPushButton("Add Component", self)
        self.addRowButtonChilling.clicked.connect(self._addRowToTable)
        # set object name
        self.addRowButtonChilling.setObjectName("addRowButtonChilling")
        layout.addWidget(self.addRowButtonChilling)
        # Initialize the table with an example row (optional)
        self._addRowToTable(tabName="chilling")


        # internal method to create the layout of

        # set layout in the widget
        widget.setLayout(layout)
        return widget

    def _createHeatingConsumptionTab(self):
        """
        Creates and returns a QWidget containing UI elements for configuring heating/cooling requirements.
        """

        def createReferenceFlowTypeComboBox(name):
            """
            Creates a QComboBox with predefined items for selecting reference flow types.

            Args:
            - name (str): Object name for the QComboBox.

            Returns:
            - QComboBox: Initialized QComboBox object.
            """
            comboBox = QComboBox(self)
            comboBox.addItems([
                "Entering mass Flow", "Exiting mass Flow",
                "Entering Molar Flow", "Exiting Molar Flow",
                "Entering Flow Cp", "Exiting Flow Cp"
            ])
            comboBox.setObjectName(name)
            return comboBox

        # Energy Consumption Tab
        widget = QWidget()
        layout = QFormLayout()

        # -------------------------------------------------------------------------------------------------
        # Heat Consumption 1
        self._createSectionTitle(text="Heating/cooling Requirements", layout=layout)
        # -------------------------------------------------------------------------------------------------

        # Reference Flow Type Heat1
        self.referenceFlowTypeHeat1 = createReferenceFlowTypeComboBox("referenceFlowTypeHeat1")
        tooltipText = """The reference flow type is the type of flow that is used to calculate the Heat Consumption of
                         the unit process."""
        self._addRowWithTooltip(layout, labelText="Reference Flow Type:", widget=self.referenceFlowTypeHeat1,
                                tooltipText=tooltipText)
        self.referenceFlowTypeHeat1.currentIndexChanged.connect(lambda: self._componentSelectionSwitch(type="Heat1"))

        # Heat consumption 1
        self.heatConsumption = QLineEdit(self)
        self.heatConsumption.setText("0.00")
        self.heatConsumption.setValidator(QDoubleValidator(0.00, 999999.99, 2))
        self.heatConsumption.setObjectName("heatConsumption")
        tooltipText = """The cooling (Negative) or heating (Positive) required for the unit process."""
        self.heatConsumptionUnit = QLabel(self)
        self.heatConsumptionUnit.setText("MWh/t")
        self.heatConsumptionUnit.setFixedWidth(120)
        self.heatConsumptionUnit.setFont(self.subtitleFont)
        hlayout = QHBoxLayout()
        hlayout.addWidget(self.heatConsumption)
        hlayout.addWidget(self.heatConsumptionUnit)
        self._addRowWithTooltip(layout, labelText="Required Cooling/Heating:", widget=hlayout, tooltipText=tooltipText)

        # Components table Heat1
        self.componentsTableHeat1 = QTableWidget(0, 1, self)
        self.componentsTableHeat1.setHorizontalHeaderLabels(["Component Name"])
        self.componentsTableHeat1.setColumnWidth(0, 200)
        tooltipText = """The chemical species selected are used to calculate the heat consumption of
                         the unit process based on the mass flow (e.g., E_consumption (MW) = F_in (t/h) * Tau (MWh/t))."""
        self._addRowWithTooltip(layout, labelText="Components:", widget=self.componentsTableHeat1,
                                tooltipText=tooltipText)
        self.componentsTableHeat1.setSelectionBehavior(QTableWidget.SelectRows)
        self.componentsTableHeat1.setSelectionMode(QTableWidget.SingleSelection)
        self.componentsTableHeat1.setObjectName("componentsTableHeat1")

        # Add row button Heat1
        self.addRowButtonHeat1 = QPushButton("Add Component", self)
        self.addRowButtonHeat1.clicked.connect(self._addRowToTable)
        self.addRowButtonHeat1.setObjectName("addRowButtonHeat1")
        layout.addWidget(self.addRowButtonHeat1)

        # Initialize the table with an example row (optional)
        self._addRowToTable(tabName="heat1")

        # -------------------------------------------------------------------------------------------------
        # Heat Consumption 2
        self._createSectionTitle(text="Heating/cooling Requirements (2)", layout=layout)
        # -------------------------------------------------------------------------------------------------

        # Reference Flow Type Heat2
        self.referenceFlowTypeHeat2 = createReferenceFlowTypeComboBox("referenceFlowTypeHeat2")
        tooltipText = """The reference flow type is the type of flow that is used to calculate the Heat Consumption of
                         the unit process."""
        self._addRowWithTooltip(layout, labelText="Reference Flow Type:", widget=self.referenceFlowTypeHeat2,
                                tooltipText=tooltipText)
        self.referenceFlowTypeHeat2.currentIndexChanged.connect(lambda: self._componentSelectionSwitch(type="Heat2"))

        # Heat consumption 2
        self.heatConsumption2 = QLineEdit(self)
        self.heatConsumption2.setText("0.00")
        self.heatConsumption2.setValidator(QDoubleValidator(0.00, 999999.99, 2))
        self.heatConsumption2.setObjectName("heatConsumption2")
        tooltipText = """The second cooling (Negative) or heating (Positive) required for the unit process."""
        self.heatConsumption2Unit = QLabel(self)
        self.heatConsumption2Unit.setText("MWh/t")
        self.heatConsumption2Unit.setFixedWidth(120)
        self.heatConsumption2Unit.setFont(self.subtitleFont)
        hlayout = QHBoxLayout()
        hlayout.addWidget(self.heatConsumption2)
        hlayout.addWidget(self.heatConsumption2Unit)
        self._addRowWithTooltip(layout, labelText="Required Cooling/Heating:", widget=hlayout, tooltipText=tooltipText)

        # Components table Heat2
        self.componentsTableHeat2 = QTableWidget(0, 1, self)
        self.componentsTableHeat2.setHorizontalHeaderLabels(["Component Name"])
        self.componentsTableHeat2.setColumnWidth(0, 200)
        tooltipText = """The chemical species selected are used to calculate the heat consumption of
                         the unit process based on the mass flow (e.g., E_consumption (MW) = F_in (t/h) * Tau (MWh/t))."""
        self._addRowWithTooltip(layout, labelText="Components:", widget=self.componentsTableHeat2,
                                tooltipText=tooltipText)
        self.componentsTableHeat2.setSelectionBehavior(QTableWidget.SelectRows)
        self.componentsTableHeat2.setSelectionMode(QTableWidget.SingleSelection)
        self.componentsTableHeat2.setObjectName("componentsTableHeat2")

        # Add row button Heat2
        self.addRowButtonHeat2 = QPushButton("Add Component", self)
        self.addRowButtonHeat2.clicked.connect(self._addRowToTable)
        self.addRowButtonHeat2.setObjectName("addRowButtonHeat2")
        layout.addWidget(self.addRowButtonHeat2)

        # Initialize the table with an example row (optional)
        self._addRowToTable(tabName="heat2")

        # Set layout in the widget
        widget.setLayout(layout)
        return widget

    def _createConcentrationTab(self):
        """
        Creates and returns a QWidget containing UI elements for configuring concentration factors.
        """

        def createReferenceFlowTypeComboBox(name):
            """
            Creates a QComboBox with predefined items for selecting reference flow types.

            Args:
            - name (str): Object name for the QComboBox.

            Returns:
            - QComboBox: Initialized QComboBox object.
            """
            comboBox = QComboBox(self)
            comboBox.addItems([
                "Entering mass Flow (F_IN)",
                "Exiting mass Flow (F_OUT)",
            ])
            comboBox.setObjectName(name)
            return comboBox

        # initialise widget
        widget = QWidget()
        layout = QFormLayout()

        # Create a title for the tab
        self._createSectionTitle(text="Concentration Factors", layout=layout)

        # create me a text box where I can explain what this tab does
        self.concentrationFactorDescription = QLabel(self)
        self.concentrationFactorDescription.setText("The concentration factor is the ratio of the mass of FLOW1 to "
                                                    "the mass of FLOW2: \n Concentration Factor = FLOW1 / FLOW2")
        layout.addRow(self.concentrationFactorDescription)


        self.concentrationFactor = QLineEdit(self)
        self.concentrationFactor.setText("0.00")
        self.concentrationFactor.setValidator(QDoubleValidator(0.00, 999999.99, 2))
        self.concentrationFactor.setObjectName("concentrationFactor")
        tooltipText = """ The concentration factor is the ratio of the mass of FLOW1 to the mass of FLOW2,
                        specified underneath."""
        self._addRowWithTooltip(layout, labelText="Concentration Factor:", widget=self.concentrationFactor,
                                tooltipText=tooltipText)

        # creat subtitel
        self._createSectionTitle(text="Reference Flow 1", layout=layout)
        # Create drop down menu for the reference flow1
        self.referenceFlow1Concentration = createReferenceFlowTypeComboBox("referenceFlow1Concentration")
        tooltipText = """The reference flow type is the type of flow that is used to calculate the concentration of
                        the unit process."""
        self._addRowWithTooltip(layout, labelText="Reference Flow Type:", widget=self.referenceFlow1Concentration,
                                tooltipText=tooltipText)
        # create table for the components
        self.componentsTableConcentration1 = QTableWidget(0, 1, self)  # Initial rows, columns
        self.componentsTableConcentration1.setHorizontalHeaderLabels(["Component Name"])
        self.componentsTableConcentration1.setColumnWidth(0, 200)  # make column 1 wider
        #  add the tabel to the widget
        tooltipText = """The chemicals species selected for flow1, sum(species) = FLOW1."""
        self._addRowWithTooltip(layout, labelText="Components:", widget=self.componentsTableConcentration1, # add same table to the layout
                                tooltipText=tooltipText)
        self.componentsTableConcentration1.setSelectionBehavior(QTableWidget.SelectRows)  # Row selection
        self.componentsTableConcentration1.setSelectionMode(QTableWidget.SingleSelection)  # Single row at a time
        self.componentsTableConcentration1.setObjectName("componentsTableConcentration1")

        # Add a row to tabel button
        self.addRowButtonConcentration1 = QPushButton("Add Component", self)
        self.addRowButtonConcentration1.clicked.connect(self._addRowToTable)
        # set object name
        self.addRowButtonConcentration1.setObjectName("addRowButtonConcentration1")
        layout.addWidget(self.addRowButtonConcentration1)
        # Initialize the table with an example row (optional)
        self._addRowToTable(tabName="concentration1")

        # creat subtitel flow2
        self._createSectionTitle(text="Reference Flow 2", layout=layout)
        # Create drop down menu for the reference flow2
        self.referenceFlow2Concentration = createReferenceFlowTypeComboBox("referenceFlow2Concentration")
        tooltipText = """The reference flow type is the type of flow that is used to calculate the concentration of
                        the unit process."""
        self._addRowWithTooltip(layout, labelText="Reference Flow Type:", widget=self.referenceFlow2Concentration,
                                tooltipText=tooltipText)
        # create table for the components
        self.componentsTableConcentration2 = QTableWidget(0, 1, self)  # Initial rows, columns
        self.componentsTableConcentration2.setHorizontalHeaderLabels(["Component Name"])
        self.componentsTableConcentration2.setColumnWidth(0, 200)  # make column 1 wider
        #  add the tabel to the widget
        tooltipText = """The chemicals species selected for flow2, sum(species) = FLOW2."""
        self._addRowWithTooltip(layout, labelText="Components:", widget=self.componentsTableConcentration2, # add same table to the layout
                                tooltipText=tooltipText)
        self.componentsTableConcentration2.setSelectionBehavior(QTableWidget.SelectRows)  # Row selection
        self.componentsTableConcentration2.setSelectionMode(QTableWidget.SingleSelection)  # Single row at a time
        self.componentsTableConcentration2.setObjectName("componentsTableConcentration2")

        # add row button
        self.addRowButtonConcentration2 = QPushButton("Add Component", self)
        self.addRowButtonConcentration2.clicked.connect(self._addRowToTable)
        # set object name
        self.addRowButtonConcentration2.setObjectName("addRowButtonConcentration2")
        layout.addWidget(self.addRowButtonConcentration2)
        # Initialize the table with an example row (optional)
        self._addRowToTable(tabName="concentration2")


        # return the widget
        widget.setLayout(layout)
        return widget

    # -----------------------------------------------------------------
    # methods for tool-tips,
    # -----------------------------------------------------------------
    def _addRowWithTooltip(self, layout, labelText, widget, tooltipText, widget2=None):
        label = QLabel(f'{labelText} <a href="#">(i)</a>')
        label.setToolTip(tooltipText)
        label.linkActivated.connect(self._showTooltip)
        layout.addRow(label, widget)

    def _showTooltip(self, _):
        QToolTip.setFont(QFont('SansSerif', 10))
        QToolTip.showText(QCursor.pos(), self.sender().toolTip())

    def _createSectionTitle(self, text, color="#e1e1e1", centerAlign=False, layout=None):
        title = QLabel(text)
        title.setFont(self.subtitleFont)
        title.setStyleSheet(f"background-color: {color}; padding: 3px;")
        if centerAlign:
            title.setAlignment(Qt.AlignCenter)
        frame = QFrame()
        frame.setFrameShape(QFrame.HLine)
        frame.setFrameShadow(QFrame.Sunken)
        layout.addRow(title)
        layout.addRow(frame)
    # -----------------------------------------------------------------
    # Methods for the components table
    # -----------------------------------------------------------------

    def _addRowToTable(self, tabName:str=''):

        try:
            senderName = self.sender().objectName()
        except AttributeError:
            senderName = None  # or any default value indicating the objectName is not accessible

        # check what button is clicked
        if tabName == "cost" or senderName == "addRowButton":
            #print('the add row button is clicked')
            table = self.componentsTable
        elif tabName == "energy" or senderName == "addRowButtonEnergy":
            #print('the add row button energy is clicked')
            table = self.componentsTableEnergy
        elif tabName == "heat1" or senderName == "addRowButtonHeat1":
            #print('the add row button heat1 is clicked')
            table = self.componentsTableHeat1
        elif tabName == "heat2" or senderName == "addRowButtonHeat2":
            #print('the add row button heat2 is clicked')
            table = self.componentsTableHeat2
        elif tabName == "chilling" or senderName == "addRowButtonChilling":
            #print('the add row button chilling is clicked')
            table = self.componentsTableChilling
        elif tabName == "concentration1" or senderName == "addRowButtonConcentration1":
            #print('the add row button concentration1 is clicked')
            table = self.componentsTableConcentration1

        elif tabName == "concentration2" or senderName == "addRowButtonConcentration2":
            #print('the add row button concentration2 is clicked')
            table = self.componentsTableConcentration2

        else:
            raise ValueError("The add row button is not connected to any table please check the "
                             "object name of the button")

        # Get the current row count and insert a new row at the end
        rowPosition = table.rowCount()
        table.insertRow(rowPosition)

        # Create new cells by creating a combo box instance
        self.comboBoxComponents = NonFocusableComboBox()
        chemicalNames = self.centralDataManager.getChemicalComponentNames()
        self.comboBoxComponents.addItems(chemicalNames)
        self.comboBoxComponents.setObjectName(f"comboBoxComponents_{rowPosition}")

        item = QTableWidgetItem('hack') # adding this item is a bit of a hack otherwise the row can't be selected and deleted
        table.setItem(rowPosition, 0, item)
        table.setCellWidget(rowPosition, 0, self.comboBoxComponents)

        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setSelectionMode(QTableWidget.SingleSelection)  # or MultiSelection if needed


    def _componentSelectionSwitch(self, type):
        """ Only fill in the component and product load if the reference flow type is mass flow"""
        if type == "Cost":
            if self.referenceFlowType.currentText() == "Exiting Flow" or self.referenceFlowType.currentText() == "Entering Flow":
                # If a mass flow is selected, make the button to add components clickable
                self.referenceFlowUnit.setText("t/h")
                self.componentsTable.setDisabled(False)
                self.addRowButton.setDisabled(False)
                self.addRowButton.setStyleSheet("""
                                QPushButton {
                                    background-color: #5a9;
                                }
                                QPushButton:hover {
                                    background-color: #78d;
                                }
                            """)

            else:
                # If a mass flow is not selected, make the button to add components unclickable
                self.componentsTable.setDisabled(True)
                self.addRowButton.setDisabled(True)
                self.addRowButton.setStyleSheet("""
                    QPushButton {
                        background-color: grey;
                    }
                """)

                self.referenceFlowUnit.setText("MWh")

        elif type == "Electricity":
            if self.referenceFlowTypeEnergy.currentText() == 'Entering mass Flow' or self.referenceFlowTypeEnergy.currentText() == 'Exiting mass Flow':
                self.referenceFlowUnitEnergy.setText("MWh/t")
            elif self.referenceFlowTypeEnergy.currentText() == 'Entering Molar Flow' or self.referenceFlowTypeEnergy.currentText() == 'Exiting Molar Flow':
                self.referenceFlowUnitEnergy.setText("MWh/Mmol")
            else:
                self.referenceFlowUnitEnergy.setText("ΔT")

        elif type == "Heat1":
            if self.referenceFlowTypeHeat1.currentText() == 'Entering mass Flow' or self.referenceFlowTypeHeat1.currentText() == 'Exiting mass Flow':
                self.heatConsumptionUnit.setText("MWh/t")
            elif self.referenceFlowTypeHeat1.currentText() == 'Entering Molar Flow' or self.referenceFlowTypeHeat1.currentText() == 'Exiting Molar Flow':
                self.heatConsumptionUnit.setText("MWh/Mmol")
            else:
                self.heatConsumptionUnit.setText("ΔT")

        elif type == "Heat2":
            if self.referenceFlowTypeHeat2.currentText() == 'Entering mass Flow' or self.referenceFlowTypeHeat2.currentText() == 'Exiting mass Flow':
                self.heatConsumption2Unit.setText("MWh/t")
            elif self.referenceFlowTypeHeat2.currentText() == 'Entering Molar Flow' or self.referenceFlowTypeHeat2.currentText() == 'Exiting Molar Flow':
                self.heatConsumption2Unit.setText("MWh/Mmol")
            else:
                self.heatConsumption2Unit.setText("ΔT")

        elif type == "Chilling":
            if self.referenceFlowTypeChilling.currentText() == 'Entering mass Flow' or self.referenceFlowTypeChilling.currentText() == 'Exiting mass Flow':
                self.chillingConsumptionUnit.setText("MWh/t")
            elif self.referenceFlowTypeChilling.currentText() == 'Entering Molar Flow' or self.referenceFlowTypeChilling.currentText() == 'Exiting Molar Flow':
                self.chillingConsumptionUnit.setText("MWh/Mmol")
            else:
                self.chillingConsumptionUnit.setText("ΔT")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Backspace:
            focused_widget = QApplication.focusWidget()

            if isinstance(focused_widget, QTableWidget):
                selectedItems = focused_widget.selectedItems()
                if selectedItems:
                    selectedRow = selectedItems[0].row()
                    focused_widget.removeRow(selectedRow)
        else:
            super().keyPressEvent(event)

    # -----------------------------------------------------------------
    # Methods for the data storage and retrieval
    # -----------------------------------------------------------------
    def collectData(self):
        data = {
            'Name': self.nameInput.text(),
            'Processing Group': self.processingGroupInput.text(),
            'Reference Flow': self.referenceFlowInput.text(),
            'Exponent': self.exponentInput.text()
            # placeholder for other fields...
        }
        return data

    def populateDialog(self, data):
        """
        Populate the dialog with the data provided in the dictionary retrived from the Central data manager.
        :param data:
        :return:
        """
        if 'Name' in data:
            self.nameInput.setText(data['Name'])
        if 'Processing Group' in data:
            self.processingGroupInput.setText(data['Processing Group'])
        if 'Reference Flow' in data:
            self.referenceFlowInput.setText(data['Reference Flow'])
        if 'Exponent' in data:
            self.exponentInput.setText(data['Exponent'])
        # placeholder for other fields...





class StoichiometricReactorDialog(PhysicalProcessesDialog):
    def __init__(self, initialData, centralDataManager):
        super().__init__(initialData, centralDataManager)  # Initialize the parent class
        # Additional initialization for StoichiometricReactorDialog

    # TODO complete this class and connect it to the main window

    # def __init__(self, initialData):
    #     super().__init__()
    #     # set style
    #     self.setStyleSheet("""
    #                                         QDialog {
    #                                             background-color: #f2f2f2;
    #                                         }
    #                                         QLabel {
    #                                             color: #333333;
    #                                         }
    #                                         QLineEdit {
    #                                             border: 1px solid #cccccc;
    #                                             border-radius: 2px;
    #                                             padding: 5px;
    #                                             background-color: #ffffff;
    #                                             selection-background-color: #b0daff;
    #                                         }
    #                                         QPushButton {
    #                                             color: #ffffff;
    #                                             background-color: #5a9;
    #                                             border-style: outset;
    #                                             border-width: 2px;
    #                                             border-radius: 10px;
    #                                             border-color: beige;
    #                                             font: bold 14px;
    #                                             padding: 6px;
    #                                         }
    #                                         QPushButton:hover {
    #                                             background-color: #78d;
    #                                         }
    #                                         QPushButton:pressed {
    #                                             background-color: #569;
    #                                             border-style: inset;
    #                                         }
    #                                         QTableWidget {
    #                                             border: 1px solid #cccccc;
    #                                             selection-background-color: #b0daff;
    #                                         }
    #                                     """)
    #
    #     self.setWindowTitle("Physical Processes Parameters")
    #     self.setGeometry(100, 100, 600, 400)  # Adjust size as needed
    #
    #     tabWidget = QTabWidget(self)
    #     tabWidget.addTab(self._createGeneralFactorsTab(), "General Factors")
    #     tabWidget.addTab(self._createCostRelatedFactorsTab(), "Cost Related Factors")
    #     tabWidget.addTab(self._createEnergyRelatedFactorsTab(), "Energy Related Factors")
    #     tabWidget.addTab(self._createSplitFactorsTab(), "Split Factors")
    #     tabWidget.addTab(self._createMaterialFlowSourcesTab(), "Material Flow Sources")
    #     tabWidget.addTab(self._createConcentrationFactorsTab(), "Concentration Factors")
    #
    #     layout = QVBoxLayout(self)
    #     layout.addWidget(tabWidget)
    #
    #     # OK and Cancel buttons
    #     buttonsLayout = QHBoxLayout()
    #     self.okButton = QPushButton("OK", self)
    #     self.okButton.clicked.connect(self.accept)
    #     buttonsLayout.addWidget(self.okButton)
    #
    #     self.cancelButton = QPushButton("Cancel", self)
    #     self.cancelButton.clicked.connect(self.reject)
    #     buttonsLayout.addWidget(self.cancelButton)
    #
    #     layout.addLayout(buttonsLayout)
    #
    # # Define the following methods to create tabs for each category
    # def _createGeneralFactorsTab(self):
    #     pass
    #     # Create and return the widget for General Factors
    #     # Add QLineEdit, QSpinBox, QDoubleSpinBox, etc. as needed
    #
    # def _createCostRelatedFactorsTab(self):
    #     # Create and return the widget for Cost Related Factors
    #     # Add QLineEdit, QSpinBox, QDoubleSpinBox, etc. as needed
    #     pass
    #
    # def _createEnergyRelatedFactorsTab(self):
    #     # Create and return the widget for Energy Related Factors
    #     # This will likely include a QTableWidget for the various energy types
    #     pass
    # def _createSplitFactorsTab(self):
    #     # Create and return the widget for Split Factors
    #     # This will likely include a QTableWidget for different target processes
    #     pass
    # def _createMaterialFlowSourcesTab(self):
    #     # Create and return the widget for Material Flow Sources
    #     # This will likely include a QTableWidget for the sources and targets
    #     pass
    # def _createConcentrationFactorsTab(self):
    #     # Create and return the widget for Concentration Factors
    #     # This will likely include a QTableWidget for flow concentration comparisons
    #     pass
    #     # Implement the above methods to create each specific tab.
    #     # The tabs will contain form fields and tables as per the provided Excel sheet.


# -----------------------------------------------------------------
# Custom Delegates and helper classes
# -----------------------------------------------------------------

class DoubleDelegate(QStyledItemDelegate):
    """
    A delegate class to handle double values in the QTableWidget. This class is used to display and edit double values in
    table widgets.
    """
    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        validator = QDoubleValidator(0.00, 999999.99, 2)
        editor.setValidator(validator)
        return editor

    def setEditorData(self, lineEdit, index):
        value = index.model().data(index, Qt.EditRole)
        lineEdit.setText(str(value))

    def setModelData(self, lineEdit, model, index):
        value = float(lineEdit.text())
        model.setData(index, value, Qt.EditRole)

class DropDownDelegate(QStyledItemDelegate):
    """
    A delegate class to handle drop-down lists in the QTableWidget. This class is used to display and edit drop-down lists
    in table widgets.
    """
    def __init__(self, items, parent=None):
        super().__init__(parent)
        self.items = ['1','2']

    def createEditor(self, parent, option, index):
        editor = QComboBox(parent)
        editor.addItems(self.items)
        return editor

    def setEditorData(self, comboBox, index):
        value = index.model().data(index, Qt.EditRole)
        comboBox.setCurrentText(value)

    def setModelData(self, comboBox, model, index):
        value = comboBox.currentText()
        model.setData(index, value, Qt.EditRole)

class NonFocusableComboBox(QComboBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure the combo box cannot gain focus
        self.setFocusPolicy(Qt.NoFocus)

    # def keyPressEvent(self, event):
    #     event.ignore()

class CustomTableWidget(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Backspace:
            selectedItems = self.selectedItems()
            if selectedItems:
                selectedRow = selectedItems[0].row()  # Get the row of the first selected item
                self.removeRow(selectedRow)
        else:
            super().keyPressEvent(event)

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
