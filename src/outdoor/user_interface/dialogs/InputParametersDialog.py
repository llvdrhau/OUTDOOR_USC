
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel, QTableWidget, QTableWidgetItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDoubleValidator

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
