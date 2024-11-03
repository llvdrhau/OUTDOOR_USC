from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel, QHBoxLayout, QMessageBox
from PyQt5.QtGui import QDoubleValidator
from outdoor.user_interface.data.ProcessDTO import ProcessDTO, ProcessType, UpdateField

class OutputParametersDialog(QDialog):
    """
    Opens a dialog to set the output parameters for the output icon. The dialog allows the user to set the product name,
    price output, CO2 credits, minimum production, and maximum production. The user can set the price output and CO2
    credits as floating-point numbers, and the minimum and maximum production as floating-point numbers.
    """
    def __init__(self, initialData, centralDataManager, iconID):
        super().__init__()

        # set the process type
        self.processType = ProcessType.OUTPUT
        # set the iconID
        self.iconID = iconID
        # set the centralDataManager
        self.centralDataManager = centralDataManager

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
        self.okButton.clicked.connect(self.saveData)
        buttonsLayout.addWidget(self.okButton)

        self.cancelButton = QPushButton("Cancel", self)
        self.cancelButton.clicked.connect(self.reject)
        buttonsLayout.addWidget(self.cancelButton)

        layout.addLayout(buttonsLayout)

        # populate the dialog with existing data (initialData) if it is not empty
        if initialData:
            self.populateOutputDialog(initialData.dialogData)

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


    def saveData(self):
        """
        Save the data entered in the dialog to the processDTO. If the data is not valid, show an error dialog.
        """
        # collect the data from the dialog
        dialogData = self.collectData()

        if self._errorCheck(dialogData):
            return

        # retrive the processDTO from the centralDataManager
        dtoOutput = self.centralDataManager.unitProcessData[self.iconID]
        # update the name
        dtoOutput.updateProcessDTO(field= UpdateField.NAME, value= dialogData['Name'])

        # add the dialog data to the processDTO
        dtoOutput.addDialogData(dialogData)

        self.accept()

    def _errorCheck(self, dialogData):

        # check if the product name is empty
        if dialogData['Name'] == "":
            self._showErrorDialog("Product Name cannot be empty.")
            return True
        # if no error, return False
        return False

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
