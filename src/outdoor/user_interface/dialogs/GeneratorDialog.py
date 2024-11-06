from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel, QWidget, QTableWidget, QTabWidget, \
    QApplication, QHBoxLayout, QTableWidgetItem, QFormLayout, QComboBox, QFrame, QToolTip
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDoubleValidator, QFont, QCursor, QIntValidator

from outdoor.user_interface.dialogs.StoichiometricReactorDialog import StoichiometricReactorDialog
from outdoor.user_interface.dialogs.PhysicalProcessDialog import ProcessType


class GeneratorDialog(StoichiometricReactorDialog):

    def __init__(self, initialData, centralDataManager, iconID):
        super().__init__(initialData, centralDataManager, iconID)  # Initialize the parent class

        # Additional initialization for ElectricityGeneratorDialog
        # start with Heat generator as default type, change according to selected type in the tab
        self.UnitType = ProcessType.GEN_HEAT

        # Add Yield Reaction Tab to the tab widget of the parent class
        self.tabWidget.insertTab(1, self._createEnergyTab(), "Energy Efficiency")

        # initialize update of the unit type based on the selected energy type
        self._energyTypeChanged()

        # initilise the energy tab
        if initialData.dialogData:
            self._populateEnergyTab(initialData.dialogData)

    def _createEnergyTab(self):
        # General Factors Tab
        widget = QWidget()
        layout = QFormLayout()

        self._createSectionTitle(text="Energy Production Type", layout=layout)

        # add a description
        description = QLabel("Specify the type of energy that is produced by the generator: \n"
                             "Electricity, Heat, or Combined Heat and power.")
        description.setWordWrap(True)
        layout.addRow(description)

        # Create a QComboBox
        self.energyType = QComboBox(self)
        self.energyType.addItem("Heat")
        self.energyType.addItem("Electricity")
        self.energyType.addItem("Combined Heat and Power")

        # Add the QComboBox to the layout
        layout.addRow("Energy Type:", self.energyType)

        # add clcik connection to the comboBox
        self.energyType.currentIndexChanged.connect(self._energyTypeChanged)


        # ---------------------------------------------------------------
        # Efficiency
        # ---------------------------------------------------------------
        self._createSectionTitle(text="Conversion Efficiency", layout=layout)

        self.electricalEfficiency = QLineEdit(self)
        tooltipText = """Efficiency of the electrical generator unit. That is the amount of electrical energy produced
                            compared to the amount of energy input from combustion."""

        self._addRowWithTooltip(layout, labelText="Efficiency", widget=self.electricalEfficiency, tooltipText=tooltipText)
        # only double values are allowed
        self.electricalEfficiency.setValidator(QDoubleValidator(0.00, 1.00, 2))
        # give a default value
        self.electricalEfficiency.setText('0.58')

        self.heatEfficiency = QLineEdit(self)
        tooltipText = """Efficiency of the heat generator unit to convert the heat from combustion to useful heat."""
        self._addRowWithTooltip(layout, labelText="Heat Efficiency", widget=self.heatEfficiency, tooltipText=tooltipText)
        # only double values are allowed
        self.heatEfficiency.setValidator(QDoubleValidator(0.00, 1.00, 2))
        # give a default value
        self.heatEfficiency.setText('0.83')


        widget.setLayout(layout)

        return widget

    def _energyTypeChanged(self):
        # get the current vaule in the combobox
        energyType = self.energyType.currentText()
        if energyType == "Heat":
            # set the unit type to heat generator
            self.UnitType = ProcessType.GEN_HEAT

            # gray the background of the line edit to show that it is disabled
            self.electricalEfficiency.setEnabled(False)
            self.electricalEfficiency.setStyleSheet("background-color: lightgray;")
            self.electricalEfficiency.setText('0.58')

            # enable the heat efficiency line edit and set the background to white
            self.heatEfficiency.setEnabled(True)
            self.heatEfficiency.setStyleSheet("background-color: white;")

        elif energyType == "Electricity":
            # set the unit type to electricity generator
            self.UnitType = ProcessType.GEN_ELEC

            # enable the electrical efficiency line edit and set the background to white
            self.electricalEfficiency.setEnabled(True)
            self.electricalEfficiency.setStyleSheet("background-color: white;")

            # gray the background of the line edit to show that it is disabled
            self.heatEfficiency.setEnabled(False)
            self.heatEfficiency.setStyleSheet("background-color: lightgray;")
            self.heatEfficiency.setText('0.83')

        elif energyType == "Combined Heat and Power":
            self.UnitType = ProcessType.GEN_CHP
            self.electricalEfficiency.setEnabled(True)
            self.heatEfficiency.setEnabled(True)
            self.electricalEfficiency.setStyleSheet("background-color: white;")
            self.heatEfficiency.setStyleSheet("background-color: white;")
        else:
            print("Error: Energy Type not recognised")

    def collectData(self):
        """
        Collect the data from the Generator Dialog and return it as a dictionary
        :return:
        """
        dialogData = super().collectData()
        # Add the data from the energy tab
        dialogData['energyType'] = self.energyType.currentText()

        if self.electricalEfficiency.text() == '':
            elecEff = 0.0
        else:
            elecEff = float(self.electricalEfficiency.text())
        dialogData['electricalEfficiency'] = elecEff

        if self.heatEfficiency.text() == '':
            heatEff = 0.0
        else:
            heatEff = float(self.heatEfficiency.text())
        dialogData['heatEfficiency'] = heatEff

        return dialogData
    def _populateEnergyTab(self, dialogData):
        # populate the energy tab with the data from the dialogData
        self.energyType.setCurrentText(dialogData['energyType'])
        self.electricalEfficiency.setText(str(dialogData['electricalEfficiency']))
        self.heatEfficiency.setText(str(dialogData['heatEfficiency']))

