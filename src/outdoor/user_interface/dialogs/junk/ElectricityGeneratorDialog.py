from PyQt5.QtGui import QDoubleValidator, QIntValidator
from PyQt5.QtWidgets import QLineEdit, QWidget, QHBoxLayout, QFormLayout, QComboBox

from outdoor.user_interface.dialogs.StoichiometricReactorDialog import StoichiometricReactorDialog


class ElectricityGeneratorDialog(StoichiometricReactorDialog):
    def __init__(self, initialData, centralDataManager, iconID):
        super().__init__(initialData, centralDataManager, iconID)  # Initialize the parent class
        # Additional initialization for ElectricityGeneratorDialog

        tabWidget = self.tabWidget
        # delete the tab "General tab" from the parent class
        tabWidget.removeTab(0)
        # remake the tab "General Parameters"
        # position the tab "General Parameters" at the first position
        tabWidget.insertTab(0, self._createGeneralParametersTab(), "General Parameters")


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
        # Efficiency
        # ---------------------------------------------------------------
        self._createSectionTitle(text="Efficiency", layout=layout)
        self.efficiency = QLineEdit(self)
        tooltipText = """Efficiency of the electrical generator unit."""
        self._addRowWithTooltip(layout, labelText="Efficiency", widget=self.efficiency, tooltipText=tooltipText)
        # only double values are allowed
        self.efficiency.setValidator(QDoubleValidator(0.00, 1.00, 2))
        # give a default value
        self.efficiency.setText('0.58')

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

