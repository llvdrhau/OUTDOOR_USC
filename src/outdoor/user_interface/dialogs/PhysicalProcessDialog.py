import os
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel, QWidget, QTableWidget, QTabWidget, \
    QApplication, QHBoxLayout, QTableWidgetItem, QFormLayout, QComboBox, QFrame, QToolTip, QCheckBox, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDoubleValidator, QFont, QCursor, QIntValidator, QPixmap, QColor
from outdoor.user_interface.utils.NonFocusableComboBox import NonFocusableComboBox
from outdoor.user_interface.data.CentralDataManager import CentralDataManager
from outdoor.user_interface.data.ProcessDTO import ProcessDTO, ProcessType

class PhysicalProcessesDialog(QDialog):
    """
    Opens a dialog to set the physical processes parameters for the physical processes icon. The dialog allows the user to
    set the name, processing group, reference flow, and exponent. The user can set the reference flow and exponent as
    floating-point numbers. The processing group and name are text fields.
    """

    def __init__(self, initialData, centralDataManager:CentralDataManager, iconID):
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
        self.iconID = iconID
        self.UnitType = ProcessType.PHYSICAL
        self.dialogData = initialData.dialogData if initialData else {}

        self.setWindowTitle("Unit Process Parameters")
        self.setGeometry(100, 100, 600, 400)  # Adjust size as needed

        self.subtitleFont = QFont("Arial", 9, QFont.Bold)

        # initialize the separation error to be False
        self.separationErrorDict = {}

        tabWidget = QTabWidget(self)
        calc_types = self.centralDataManager.configs["calcConfigs"]
        tabWidget.addTab(self._createGeneralParametersTab(), "General Parameters")
        if calc_types['Cost'] == 'True':
            tabWidget.addTab(self._createAnnualCostsTab(), "Annualized Capital Costs")
            tabWidget.addTab(self._createCostRelatedFactorsTab(), "Cost Related Parameters")
        if calc_types['Utility Consumption'] == 'True':
            tabWidget.addTab(self._createUtilityConsumptionTab(), "Utility Consumption")
        if calc_types['Heating'] == 'True':
            tabWidget.addTab(self._createHeatingConsumptionTab(), "Heating Requirements")
        if calc_types['Concentration'] == 'True':
            tabWidget.addTab(self._createConcentrationTab(), "Concentration Factors")

        # todo, ask Mias to add this to the config file! I don't know how to do it
        # @ Mias, please add this to the config files
        # if calc_types['Separation'] == 'True':
        #     tabWidget.addTab(self._createSeparationEfficiencyTab(), "Separation Efficiency")

        # for now, I will add it manually to the dialog
        tabWidget.addTab(self._createSeparationEfficiencyTab(), "Separation Efficiency")

        if calc_types['LCA'] == 'True':
            tabWidget.addTab(self._createLcaDialogTab(), "LCA")
        # You can add more tabs as needed...

        # save the tabWidget as an attribute so it can be called in other class that inherit from this class
        self.tabWidget = tabWidget

        layout = QVBoxLayout(self)
        layout.addWidget(self.tabWidget)

        # OK and Cancel buttons
        buttonsLayout = QHBoxLayout()
        self.okButton = QPushButton("OK", self)
        self.okButton.clicked.connect(lambda: self.saveData(self.UnitType))
        buttonsLayout.addWidget(self.okButton)

        self.cancelButton = QPushButton("Cancel", self)
        self.cancelButton.clicked.connect(self.reject)
        buttonsLayout.addWidget(self.cancelButton)

        layout.addLayout(buttonsLayout)

        # populate the dialog with existing data (initialData) if it is not empty
        if initialData:
            self.populateDialog(dialogData=self.dialogData)

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
        self.fullLoadingHours.setObjectName("fullLoadingHours")  # set object name
        tooltipText = """The working hours per year of the unit process."""
        self._addRowWithTooltip(layout, labelText="Working Hours per Year:", widget=self.fullLoadingHours,
                                tooltipText=tooltipText)

        # CO2 Emissions for Building
        self.co2EmissionsBuilding = QLineEdit(self)
        self.co2EmissionsBuilding.setText("0.00")  # Replace "Your Start Value" with the value you want to set
        self.co2EmissionsBuilding.setObjectName("co2EmissionsBuilding")  # set object name
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
        self._addRowWithTooltip(layout, labelText="Temperature in (°C):", widget=self.temperatureEnteringProcess,
                                tooltipText=tooltipText)
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



        widget.setLayout(layout)

        return widget

    def _createAnnualCostsTab(self):

        # ---------------------------------------------------------------
        #  parameters Annualized Capital Costs
        # ---------------------------------------------------------------

        # General Factors Tab
        widget = QWidget()
        layout = QFormLayout()

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
        self.turnOverTime.setValidator(QDoubleValidator(0.00, 999.99, 2))
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
        tooltipText = """Percentage of the raw purchase equipment costs to pay for parts to replace."""  # Cu^(RE) in the thesis of Philpp
        self._addRowWithTooltip(layout, labelText="Turn Over Factor:", widget=self.turnOverFactor,
                                tooltipText=tooltipText)
        # only double values are allowed
        self.turnOverFactor.setValidator(QDoubleValidator(0.00, 1.00, 2))

        # add the layout to the widget and return the widget
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

        self._addRowWithTooltip(layout, labelText="Reference Flow Type:", widget=self.referenceFlowType,
                                tooltipText=tooltipText)
        # # Connect the signal to the slot function
        self.referenceFlowType.currentIndexChanged.connect(lambda: self._componentSelectionSwitch(type="Cost"))

        # Reference Flow input
        self.referenceFlowInput = QLineEdit(self)
        self.referenceFlowInput.setValidator(QDoubleValidator(0.00, 999999.99, 2))
        # set object name
        self.referenceFlowInput.setObjectName("referenceFlowInput")
        self.referenceFlowUnit = QLabel(self)
        self.referenceFlowUnit.setText("t/h")  # Replace "Your Start Value" with the value you want to set
        self.referenceFlowUnit.setFixedWidth(50)  # make the lable bigger in width
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
        tooltipText = """The chemicals species selected are the ones that are used to calculate the Equipment Costs of
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
        self._addRowWithTooltip(layout, labelText="Reference Cost (M€):", widget=self.referenceCost,
                                tooltipText=tooltipText)

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
        self.referenceFlowTypeEnergy.currentIndexChanged.connect(
            lambda: self._componentSelectionSwitch(type="Electricity"))

        # Electricity Consumption parameter
        self.energyConsumption = QLineEdit(self)
        self.energyConsumption.setText("0.00")
        self.energyConsumption.setValidator(QDoubleValidator(0.00, 999999.99, 2))
        self.energyConsumption.setObjectName("energyConsumption")
        tooltipText = """The energy consumption of the unit process."""
        # add a label to the energy consumption units
        self.referenceFlowUnitEnergy = QLabel(self)
        self.referenceFlowUnitEnergy.setText("MWh/t")  # Replace "Your Start Value" with the value you want to set
        self.referenceFlowUnitEnergy.setFixedWidth(120)  # make the lable bigger in width
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
        self._addRowWithTooltip(layout, labelText="Components:", widget=self.componentsTableEnergy,
                                # add same table to the layout
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
        self.referenceFlowTypeChilling.currentIndexChanged.connect(
            lambda: self._componentSelectionSwitch(type="Chilling"))

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
        self._addRowWithTooltip(layout, labelText="Components:", widget=self.componentsTableChilling,
                                # add same table to the layout
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
                                                    "the mass of FLOW2: "
                                                    "\n FLOW1 (t/h) = Concentration Factor (-) * FLOW2 (t/h) ")
        layout.addRow(self.concentrationFactorDescription)

        self.concentrationFactor = QLineEdit(self)
        self.concentrationFactor.setText("0.00")
        self.concentrationFactor.setValidator(QDoubleValidator(0.00, 999999.99, 2))
        self.concentrationFactor.setObjectName("concentrationFactor")
        tooltipText = """ The concentration factor is the ratio of the mass of FLOW1 to the mass of FLOW2,
                        specified underneath."""
        self._addRowWithTooltip(layout, labelText="Concentration Factor:", widget=self.concentrationFactor,
                                tooltipText=tooltipText)

        # create subtitel
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
        self._addRowWithTooltip(layout, labelText="Components:", widget=self.componentsTableConcentration1,
                                # add same table to the layout
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

        # create subtitel flow2
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
        self._addRowWithTooltip(layout, labelText="Components:", widget=self.componentsTableConcentration2,
                                # add same table to the layout
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

    def _createSeparationEfficiencyTab(self):
        """
        Creates and returns a QWidget containing UI elements for configuring separation efficiency.
        """

        # Create a QWidget
        widget = QWidget()
        main_layout = QFormLayout()

        # Create a title for the tab
        self._createSectionTitle(text="Separation Streams", layout=main_layout)

        # Create a description for the tab
        self.separationEfficiencyDescription = QLabel(self)
        textExplanation = ("This tab defines the fractions of chemicals that are separated into various streams.\n"
                           "The unit process can be divided into max 3 streams. The user can choose which stream to \n"
                           "activate using the check boxes. The streams outlet locations are indicated by the Figure.\n")
        self.separationEfficiencyDescription.setText(textExplanation)
        main_layout.addRow(self.separationEfficiencyDescription)

        # --- Create Figure ---
        self.separationEfficiencyFigure = QLabel(self)


        # --- Create Check Boxes ---
        # Define the font for the checkboxes to make the text larger
        checkbox_font = QFont()
        checkbox_font.setPointSize(12)  # Set the desired font size (e.g., 12)

        self.stream1CheckBox = QCheckBox("Stream 1")
        self.stream1CheckBox.setFont(checkbox_font)  # Set font for larger text

        self.stream2CheckBox = QCheckBox("Stream 2")
        self.stream2CheckBox.setFont(checkbox_font)  # Set font for larger text

        self.stream3CheckBox = QCheckBox("Stream 3")
        self.stream3CheckBox.setFont(checkbox_font)  # Set font for larger text

        # Make check box 1 checked by default and immutable
        self.stream1CheckBox.setChecked(True)
        self.stream1CheckBox.setEnabled(False)
        # Make check box 2 and 3 unchecked by default and mutable
        self.stream2CheckBox.setChecked(False)
        self.stream2CheckBox.setEnabled(True)
        self.stream3CheckBox.setChecked(False)
        self.stream3CheckBox.setEnabled(True)

        self._updateFigure()  # # Set the default figure based on the default checkbox state

        # Connect checkboxes to functions to update the figure and table columns
        self.stream2CheckBox.stateChanged.connect(self._updateFigure)
        self.stream3CheckBox.stateChanged.connect(self._updateFigure)
        self.stream2CheckBox.stateChanged.connect(self._updateTableColumns)
        self.stream3CheckBox.stateChanged.connect(self._updateTableColumns)

        # --- Create Layouts to Arrange Figure and Check Boxes ---
        # Create a vertical layout for check boxes (on the left)
        checkboxes_layout = QVBoxLayout()
        checkboxes_layout.addWidget(self.stream1CheckBox)
        checkboxes_layout.addWidget(self.stream2CheckBox)
        checkboxes_layout.addWidget(self.stream3CheckBox)
        checkboxes_layout.setAlignment(Qt.AlignTop)  # Align checkboxes at the top

        # Create a vertical layout for the figure (on the right)
        figure_layout = QVBoxLayout()
        figure_layout.addWidget(self.separationEfficiencyFigure)
        figure_layout.setAlignment(Qt.AlignCenter)  # Center the figure vertically

        # Create a horizontal layout to contain checkboxes on the left and figure on the right
        figure_and_checkboxes_layout = QHBoxLayout()
        figure_and_checkboxes_layout.addLayout(checkboxes_layout)  # Add the checkboxes layout
        figure_and_checkboxes_layout.addSpacing(20)  # Add some space between the checkboxes and figure
        figure_and_checkboxes_layout.addLayout(figure_layout)  # Add the figure layout

        # Add the combined layout to the main layout
        main_layout.addRow(figure_and_checkboxes_layout)

        # --- Separation Fractions Section ---
        # Create a title for the separation fractions table
        self._createSectionTitle(text="Separation Fractions", layout=main_layout)

        # Add a table to the layout for separation efficiency
        self.separationEfficiencyTable = QTableWidget(0, 5, self)  # Initial rows, columns
        self.separationEfficiencyTable.setHorizontalHeaderLabels(
            ["Component Name", "Stream 1", "Stream 2", "Stream 3", "Waste"])

        # Set the column width for the first column
        self.separationEfficiencyTable.setColumnWidth(0, 200)  # make column 1 wider

        # make the table selectable under the name componentsTableSeparationEfficiency
        self.separationEfficiencyTable.setObjectName("componentsTableSeparationEfficiency")

        #  add the tabel to the widget
        main_layout.addRow(self.separationEfficiencyTable)

        # update the table columns based on the checkbox state
        self._updateTableColumns()

        # add row button
        self.addRowButtonSeparation = QPushButton("Add Component", self)
        self.addRowButtonSeparation.clicked.connect(self._addRowToTable)
        # set object name
        self.addRowButtonSeparation.setObjectName("addRowButtonSeparation")
        main_layout.addWidget(self.addRowButtonSeparation)
        # Initialize the table with an example row (optional)
        self._addRowToTable(tabName="separationEfficiency")


        # --- Waste Management Section ---
        # Create a title for the waste management section
        self._createSectionTitle(text="Waste Management", layout=main_layout)

        # Add a combo box for the waste management
        self.wasteManagement = QComboBox(self)
        self.wasteManagement.addItems(["Incineration", "Landfill", "WWTP"])
        tooltipText = """The waste management method used for the waste stream.\n
                Incineration: The waste is burned in an incinerator.\n
                Landfill: The waste is disposed of in a landfill.\n
                WWTP: The waste is treated in a wastewater treatment plant."""

        self._addRowWithTooltip(main_layout, labelText="Waste Management:", widget=self.wasteManagement,
                                tooltipText=tooltipText)

        # Set the layout for the widget
        widget.setLayout(main_layout)

        # Return the widget
        return widget

    # -----------------------------------------------------------------
    # methods for separation efficiency tab
    # -----------------------------------------------------------------

    def _updateFigure(self):
        """
        Updates the figure based on which checkboxes are checked.
        """

        # Get the directory of the current script
        base_dir = os.path.dirname(os.path.abspath(__file__))

        # Determine the image to load based on checked streams
        if self.stream1CheckBox.isChecked() and self.stream2CheckBox.isChecked() and self.stream3CheckBox.isChecked():
            figure_filename = "figure_stream_1_2_3.png"
        elif self.stream1CheckBox.isChecked() and self.stream2CheckBox.isChecked():
            figure_filename = "figure_stream_1_2.png"
        elif self.stream1CheckBox.isChecked() and self.stream3CheckBox.isChecked():
            figure_filename = "figure_stream_1_3.png"
        else:
            figure_filename = "figure_stream_1.png"  # Default figure when only stream 1 is active

        # Construct the full path to the figure using relative path
        pathFigure = os.path.join(base_dir, "figures", figure_filename)

        # Load the figure using QPixmap and add it to the QLabel
        pixmap = QPixmap(pathFigure)
        if pixmap.isNull():
            self.separationEfficiencyFigure.setText("Figure not found: " + pathFigure)
        else:
            smaller_pixmap = pixmap.scaled(225, 225, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.separationEfficiencyFigure.setPixmap(smaller_pixmap)

    def _updateTableColumns(self):
        """
        Updates the editability of columns Stream 2 and Stream 3 based on checkbox state.
        """
        # Update Stream 2 column
        for row in range(self.separationEfficiencyTable.rowCount()):
            item = self.separationEfficiencyTable.cellWidget(row, 2)  # Stream 2 column
            if not item:
                item = QTableWidgetItem()
                self.separationEfficiencyTable.setItem(row, 2, item)
            if self.stream2CheckBox.isChecked():
                item.setReadOnly(False)
                # make the cell white if it is editable
                item.setStyleSheet("background-color: rgb(255, 255, 255);")
            else:
                item.setReadOnly(True)
                item.setText("0") # set the value to 0
                # make the cell grayed out
                item.setStyleSheet("background-color: rgb(192, 192, 192);")



        # Update Stream 3 column
        for row in range(self.separationEfficiencyTable.rowCount()):
            item = self.separationEfficiencyTable.cellWidget(row, 3)  # Stream 3 column
            if not item:
                item = QTableWidgetItem()
                self.separationEfficiencyTable.setItem(row, 3, item)
            if self.stream3CheckBox.isChecked():
                item.setReadOnly(False)
                # make the cell white
                item.setStyleSheet("background-color: rgb(255, 255, 255);")
            else:
                item.setReadOnly(True)
                # set the value to 0
                item.setText("0")
                # make the cell grayed out
                item.setStyleSheet("background-color: rgb(192, 192, 192);")

    def _updateWasteFraction(self, row):
        """
        Updates the editability of columns Waste based on the waste management method.
        """
        # Update Waste column

        #WasteEditLine = self.separationEfficiencyTable.cellWidget(row, 4)  # Waste column
        #item = self._getCellValue(self.separationEfficiencyTable, row, 4)

        stream1 = self._getCellValue(self.separationEfficiencyTable, row, 1)
        stream2 = self._getCellValue(self.separationEfficiencyTable, row, 2)
        stream3 = self._getCellValue(self.separationEfficiencyTable, row, 3)

        wasteFraction = round(1 - stream1 - stream2 - stream3, 3)
        if wasteFraction < 0:
            # text should be red
            insert = QTableWidgetItem(str(wasteFraction))
            # set the background color to light red
            insert.setBackground(QColor(255, 0, 0))
            self.separationEfficiencyTable.setItem(row, 4, insert)
            self.separationErrorDict[row] = True

        else:
            # set the text of the waste edit line to the waste fraction
            self.separationEfficiencyTable.setItem(row, 4, QTableWidgetItem(str(wasteFraction)))
            self.separationErrorDict[row] = False

    def _getCellValue(self, table, row, column):
        """
        Gets the value of the QLineEdit in the given cell, or returns 0 if it doesn't exist.

        Args:
        - row (int): The row index of the cell.
        - column (int): The column index of the cell.

        Returns:
        - float: The value in the QLineEdit, or 0 if no value exists.
        """
        # Access the QLineEdit widget in the given cell
        cell_widget = table.cellWidget(row, column)

        if isinstance(cell_widget, QLineEdit):
            try:
                # Convert the text to a float value
                if cell_widget.text() == "":
                    value = 0.0
                else:
                    value = float(cell_widget.text())
            except ValueError:
                # If the text is not a valid number, return 0
                #logging.warning(f"Invalid value in cell ({row}, {column}) of the table Fractions for Icon {self.nameInput}.")
                # yellow color warning
                print("\033[93m" + f"Invalid value in cell ({row}, {column}) of the table Fractions for Icon {self.nameInput}.")
                value = 0.0
        else:
            # If the cell is not a QLineEdit, return 0
            value = 0.0

        return value


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

    def _addRowToTable(self, tabName: str = '', componentName= None):

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

        elif tabName == "reactantsTable" or senderName == "addRowButtonReactantsTable":
            table = self.reactantsTable

        elif tabName == "productsTable" or senderName == "addRowButtonProductsTable":
            table = self.productsTable

        elif tabName == "yield" or senderName == "addRowButtonYieldTable":
            table = self.inertComponentsTable

        elif tabName == "separationEfficiency" or senderName == "addRowButtonSeparation":
            table = self.separationEfficiencyTable


        else:
            raise ValueError("The add row button is not connected to any table please check the "
                             "object name of the button")

        # Get the current row count and insert a new row at the end
        rowPosition = table.rowCount()
        table.insertRow(rowPosition)

        # add restrictions to the Reactants table so stoichiometric and conversion factors are only between 0 and 1
        if tabName == "separationEfficiency" or senderName == "addRowButtonSeparation":
            # Add QTableWidgetItems for columns
            table.setItem(rowPosition, 2, QTableWidgetItem(""))
            table.setItem(rowPosition, 3, QTableWidgetItem(""))

            # make the last column read only
            item = QTableWidgetItem()
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            table.setItem(rowPosition, 4, item)

            # Add QLineEdit with QDoubleValidator for "Stoichiometric" and "Conversion Factor" columns
            for columnIndex in [1, 2, 3]:  # Columns stream 1, stream 2, stream 3
                lineEdit = QLineEdit()
                validator = QDoubleValidator(0.0, 1.0, 3)  # Values between 0 and 1, up to 5 decimal places
                validator.setNotation(QDoubleValidator.StandardNotation)
                lineEdit.setValidator(validator)
                table.setCellWidget(rowPosition, columnIndex, lineEdit)
                lineEdit.textChanged.connect(lambda _, r=rowPosition: self._updateWasteFraction(r))
                self.separationErrorDict[rowPosition] = False

            # update the table columns based on the checkbox state
            self._updateTableColumns()


        self.comboBoxComponents = NonFocusableComboBox()
        chemicalNames = self.centralDataManager.getChemicalComponentNames()
        self.comboBoxComponents.addItems(chemicalNames)
        self.comboBoxComponents.setObjectName(f"comboBoxComponents_{rowPosition}")

        item = QTableWidgetItem(
            'hack')  # adding this item is a bit of a hack otherwise the row can't be selected and deleted
        table.setItem(rowPosition, 0, item)
        table.setCellWidget(rowPosition, 0, self.comboBoxComponents)

        if componentName and componentName in chemicalNames:
            self.comboBoxComponents.setCurrentText(componentName)

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
        if event.key() == Qt.Key_Backspace or event.key() == Qt.Key_Delete:
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
            # General data
            'Type':     'Physical Process',
            'Name':     self.nameInput.text(),
            'Processing Group':                 self._getWidgetData(self.processingGroupInput, "int"),
            'Life Time Unit Process':           self._getWidgetData(self.lifeTimeUnitProcess, "float"),
            'Working Time Unit Process':        self._getWidgetData(self.fullLoadingHours, "float"),
            'CO2 Building':                     self._getWidgetData(self.co2EmissionsBuilding, "float"),
            'TemperatureIn1':                   self._getWidgetData(self.temperatureEnteringProcess, "float"),
            'TemperatureOut1':                  self._getWidgetData(self.temperatureLeavingProcess, "float"),
            'TemperatureIn2':                   self._getWidgetData(self.temperatureEnteringUnitProcess2, "float"),
            'TemperatureOut2':                  self._getWidgetData(self.temperatureLeavingUnitProcess2, "float"),
            'Operating Hours':                  self._getWidgetData(self.operatingAndMaintenanceCost, "float"),
            'Direct Cost Factor':               self._getWidgetData(self.directCostFactor, "float"),
            'Indirect Cost Factor':             self._getWidgetData(self.indirectCostFactor, "float"),

            # Reoccurring Annualized Capital Costs
            'Reoccurring Cost Factor':                self._getWidgetData(self.turnOverFactor, "float"),
            'Turn Over Time':                         self._getWidgetData(self.turnOverTime, "float"),
            'Turn Over Unit':                         self._getWidgetData(self.comboBoxUnits, "str"),

            # Cost data
            'Reference Flow Type':              self._getWidgetData(self.referenceFlowType, "str"),
            'Reference Flow Equipment Cost':    self._getWidgetData(self.referenceFlowInput, "float"),
            'Exponent':                         self._getWidgetData(self.exponentInput, "float"),
            'Components Equipment Costs':       self._collectTableData(self.componentsTable),
            'Reference Cost Unit':              self._getWidgetData(self.referenceCost, "float"),
            'Reference Year':                   self._getWidgetData(self.referenceYear, "int"),

            # Utility Consumption data
            'Reference Flow Type Energy':       self._getWidgetData(self.referenceFlowTypeEnergy, "str"),
            'Energy Consumption':               self._getWidgetData(self.energyConsumption, "float"),
            'Components Energy Consumption':    self._collectTableData(self.componentsTableEnergy),
            'Reference Flow Type Chilling':     self._getWidgetData(self.referenceFlowTypeChilling, "str"),
            'Chilling Consumption':             self._getWidgetData(self.chillingConsumption, "float"),
            'Components Chilling Consumption':  self._collectTableData(self.componentsTableChilling),

            # Heat Consumption data
            'Reference Flow Type Heat1':        self._getWidgetData(self.referenceFlowTypeHeat1, "str"),
            'Heat Consumption 1':               self._getWidgetData(self.heatConsumption, "float"),
            'Components Heat Consumption 1':    self._collectTableData(self.componentsTableHeat1),
            'Reference Flow Type Heat2':        self._getWidgetData(self.referenceFlowTypeHeat2, "str"),
            'Heat Consumption 2':               self._getWidgetData(self.heatConsumption2, "float"),
            'Components Heat Consumption 2':    self._collectTableData(self.componentsTableHeat2),

            # Concentration data
            'Concentration Factor':             self._getWidgetData(self.concentrationFactor, "float"),
            'Reference Flow 1':                 self._getWidgetData(self.referenceFlow1Concentration, "str"),
            'Components Flow1':                 self._collectTableData(self.componentsTableConcentration1),
            'Reference Flow 2':                 self._getWidgetData(self.referenceFlow2Concentration, "str"),
            'Components Flow2':                 self._collectTableData(self.componentsTableConcentration2),

            # Separation Efficiency data
            'Separation Fractions':             self._collectTableData(self.separationEfficiencyTable,
                                                                       tableType="separationEfficiency"),
            'Waste Management':                 self._getWidgetData(self.wasteManagement, "str"),
            "Check box stream 1":               self.stream1CheckBox.isChecked(),
            "Check box stream 2":               self.stream2CheckBox.isChecked(),
            "Check box stream 3":               self.stream3CheckBox.isChecked(),
        }

        return data

    def populateDialog(self, dialogData):
        """
        Populate the dialog with the data provided in the dictionary retrieved from the Central data manager.

        :param data: Dictionary containing data to populate the dialog.
        """
        # General parameters
        if 'Name' in dialogData:
            self.nameInput.setText(dialogData['Name'])
        if 'Processing Group' in dialogData:
            self.processingGroupInput.setText(str(dialogData['Processing Group']))
        if 'Life Time Unit Process' in dialogData:
            self.lifeTimeUnitProcess.setText(str(dialogData['Life Time Unit Process']))
        if 'Working Time Unit Process' in dialogData:
            self.fullLoadingHours.setText(str(dialogData['Working Time Unit Process']))
        if 'CO2 Building' in dialogData:
            self.co2EmissionsBuilding.setText(str(dialogData['CO2 Building']))
        if 'TemperatureIn1' in dialogData:
            self.temperatureEnteringProcess.setText(str(dialogData['TemperatureIn1']))
        if 'TemperatureOut1' in dialogData:
            self.temperatureLeavingProcess.setText(str(dialogData['TemperatureOut1']))
        if 'TemperatureIn2' in dialogData:
            self.temperatureEnteringUnitProcess2.setText(str(dialogData['TemperatureIn2']))
        if 'TemperatureOut2' in dialogData:
            self.temperatureLeavingUnitProcess2.setText(str(dialogData['TemperatureOut2']))
        if 'Operating Hours' in dialogData:
            self.operatingAndMaintenanceCost.setText(str(dialogData['Operating Hours']))
        if 'Direct Cost Factor' in dialogData:
            self.directCostFactor.setText(str(dialogData['Direct Cost Factor']))
        if 'Indirect Cost Factor' in dialogData:
            self.indirectCostFactor.setText(str(dialogData['Indirect Cost Factor']))

        # Reoccurring Annualized Capital Costs
        if 'Reoccurring Cost Factor' in dialogData:
            self.turnOverFactor.setText(str(dialogData['Reoccurring Cost Factor']))
        if 'Turn Over Time' in dialogData:
            self.turnOverTime.setText(str(dialogData['Turn Over Time']))
        if 'Turn Over Unit' in dialogData:
            self.comboBoxUnits.setCurrentText(dialogData['Turn Over Unit'])

        # Cost-related factors
        if 'Reference Flow Type' in dialogData:
            index = self.referenceFlowType.findText(dialogData['Reference Flow Type'])
            if index != -1:
                self.referenceFlowType.setCurrentIndex(index)
        if 'Reference Flow Equipment Cost' in dialogData:
            self.referenceFlowInput.setText(str(dialogData['Reference Flow Equipment Cost']))
        if 'Exponent' in dialogData:
            self.exponentInput.setText(str(dialogData['Exponent']))
        if 'Reference Cost Unit' in dialogData:
            self.referenceCost.setText(str(dialogData['Reference Cost Unit']))
        if 'Reference Year' in dialogData:
            self.referenceYear.setText(str(dialogData['Reference Year']))

        # Utility consumption dialogData
        if 'Reference Flow Type Energy' in dialogData:
            index = self.referenceFlowTypeEnergy.findText(dialogData['Reference Flow Type Energy'])
            if index != -1:
                self.referenceFlowTypeEnergy.setCurrentIndex(index)
        if 'Energy Consumption' in dialogData:
            self.energyConsumption.setText(str(dialogData['Energy Consumption']))
        if 'Reference Flow Type Chilling' in dialogData:
            index = self.referenceFlowTypeChilling.findText(dialogData['Reference Flow Type Chilling'])
            if index != -1:
                self.referenceFlowTypeChilling.setCurrentIndex(index)
        if 'Chilling Consumption' in dialogData:
            self.chillingConsumption.setText(str(dialogData['Chilling Consumption']))

        # Heat consumption dialogData
        if 'Reference Flow Type Heat1' in dialogData:
            index = self.referenceFlowTypeHeat1.findText(dialogData['Reference Flow Type Heat1'])
            if index != -1:
                self.referenceFlowTypeHeat1.setCurrentIndex(index)
        if 'Heat Consumption 1' in dialogData:
            self.heatConsumption.setText(str(dialogData['Heat Consumption 1']))
        if 'Reference Flow Type Heat2' in dialogData:
            index = self.referenceFlowTypeHeat2.findText(dialogData['Reference Flow Type Heat2'])
            if index != -1:
                self.referenceFlowTypeHeat2.setCurrentIndex(index)
        if 'Heat Consumption 2' in dialogData:
            self.heatConsumption2.setText(str(dialogData['Heat Consumption 2']))

        # Concentration dialogData
        if 'Concentration Factor' in dialogData:
            self.concentrationFactor.setText(str(dialogData['Concentration Factor']))
        if 'Reference Flow 1' in dialogData:
            index = self.referenceFlow1Concentration.findText(dialogData['Reference Flow 1'])
            if index != -1:
                self.referenceFlow1Concentration.setCurrentIndex(index)
        if 'Reference Flow 2' in dialogData:
            index = self.referenceFlow2Concentration.findText(dialogData['Reference Flow 2'])
            if index != -1:
                self.referenceFlow2Concentration.setCurrentIndex(index)

        # Separation Efficiency dialogData
        if 'Waste Management' in dialogData:
            index = self.wasteManagement.findText(dialogData['Waste Management'])
            if index != -1:
                self.wasteManagement.setCurrentIndex(index)
        if 'Check box stream 1' in dialogData:
            self.stream1CheckBox.setChecked(dialogData['Check box stream 1'])
        if 'Check box stream 2' in dialogData:
            self.stream2CheckBox.setChecked(dialogData['Check box stream 2'])
        if 'Check box stream 3' in dialogData:
            self.stream3CheckBox.setChecked(dialogData['Check box stream 3'])

        # Populate tables
        if 'Components Equipment Costs' in dialogData:
            self._populateTable(self.componentsTable, dialogData['Components Equipment Costs'], tabName='cost')
        if 'Components Energy Consumption' in dialogData:
            self._populateTable(self.componentsTableEnergy, dialogData['Components Energy Consumption'], tabName='energy')
        if 'Components Chilling Consumption' in dialogData:
            self._populateTable(self.componentsTableChilling, dialogData['Components Chilling Consumption'], tabName='chilling')
        if 'Components Heat Consumption 1' in dialogData:
            self._populateTable(self.componentsTableHeat1, dialogData['Components Heat Consumption 1'], tabName='heat1')
        if 'Components Heat Consumption 2' in dialogData:
            self._populateTable(self.componentsTableHeat2, dialogData['Components Heat Consumption 2'], tabName='heat2')
        if 'Components Flow1' in dialogData:
            self._populateTable(self.componentsTableConcentration1, dialogData['Components Flow1'], tabName='concentration1')
        if 'Components Flow2' in dialogData:
            self._populateTable(self.componentsTableConcentration2, dialogData['Components Flow2'], tabName='concentration2')
        if 'Separation Fractions' in dialogData:
            self._populateTable(self.separationEfficiencyTable, dialogData['Separation Fractions'], tabName='separationEfficiency',
                                tableType="separationEfficiency")

        # update the waste fraction
        rowCount = self.separationEfficiencyTable.rowCount()
        for i in range(rowCount):
            self._updateWasteFraction(i)


    def _populateTable(self, table, dialogData, tabName, tableType="standard"):
        """
        Populate a given table with the dialogData provided.

        Args:
        - table (QTableWidget): The table to populate.
        - dialogData (list): A list of dictionaries containing the dialogData for the table.
        - tableType (str): Type of the table (default is "standard").
        """
        table.setRowCount(0)  # Clear existing rows
        for rowData in dialogData:
            rowPosition = table.rowCount()
            componentName = rowData
            self._addRowToTable(tabName=tabName, componentName=componentName)  # Reuse addRowToTable method to add rows

            if tableType == "separationEfficiency":
                # Populate columns for separation efficiency table
                table.cellWidget(rowPosition, 0).setCurrentText(rowData['Component'])  # ComboBox for Component
                table.cellWidget(rowPosition, 1).setText(str(rowData['Stream 1']))  # QLineEdit for Stream 1
                table.cellWidget(rowPosition, 2).setText(str(rowData['Stream 2']))  # QLineEdit for Stream 2
                table.cellWidget(rowPosition, 3).setText(str(rowData['Stream 3']))  # QLineEdit for Stream 3
                table.item(rowPosition, 4).setText(str(rowData['Waste']))  # Read-only item for Waste

            else:
                # Populate standard tables with component names
                table.cellWidget(rowPosition, 0).setCurrentText(rowData)

    def _createLcaDialogTab(self):
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
        self._createSectionTitle(text="LCA Input", layout=layout)
        # ----------------------------------------------------------------------------------------------------------

        # Reference Flow type Energy
        self.referenceFlowTypeEnergy = createReferenceFlowTypeComboBox("referenceFlowTypeEnergy")
        tooltipText = """The reference flow type is the type of flow that is used to calculate the Energy Consumption of
                                    the unit process."""
        self._addRowWithTooltip(layout, labelText="Reference Flow Type:", widget=self.referenceFlowTypeEnergy,
                                tooltipText=tooltipText)
        self.referenceFlowTypeEnergy.currentIndexChanged.connect(
            lambda: self._componentSelectionSwitch(type="Electricity"))

        # Electricity Consumption parameter
        self.energyConsumption = QLineEdit(self)
        self.energyConsumption.setText("0.00")
        self.energyConsumption.setValidator(QDoubleValidator(0.00, 999999.99, 2))
        self.energyConsumption.setObjectName("energyConsumption")
        tooltipText = """The energy consumption of the unit process."""
        # add a label to the energy consumption units
        self.referenceFlowUnitEnergy = QLabel(self)
        self.referenceFlowUnitEnergy.setText("MWh/t")  # Replace "Your Start Value" with the value you want to set
        self.referenceFlowUnitEnergy.setFixedWidth(120)  # make the lable bigger in width
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
        self._addRowWithTooltip(layout, labelText="Components:", widget=self.componentsTableEnergy,
                                # add same table to the layout
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
        self.referenceFlowTypeChilling.currentIndexChanged.connect(
            lambda: self._componentSelectionSwitch(type="Chilling"))

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
        self._addRowWithTooltip(layout, labelText="Components:", widget=self.componentsTableChilling,
                                # add same table to the layout
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

    def _collectTableData(self, table, tableType=""):
        """
        Collect the data from the table.
        :param table: the table widget to collect the data from
        :param tableType: the type of the table if it is a separation efficiency table
                            or a standard table (just containing components)
        :return:
        """
        data = []
        if tableType == "separationEfficiency":
            for row in range(table.rowCount()):
                component = table.cellWidget(row, 0).currentText()
                stream1 = self._getCellValue(table, row, 1)
                stream2 = self._getCellValue(table, row, 2)
                stream3 = self._getCellValue(table, row, 3)
                waste = self._getCellValue(table, row, 4)
                data.append({
                    'Component': component,
                    'Stream 1': stream1,
                    'Stream 2': stream2,
                    'Stream 3': stream3,
                    'Waste': waste
                })
        else:
            for row in range(table.rowCount()):
                element = table.cellWidget(row, 0).currentText()
                data.append(element)
        return data

    def _getWidgetData(self, widget, type:str, returnAlternative=0):
        """
        Get the data from the widgets.
        :return:
        """

        if isinstance(widget, QLineEdit):
            textWidget = widget.text()  # get the text from the widget

        elif isinstance(widget, QComboBox):
            textWidget = widget.currentText() # get the text from the widget

        else:
            raise ValueError("The widget type is not supported")

        match type:
            case "float":
                if textWidget == "":
                    return returnAlternative
                else:
                    return float(textWidget)

            case "int":
                if textWidget == "":
                    return returnAlternative
                else:
                    return int(textWidget)

            case "str":
                return str(textWidget)

    def saveData(self, type:ProcessType):
        """
        Creates an instance of the ProcessDTO and saves the data to the central data manager.
        :return:
        """
        # collect the data from the dialog
        dialogData = self.collectData()

        if self._errorCheck(dialogData):
            return

        # print(ProcessType.INPUT)
        # create a new processDTO and add the data to it
        dtoProcess = ProcessDTO(uid=self.iconID, name=dialogData['Name'], type=type)
        # add the dialog data to the processDTO
        dtoProcess.addDialogData(dialogData)
        # add the processDTO to the centralDataManager
        self.centralDataManager.unitProcessData[self.iconID] = dtoProcess
        self.accept()



    # -----------------------------------------------------------------
    # Methods for checking errors
    # -----------------------------------------------------------------

    def _errorCheck(self,dialogData):
        """
        Check for errors in the dialog data.

        check if:
        1) the name is not empty
        2) the temperatures (the first pair) are not empty
        3) the sum of fractions is not larger than 1 for the separation efficiency

        :return:
        """
        # check if the name is not empty
        if dialogData["Name"] == "":
            errorMessage = "The name of the unit process is not set"
            self._showErrorDialog(errorMessage)
            return True

        # check if the temperatures are not empty
        if dialogData["TemperatureIn1"] == 0 or dialogData["TemperatureOut1"] == 0:
            errorMessage = "The temperatures of the unit process are not set"
            self._showErrorDialog(errorMessage)
            return True

        # check if the sum of the fractions is not larger than 1
        errorCheckSeparation, errorMessageSeparation = self._checkSumOfSeparationFractions()
        if errorCheckSeparation:
            self._showErrorDialog(errorMessageSeparation)
            return True

        return False  # if no errors are found return False

    def _showErrorDialog(self, message):
        """
        Show an error dialog with the message provided.
        :param message: Message to show in the dialog
        """
        errorDialog = QMessageBox()
        errorDialog.setIcon(QMessageBox.Critical)
        errorDialog.setText(message)
        errorDialog.setWindowTitle("Error")
        errorDialog.exec_()

    def _checkSumOfSeparationFractions(self):
        """
        Check if the sum of the separation fractions is larger than 1. check the flag parameter
        :return: true or false depending on the flag
        """
        errorMessage = ""
        # check if the first colunm contains names of the components I.E. is not ''
        for row in range(self.separationEfficiencyTable.rowCount()):
            if self.separationEfficiencyTable.cellWidget(row, 0).currentText() == '':
                errorMessage = "The component name in the separation efficiency table is not set"
                return True, errorMessage

        if True in self.separationErrorDict.values():
            errorMessage = ("The sum of the separation fractions is larger than 1, \n"
                            "please check the tab 'Separation Efficiency'")
            return True, errorMessage
        else:
            return False, errorMessage

