from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QTableWidget, QVBoxLayout, QTableWidgetItem
from PyQt5.QtCore import Qt

from outdoor.user_interface.utils.DoubleDelegate import DoubleDelegate


class UtilityTab(QWidget):
    def __init__(self, centralDataManager, parent=None):
        super().__init__(parent)
        self.centralDataManager = centralDataManager

        # Main layout for the tab
        layout = QVBoxLayout(self)

        # Upper table for general utilities
        self.utilitiesTable = QTableWidget(3, 3)  # 3 rows for utilities, 4 columns for data
        self.utilitiesColumns = ["Costs (€/MWh)", "CO2 Emissions (t/MWh)", "Fresh water depletion (t/MWh)"]
        self.utilitiesTable.setHorizontalHeaderLabels(self.utilitiesColumns)
        self.utilitiesRows = ["Electricity", "Heat", "Chilling"]
        self.utilitiesTable.setVerticalHeaderLabels(self.utilitiesRows)
        # set the width of the columns to be bigger so it fits the column names
        self.utilitiesTable.setColumnWidth(0, 120)
        self.utilitiesTable.setColumnWidth(1, 180)
        self.utilitiesTable.setColumnWidth(2, 230)
        if 'utilitiesData' in self.centralDataManager.data:
            self._loadUtilityData()
        else:
            utilitiesData = [
                [87, 0.014, 0],
                ['', 0.248, 0],
                [35, 0.1, 0]
            ]
            self._populateUtilitiesTable(utilitiesData)
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
        if 'temperatureData' in self.centralDataManager.data:
            self._loadTemperatureData()
        else:
            temperatureData = [
                [600, 34],
                [330, 32],
                [220, 30],
                [130, 29],
                [15, 0.22]
            ]
            self._populateTemperatureTable(temperatureData)
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

    def _populateUtilitiesTable(self, utilitiesData):
        # Fill in the utilities table with data
        for i, row in enumerate(utilitiesData):
            for j, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                self.utilitiesTable.setItem(i, j, item)
                # make the width of the columns bigger
                if value =='':  # Costs column has float values
                    # item.setFlags(item.flags() | Qt.ItemIsEditable)
                    self.utilitiesTable.item(i, j).setFlags(self.utilitiesTable.item(i, j).flags() & ~Qt.ItemIsEditable)

    def _populateTemperatureTable(self, temperatureData):
        # Fill in the temperature table with data

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
            rowData = [self.utilitiesRows[row]]
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
        print(temperatureData)
        return temperatureData

    def _loadUtilityData(self):
        utilityLoad = self.centralDataManager.data["utilitiesData"]
        utilityCleaned = []
        for row in utilityLoad:
            utilityCleaned.append([row[1], row[2], row[3]])
            self._populateUtilitiesTable(utilityCleaned)

    def _loadTemperatureData(self):
        tempLoad = self.centralDataManager.data["temperatureData"]
        self._populateTemperatureTable(tempLoad)

