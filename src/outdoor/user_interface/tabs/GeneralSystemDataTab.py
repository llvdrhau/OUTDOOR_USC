from unittest import case

from PyQt5.QtWidgets import QFormLayout, QComboBox, QFrame, QWidget, QLineEdit, QPushButton, QLabel
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QDoubleValidator, QFont
# add the looger
from src.outdoor.user_interface.utils.OutdoorLogger import outdoorLogger
import logging

class GeneralSystemDataTab(QWidget):
    """
    This class creates a tab for the general system data
    """
    def __init__(self, centralDataManager, outputManager, parent=None):
        super().__init__(parent)
        # add the logger
        self.logger = outdoorLogger(name="outdoor_logger", level=logging.DEBUG)

        # add the central data manager
        self.centralDataManager = centralDataManager
        self.outputManager = outputManager

        # Create a new QWidget for the General System Data tab
        self.layout = QFormLayout(self)
        self.subtitleFont = QFont("Arial", 11, QFont.Bold)
        # Set the background color of the widget
        self.setStyleSheet("background-color: #f5f5f5;")

        # Title for the general system data (centered)
        self.createSectionTitle(text="General System Data", centerAlign=False, color="#C7CEEA")

        self.opti_combo = QComboBox(self)
        self.opti_combo.addItems(
            ["Single", "Multi-Objective", "Sensitivity", "Cross-Parameter Sensitivity",
             "2-Stage-Recourse", "Multi-2-Stage-Recourse"])
        self.layout.addRow(QLabel("Optimization Mode:"), self.opti_combo)
        self.opti_combo.currentIndexChanged.connect(self.saveData)

        # Combo box for the objective function
        self.objective_combo = QComboBox(self)
        self.objective_combo.addItems(
            ["EBIT: Earnings Before Income Taxes", "NPC: Net Production Costs", "NPE: Net Produced CO2 Emissions",
             "FWD: Freshwater Demand"])
        self.layout.addRow(QLabel("Objective Function:"), self.objective_combo)
        self.objective_combo.currentIndexChanged.connect(self.saveData)

        # Title for the specific production of a product
        self.createSectionTitle(text="Specific Production", color="#B5EAD7")

        # Create a dropdown for "Product driven"
        self.productDrivenDropdown = QComboBox()
        self.productDrivenDropdown.addItems(["Yes", "No"])  # Add options to the dropdown
        self.layout.addRow(QLabel("Product driven:"), self.productDrivenDropdown)
        self.productDrivenDropdown.currentIndexChanged.connect(self.saveData)

        self.productSelection = QComboBox()
        self.layout.addRow(QLabel("Main product:"), self.productSelection)
        # Initially populate the combo box
        self._updateProductSelectioComboBox()
        # Connect the centralDataManager's signal to the update method
        self.outputManager.outputListUpdated.connect(self._updateProductSelectioComboBox)
        # if changed save data
        self.productSelection.currentIndexChanged.connect(self.saveData)


        self.productLoadLineEdit = QLineEdit()
        self.productLoadLineEdit.setValidator(
            QDoubleValidator(0.00, 999999.99, 2))  # Set validator to restrict to floating-point numbers
        self.layout.addRow(QLabel("Product load:"), self.productLoadLineEdit)  # only floating numbers allowed as input

        # Connect the signal to the slot function
        self.productDrivenDropdown.currentIndexChanged.connect(lambda: self.productDrivenSwitch())

        # connect to the save data function
        self.productLoadLineEdit.textChanged.connect(self.saveData)


        # make title "general CAPEX parameters"
        self.createSectionTitle(text="General CAPEX parameters", color="#E2F0CB")

        # Add fields for the general CAPEX parameters
        self.operatingHoursLineEdit = QLineEdit("8000")
        self.layout.addRow(QLabel("Operating Hours:"), self.operatingHoursLineEdit)
        self.operatingHoursLineEdit.textChanged.connect(self.saveData)

        self.yearOfStudyLineEdit = QLineEdit("2018")
        self.layout.addRow(QLabel("Year of Study:"), self.yearOfStudyLineEdit)
        self.yearOfStudyLineEdit.textChanged.connect(self.saveData)

        self.interestRateLineEdit = QLineEdit("0.05")
        self.layout.addRow(QLabel("Interest rate:"), self.interestRateLineEdit)
        self.interestRateLineEdit.textChanged.connect(self.saveData)

        self.detailLevelLineEdit = QComboBox()
        self.detailLevelLineEdit.addItems(["real", "fine", "rough", "average"])  # Add options to the dropdown
        self.layout.addRow(QLabel("Detail level of linearization of CAPEX:"), self.detailLevelLineEdit)
        self.detailLevelLineEdit.currentIndexChanged.connect(self.saveData)

        self.indirectCostsLineEdit = QLineEdit("1.44")
        self.layout.addRow(QLabel("Indirect costs:"), self.indirectCostsLineEdit)
        self.indirectCostsLineEdit.textChanged.connect(self.saveData)

        self.directCostsLineEdit = QLineEdit("2.6")
        self.layout.addRow(QLabel("Direct costs:"), self.directCostsLineEdit)
        self.directCostsLineEdit.textChanged.connect(self.saveData)

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
        self.heatPumpDropdown.addItems(["Yes", "No"])  # Add options to the dropdown
        self.layout.addRow(QLabel("Heat pump switch:"), self.heatPumpDropdown)
        self.heatPumpDropdown.currentIndexChanged.connect(self.saveData)

        # Add fields for the heat pump parameters
        self.COPLineEdit = QLineEdit("2.5")
        self.COPLineEdit.setValidator(
            QDoubleValidator(0.00, 999999.99, 2))  # Set validator to restrict to floating-point numbers
        self.layout.addRow(QLabel("Coefficient of performance (COP):"), self.COPLineEdit)
        self.COPLineEdit.textChanged.connect(self.saveData)

        self.costLineEdit = QLineEdit("450")
        self.costLineEdit.setValidator(
            QDoubleValidator(0.00, 999999.99, 2))  # Set validator to restrict to floating-point numbers
        self.layout.addRow(QLabel("Cost per kW installed:"), self.costLineEdit)
        self.costLineEdit.textChanged.connect(self.saveData)


        self.lifetimeLineEdit = QLineEdit("0")
        self.lifetimeLineEdit.setValidator(
            QDoubleValidator(1990, 2018, 0))  # Set validator to restrict to floating-point numbers
        self.layout.addRow(QLabel("Lifetime:"), self.lifetimeLineEdit)
        self.lifetimeLineEdit.textChanged.connect(self.saveData)


        self.TINLineEdit = QLineEdit()
        self.TINLineEdit.setValidator(
            QDoubleValidator(0.00, 999999.99, 2))  # Set validator to restrict to floating-point numbers
        self.layout.addRow(QLabel("Inlet Temperature °C:"), self.TINLineEdit)
        self.TINLineEdit.textChanged.connect(self.saveData)


        self.TOUTLineEdit = QLineEdit()
        self.TOUTLineEdit.setValidator(
            QDoubleValidator(0.00, 999999.99, 2))  # Set validator to restrict to floating-point numbers
        self.layout.addRow(QLabel("Outlet Temperature °C:"), self.TOUTLineEdit)
        self.TOUTLineEdit.textChanged.connect(self.saveData)

        # Connect the signal to the slot function
        self.heatPumpDropdown.currentIndexChanged.connect(lambda: self.heatPumpSwitch())



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
        self.importData()

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
        if self.productDrivenDropdown.currentText() == "No":
            # If "No" is selected, make the other fields not editable
            self.productSelection.setDisabled(True)
            self.productSelection.setCurrentText("")
            self.productLoadLineEdit.setDisabled(True)
            self.productLoadLineEdit.setText("")
            # Set the background color to grey
            self.productSelection.setStyleSheet("background-color: #f5f5f5;")
            self.productLoadLineEdit.setStyleSheet("background-color: #f5f5f5;")

        else:
            # If "Yes" is selected, make the other fields editable
            self.productSelection.setDisabled(False)
            self.productLoadLineEdit.setDisabled(False)
            # set the background color to white
            self.productSelection.setStyleSheet("background-color: #ffffff;")
            self.productLoadLineEdit.setStyleSheet("background-color: #ffffff;")

    def heatPumpSwitch(self):
        if self.heatPumpDropdown.currentText() == "No":
            # If "No" is selected, make the other fields not editable
            self.COPLineEdit.setDisabled(True)
            self.costLineEdit.setDisabled(True)
            self.lifetimeLineEdit.setDisabled(True)
            self.TINLineEdit.setDisabled(True)
            self.TOUTLineEdit.setDisabled(True)
            # Set the fields to empty
            self.COPLineEdit.setText("")
            self.costLineEdit.setText("")
            self.lifetimeLineEdit.setText("")
            self.TINLineEdit.setText("")
            self.TOUTLineEdit.setText("")
            # set the background color to grey
            self.COPLineEdit.setStyleSheet("background-color: #f5f5f5;")
            self.costLineEdit.setStyleSheet("background-color: #f5f5f5;")
            self.lifetimeLineEdit.setStyleSheet("background-color: #f5f5f5;")
            self.TINLineEdit.setStyleSheet("background-color: #f5f5f5;")
            self.TOUTLineEdit.setStyleSheet("background-color: #f5f5f5;")

        else:
            # If "Yes" is selected, make the other fields editable
            self.COPLineEdit.setDisabled(False)
            self.costLineEdit.setDisabled(False)
            self.lifetimeLineEdit.setDisabled(False)
            self.TINLineEdit.setDisabled(False)
            self.TOUTLineEdit.setDisabled(False)
            # set the background color to white
            self.COPLineEdit.setStyleSheet("background-color: #ffffff;")
            self.costLineEdit.setStyleSheet("background-color: #ffffff;")
            self.lifetimeLineEdit.setStyleSheet("background-color: #ffffff;")
            self.TINLineEdit.setStyleSheet("background-color: #ffffff;")
            self.TOUTLineEdit.setStyleSheet("background-color: #ffffff;")


    @pyqtSlot()
    def saveData(self):

        # Collect data from the table
        generalData = self.collectData()

        # Save the data to the central data manager
        # self.centralDataManager.addData("generalData", generalData) # not a fan of this fumction, convoluted

        # overwrite the data to the central data manager straight away
        self.centralDataManager.generalData = generalData
        self.logger.info("General System Data saved")
        # print(generalData)


    def collectData(self):
        # Collect data from the Widget fields
        if "PROJECT_NAME" in self.centralDataManager.data:
            projectName = self.centralDataManager.data["PROJECT_NAME"]
        else:
            projectName = "Not Saved"

        data = {
            "projectName": projectName,
            "productDriver": self.productDrivenDropdown.currentText(),
            "objective": self.objective_combo.currentText(),
            "optimizationMode": self.opti_combo.currentText(),
            "mainProduct": self.productSelection.currentText(),
            "productLoad": self.productLoadLineEdit.text(),
            "operatingHours": self.operatingHoursLineEdit.text(),
            "yearOfStudy": self.yearOfStudyLineEdit.text(),
            "interestRate": self.interestRateLineEdit.text(),
            "detailLevel": self.detailLevelLineEdit.currentText(),
            # "omFactor": self.omFactorLineEdit.text(), => not used in the code is unit specific and not general
            "indirectCost": self.indirectCostsLineEdit.text(),
            "directCost": self.directCostsLineEdit.text(),
            "heatPumpSwitch": self.heatPumpDropdown.currentText(),
            "COP": self.COPLineEdit.text(),
            "cost": self.costLineEdit.text(),
            "lifetime": self.lifetimeLineEdit.text(),
            "TIN": self.TINLineEdit.text(),
            "TOUT": self.TOUTLineEdit.text(),
        }
        # print(data["objective"])
        return data

    def importData(self):
        generalData = self.centralDataManager.generalData
        if generalData:
            self.productSelection.setCurrentText(generalData['mainProduct'])
            self.objective_combo.setCurrentText(generalData["objective"])
            self.opti_combo.setCurrentText(generalData["optimizationMode"])
            self.productDrivenDropdown.setCurrentText(generalData["productDriver"])
            self.productLoadLineEdit.setText(generalData["productLoad"])
            self.operatingHoursLineEdit.setText(generalData["operatingHours"])
            self.yearOfStudyLineEdit.setText(generalData["yearOfStudy"])
            self.interestRateLineEdit.setText(generalData["interestRate"])
            self.detailLevelLineEdit.setCurrentText(generalData["detailLevel"])
            self.indirectCostsLineEdit.setText(generalData["indirectCost"])
            self.directCostsLineEdit.setText(generalData["directCost"])
            self.heatPumpDropdown.setCurrentText(generalData["heatPumpSwitch"])
            self.COPLineEdit.setText(generalData["COP"])
            self.costLineEdit.setText(generalData["cost"])
            self.lifetimeLineEdit.setText(generalData["lifetime"])
            self.TINLineEdit.setText(generalData["TIN"])
            self.TOUTLineEdit.setText(generalData["TOUT"])
        else:
            self.logger.info("Booting up with no General System Data")

    def _updateProductSelectioComboBox(self):
        """
        This function updates the QComboBox with the current values from centralDataManager.outputList.
        """
        # Clear the existing items
        self.productSelection.clear()
        # Add updated items from centralDataManager
        self.productSelection.addItems(self.outputManager.outputList)
