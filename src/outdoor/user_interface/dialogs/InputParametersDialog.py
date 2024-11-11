from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDoubleValidator, QFont, QCursor
from PyQt5.QtWidgets import (QDialog, QLineEdit, QPushButton, QLabel, QTableWidget, QTableWidgetItem,
                             QFormLayout, QFrame, QToolTip, QApplication, QMessageBox)

from outdoor.user_interface.data.CentralDataManager import CentralDataManager
from outdoor.user_interface.data.ProcessDTO import ProcessType, UpdateField
from outdoor.user_interface.utils.NonFocusableComboBox import NonFocusableComboBox


class InputParametersDialog(QDialog):
    """
    Opens a dialog to set the input parameters for the input icon. The dialog allows the user to set the source name,
    price input, components, CO2 emission factor, lower limit, and upper limit. The components are entered in a table
    format with two columns: Component Name and % Composition. The user can add multiple rows to enter multiple
    components and their composition in the feedstock.
    """

    def __init__(self, initialData, centralDataManager: CentralDataManager, iconID):
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
        self.setGeometry(150, 150, 450, 350)  # Adjust size as needed
        self.centralDataManager = centralDataManager
        self.dialogData = initialData.dialogData if initialData else {}

        # pass on the iconID to the class
        self.iconID = iconID

        # set the process type
        self.processType = ProcessType.INPUT

        #layout = QVBoxLayout(self)
        layout = QFormLayout(self)

        # Title for the component tab
        self.title = self._createSectionTitle("Input Parameters", color="#e1e1e1", centerAlign=True, layout=layout)

        # Source Name
        self.sourceName = QLineEdit(self)
        self._addRowWithTooltip(layout=layout, labelText= "Source Name:", widget=self.sourceName,
                                tooltipText="Enter the name of the source for this feedstock.")

        # Price Input
        self.priceInput = QLineEdit(self)
        self._addRowWithTooltip(layout=layout, labelText="Cost Input (euro/t):", widget=self.priceInput,
                                tooltipText="Enter the cost of the feedstock in euros per ton.")
        self.priceInput.setValidator(QDoubleValidator(0.00, 999999.99, 2))

        # the sum of the fractions should be 1.0, keeps track of the sum of the fractions
        self.sumFractionLabel = QLineEdit(self)
        self._addRowWithTooltip(layout=layout, labelText="Sum of fractions:", widget=self.sumFractionLabel,
                                tooltipText="The sum of the fractions should be 1.0. "
                                            "\nThe counter turns red if the sum exceeds 1.0, and purple if not.")
        self.sumFractionLabel.setReadOnly(True)
        self.sumFractionLabel.setStyleSheet("background-color: orange;")
        # initialize the fractionError flag to False
        self.fractionError = True


        # Components table
        self.componentsTable = QTableWidget(0, 2, self)  # Initial rows, 2 columns
        self.componentsTable.setHorizontalHeaderLabels(["Component Name", "% Composition"])
        self.componentsTable.setToolTip("Enter the composition of components in percentage.")  # Adding a tooltip
        self._addRowWithTooltip(layout=layout, labelText="Components:", widget=self.componentsTable,
                                tooltipText="Enter the composition of components in percentage.")

        # Add Row button
        self.addRowButton = QPushButton("Add Row", self)
        self.addRowButton.setToolTip("Click to add a new row for entering component details.")  # Adding a tooltip
        self.addRowButton.clicked.connect(self.addRowToComponentsTable)
        layout.addWidget(self.addRowButton)

        # # CO2 Emission Factor
        # self.co2EmissionFactor = QLineEdit(self)
        # self._addRowWithTooltip(layout=layout, labelText="CO2 Emission Factor:", widget=self.co2EmissionFactor,
        #                         tooltipText="Enter the CO2 emission factor for this source in kg CO2 per ton, should deleet this soon ")
        #
        # self.co2EmissionFactor.setValidator(QDoubleValidator(0.00, 999999.99, 2))


        # Lower Limit
        self.lowerLimit = QLineEdit(self)
        self._addRowWithTooltip(layout=layout, labelText="Lower Limit (t/h):", widget=self.lowerLimit,
                                tooltipText="Enter the lower limit for the quantity in tons.")
        self.lowerLimit.setValidator(QDoubleValidator(0.00, 999999.99, 2))

        # Upper Limit
        self.upperLimit = QLineEdit(self)
        self._addRowWithTooltip(layout=layout, labelText="Upper Limit (t/h):", widget=self.upperLimit,
                                tooltipText="Enter the upper limit for the quantity in tons/h.")
        self.upperLimit.setValidator(QDoubleValidator(0.00, 999999.99, 2))

        # OK and Cancel buttons
        self.okButton = QPushButton("OK", self)
        self.okButton.clicked.connect(self.saveData)
        layout.addWidget(self.okButton)

        self.cancelButton = QPushButton("Cancel", self)
        self.cancelButton.clicked.connect(self.reject)
        layout.addWidget(self.cancelButton)

        # Populate the dialog with existing data (initialData) if it is not empty
        if initialData:
            self.populateInputDialog(self.dialogData)

    def addRowToComponentsTable(self, componentName=None, composition=None):
        """
        Add a row to the table specified by the component name and composition.

        :return: updated table with the new row
        """

        rowPosition = self.componentsTable.rowCount()
        self.componentsTable.insertRow(rowPosition)

        # create the comboboxewidget
        self.comboBoxComponents = NonFocusableComboBox()
        chemicalNames = self.centralDataManager.getChemicalComponentNames()
        self.comboBoxComponents.addItems(chemicalNames)
        self.comboBoxComponents.setObjectName(f"comboBoxComponents_{rowPosition}")

        # Set the current text to the component_name if provided
        if componentName and componentName in chemicalNames:
            self.comboBoxComponents.setCurrentText(componentName)

        item = QTableWidgetItem('hack')  # adding this is a hack otherwise the row can't be selected and deleted
        self.componentsTable.setItem(rowPosition, 0, item)
        self.componentsTable.setCellWidget(rowPosition, 0, self.comboBoxComponents)

        self.componentsTable.setSelectionBehavior(QTableWidget.SelectRows)
        self.componentsTable.setSelectionMode(QTableWidget.SingleSelection)  # or MultiSelection if needed

        # compostion should be a line edit with a validator to restrict to floating-point numbers
        lineEdit = QLineEdit()
        validator = QDoubleValidator(0.0, 1.0, 3)  # Values between 0 and 1, up to 5 decimal places
        validator.setNotation(QDoubleValidator.StandardNotation)
        lineEdit.setValidator(validator)

        if composition is not None:
            lineEdit.setText(str(composition))

        lineEdit.textChanged.connect(self._updateFractionCounter)
        self.componentsTable.setCellWidget(rowPosition, 1, lineEdit)

    def collectData(self):
        """Collect data from all fields to save state."""
        data = {
            'Name': self.sourceName.text(),
            'priceInput': self.priceInput.text(),
            'components': [],
            #'co2EmissionFactor': self.co2EmissionFactor.text(),
            'lowerLimit': self.lowerLimit.text(),
            'upperLimit': self.upperLimit.text()
        }

        # Collect data from the components table
        for row in range(self.componentsTable.rowCount()):
            component_name = self.componentsTable.cellWidget(row, 0).currentText() # is a combobox
            composition = self.componentsTable.cellWidget(row, 1).text()
            if composition == "":
                composition = 0.0
            else:
                composition = float(composition)

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

        # Populate the components table if data for components is available
        if 'components' in data:
            components = data['components']
            for component_name, composition in components:
                self.addRowToComponentsTable(componentName=component_name, composition=composition)
        # Update the fraction counter after populating
        self._updateFractionCounter()

    def _updateFractionCounter(self):
        """
        Sum of the fractions for the components should be 1.0. This function updates the counter to show the remaining
        fraction to reach 1.0. The counter also turns red if the sum exceeds 1.0 and purple if less than 1.0.
        """
        total = 0.0
        fractionError = True
        for row in range(self.componentsTable.rowCount()):
            lineEdit = self.componentsTable.cellWidget(row, 1)  # Get the QLineEdit from the second column
            if lineEdit is not None:
                try:
                    value = float(lineEdit.text()) if lineEdit.text() else 0.0
                    total += value
                except ValueError:
                    pass  # Handle any conversion errors silently

        # Update the sumFractionLabel with the total sum
        self.sumFractionLabel.setText(f"{total:.3f}")

        # Change the color of the background of sumFractionLabel based on the total sum
        if total > 1.0:
            self.sumFractionLabel.setStyleSheet("background-color: red;")
        elif total < 1.0:
            self.sumFractionLabel.setStyleSheet("background-color: orange;")
        else:
            self.sumFractionLabel.setStyleSheet("background-color: green;")
            fractionError = False

        # pass on the fractionError flag to the parent class
        self.fractionError = fractionError



    # -----------------------------------------------------------------
    # methods for tool-tips,
    # -----------------------------------------------------------------
    def _addRowWithTooltip(self, layout, labelText, widget, tooltipText, widget2=None):
        label = QLabel(f'{labelText} <a href="#">(i)</a>')
        label.setToolTip(tooltipText)
        label.linkActivated.connect(self._showTooltip)
        if widget is None:
            layout.addRow(label)
        else:
            layout.addRow(label, widget)

    def _showTooltip(self, _):
        QToolTip.setFont(QFont('SansSerif', 10))
        QToolTip.showText(QCursor.pos(), self.sender().toolTip())

    def _createSectionTitle(self, text, color="#e1e1e1", centerAlign=False, layout=None):
        title = QLabel(text)
        subtitleFont = QFont("Arial", 9, QFont.Bold)
        title.setFont(subtitleFont)
        title.setStyleSheet(f"background-color: {color}; padding: 3px;")
        if centerAlign:
            title.setAlignment(Qt.AlignCenter)
        frame = QFrame()
        frame.setFrameShape(QFrame.HLine)
        frame.setFrameShadow(QFrame.Sunken)
        layout.addRow(title)
        layout.addRow(frame)

    def keyPressEvent(self, event):
        """
        Override the keyPressEvent method to allow deleting rows in the components table using the Backspace or Delete
        :param event:
        :return:
        """
        if event.key() == Qt.Key_Backspace or event.key() == Qt.Key_Delete:
            focused_widget = QApplication.focusWidget()

            if isinstance(focused_widget, QTableWidget):
                selectedItems = focused_widget.selectedItems()
                if selectedItems:
                    selectedRow = selectedItems[0].row()
                    focused_widget.removeRow(selectedRow)
            self._updateFractionCounter()

        else:
            super().keyPressEvent(event)

    # -----------------------------------------------------------------
    # methodes for error checking and saveing data to the processDTO
    # -----------------------------------------------------------------

    def saveData(self):
        """
        Save the data entered in the dialog to the processDTO. If the data is not valid, show an error dialog.
        """
        # collect the data from the dialog
        dialogData = self.collectData()

        if self._errorCheck(dialogData):
            return


        # get the dto
        dto = self.centralDataManager.unitProcessData[self.iconID]
        # update the dto with the new data
        dto.updateProcessDTO(field=UpdateField.NAME, value=dialogData['Name'])

        # get all the chemical from the dialogData in the table and update the dto
        chemicals = [chemical[0] for chemical in dialogData['components']]
        dto.updateProcessDTO(field=UpdateField.OUTGOINGCHEMICALS, value=chemicals)

        # add the dialog data to the processDTO
        dto.addDialogData(dialogData)

        # # create a new processDTO and add the data to it
        # dtoInput = ProcessDTO(uid=self.iconID, name=dialogData['Name'],
        #                       type=self.processType, outGoingChemicals=chemicals)
        # add the processDTO to the centralDataManager
        # self.centralDataManager.unitProcessData[self.iconID] = dtoInput

        self.accept()

    def _errorCheck(self, dialogData):
        """
        Check if the data entered in the dialog is valid. If not, show an error message.

        :return: True if there is an error, False otherwise
        """

        if self.fractionError:
            self._showErrorDialog("The sum of the fractions should be 1.0.")
            return True # there is an error if you return true

        if dialogData['Name'] == "":
            self._showErrorDialog("Source Name is required.")
            return True

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


