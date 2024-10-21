from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel, QWidget, QTableWidget, QTabWidget, \
    QApplication, QHBoxLayout, QTableWidgetItem, QFormLayout, QComboBox, QFrame, QToolTip
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDoubleValidator, QFont, QCursor, QIntValidator

from outdoor.user_interface.utils.NonFocusableComboBox import NonFocusableComboBox

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

        self.setWindowTitle("Unit Process Parameters")
        self.setGeometry(100, 100, 600, 400)  # Adjust size as needed

        self.subtitleFont = QFont("Arial", 9, QFont.Bold)

        tabWidget = QTabWidget(self)
        calc_types = self.centralDataManager.configs["calcConfigs"]
        tabWidget.addTab(self._createGeneralParametersTab(), "General Parameters")
        if calc_types['Cost'] == 'True':
            tabWidget.addTab(self._createCostRelatedFactorsTab(), "Cost Related Parameters")
        if calc_types['Utility Consumption'] == 'True':
            tabWidget.addTab(self._createUtilityConsumptionTab(), "Utility Consumption")
        if calc_types['Heating'] == 'True':
            tabWidget.addTab(self._createHeatingConsumptionTab(), "Heating Requirements")
        if calc_types['Concentration'] == 'True':
            tabWidget.addTab(self._createConcentrationTab(), "Concentration Factors")
        if calc_types['LCA'] == 'True':
            tabWidget.addTab(self._createLcaDialogTab(), "LCA")
        # You can add more tabs as needed...

        # save the tabWidget as an attribute so it can be called in other class that inherit from this class
        self.tabWidget = tabWidget

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
        tooltipText = """Percentage of the raw purchase equipment costs to pay for parts to replace."""  # Cu^(RE) in the thesis of Philpp
        self._addRowWithTooltip(layout, labelText="Turn Over Factor:", widget=self.turnOverFactor,
                                tooltipText=tooltipText)
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

    def _addRowToTable(self, tabName: str = ''):

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

        else:
            raise ValueError("The add row button is not connected to any table please check the "
                             "object name of the button")

        # Get the current row count and insert a new row at the end
        rowPosition = table.rowCount()
        table.insertRow(rowPosition)

        # add restrictions to the Reactants table so stoichiometric and conversion factors are only between 0 and 1
        if tabName == "reactantsTable" or senderName == "addRowButtonReactantsTable":
            # Add QTableWidgetItems for "Reactant Name" and "Reaction Number" columns
            table.setItem(rowPosition, 0, QTableWidgetItem(""))
            table.setItem(rowPosition, 3, QTableWidgetItem(""))
            # Add QLineEdit with QDoubleValidator for "Stoichiometric" and "Conversion Factor" columns
            for columnIndex in [1, 2]:  # Columns "Stoichiometric" and "Conversion Factor"
                lineEdit = QLineEdit()
                validator = QDoubleValidator(0.0, 1.0, 5)  # Values between 0 and 1, up to 5 decimal places
                validator.setNotation(QDoubleValidator.StandardNotation)
                lineEdit.setValidator(validator)
                table.setCellWidget(rowPosition, columnIndex, lineEdit)

        # add restrictions to the Products table so stoichiometric and conversion factors are only between 0 and 1
        if tabName == "productsTable" or senderName == "addRowButtonProductsTable":
            # Add QTableWidgetItems for "Component Name" and "Reaction Number" columns
            table.setItem(rowPosition, 0, QTableWidgetItem(""))
            table.setItem(rowPosition, 2, QTableWidgetItem(""))

            # Add QLineEdit with QDoubleValidator for "Stoichiometric" column
            lineEdit = QLineEdit()
            validator = QDoubleValidator(0.0, 1.0, 5)  # Values between 0 and 1, up to 5 decimal places
            validator.setNotation(QDoubleValidator.StandardNotation)
            lineEdit.setValidator(validator)
            table.setCellWidget(rowPosition, 1, lineEdit)

        # Create new cells by creating a combo box instance
        self.comboBoxComponents = NonFocusableComboBox()
        chemicalNames = self.centralDataManager.getChemicalComponentNames()
        self.comboBoxComponents.addItems(chemicalNames)
        self.comboBoxComponents.setObjectName(f"comboBoxComponents_{rowPosition}")

        item = QTableWidgetItem(
            'hack')  # adding this item is a bit of a hack otherwise the row can't be selected and deleted
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
