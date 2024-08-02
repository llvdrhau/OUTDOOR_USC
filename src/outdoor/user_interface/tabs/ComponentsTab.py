
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QPushButton, QLabel,QTableWidgetItem
from PyQt5.QtCore import Qt

from outdoor.user_interface.utils.DoubleDelegate import DoubleDelegate


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
