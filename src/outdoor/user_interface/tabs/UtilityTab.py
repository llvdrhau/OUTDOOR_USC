from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QLabel, QTableWidget, QVBoxLayout, QTableWidgetItem

from outdoor.user_interface.data.UtilityDTO import UtilityDTO
from outdoor.user_interface.utils.DoubleDelegate import DoubleDelegate


class UtilityTab(QWidget):
    def __init__(self, centralDataManager, parent=None):
        super().__init__(parent)
        self.centralDataManager = centralDataManager
        self.utilityDTO: UtilityDTO = centralDataManager.utilityData
        # Main layout for the tab
        layout = QVBoxLayout(self)

        # Upper table for general utilities
        self.utilitiesColumns = ["Costs (€/MWh)", "CO2 Emissions (t/MWh)", "Fresh water depletion (t/MWh)", "LCA"]
        self.utilitiesTable = QTableWidget(3, len(self.utilitiesColumns))  # 3 rows for utilities, 4 columns for data

        self.utilitiesTable.setHorizontalHeaderLabels(self.utilitiesColumns)
        self.utilitiesRows = ["Electricity", "Heat", "Chilling"]
        self.utilitiesTable.setVerticalHeaderLabels(self.utilitiesRows)
        # set the width of the columns to be bigger so it fits the column names
        self.utilitiesTable.setColumnWidth(0, 120)
        self.utilitiesTable.setColumnWidth(1, 200)
        self.utilitiesTable.setColumnWidth(2, 230)
        self.utilitiesTable.setColumnWidth(3, 120)

        # Row 2, Column 1 (zero-based indexing: row 1, column 0) - make it uneditable
        # (cost of heat is specified by the user in the table below)
        item = QTableWidgetItem("")  # Set a placeholder value
        self.utilitiesTable.setItem(1, 0, item)
        item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Make uneditable

        # Graying out the item (optional)
        item.setBackground(Qt.gray)  # Change text color to gray

        self._populateUtilitiesTable(self.utilityDTO.utilityParameters)
        # Save the data if something is changed in the table
        self.utilitiesTable.itemChanged.connect(self._saveData)


        # Set validators for the numeric columns using a custom delegate class
        self.doubleDelegateUtility = DoubleDelegate(self.utilitiesTable)
        for i in range(0, self.utilitiesTable.columnCount()):
            if self.utilitiesColumns[i] != "LCA":
                self.utilitiesTable.setItemDelegateForColumn(i, self.doubleDelegateUtility)
            else:
                #TODO Add a separate ctor for LCA button that takes a UtilityDTO
                pass


        # Lower table for temperature levels
        self.temperatureTable = QTableWidget(5, 2)  # 5 rows for temperature levels, 3 columns for data
        self.temperatureTable.setHorizontalHeaderLabels(["Temperature (°C)", "Costs (€/MWh)"])
        self.temperatureTable.setVerticalHeaderLabels(["Superheated steam", "High pressure steam", "Medium pressure steam", "Low pressure steam", "Cooling water"])
        self.temperatureTable.setColumnWidth(0, 150)
        self.temperatureTable.setColumnWidth(1, 150)

        self._populateTemperatureTable(self.utilityDTO.temperatureParameters)

        # Set validators for the numeric columns using a custom delegate class
        self.doubleDelegateTemperature = DoubleDelegate(self.temperatureTable)
        for i in range(0, self.temperatureTable.columnCount()):
            self.temperatureTable.setItemDelegateForColumn(i, self.doubleDelegateTemperature)

        self.temperatureTable.itemChanged.connect(self._saveData)

        # Add tables to the layout
        layout.addWidget(QLabel("Utilities"))
        layout.addWidget(self.utilitiesTable)
        layout.addWidget(QLabel("Cost of heat"))
        layout.addWidget(self.temperatureTable)

        # Save button
        # not needed, data is saved automatically when edited
        # saveButton = QPushButton("Save Data")
        # saveButton.clicked.connect(self._saveData)
        # layout.addWidget(saveButton)

    def _populateUtilitiesTable(self, utilitiesData):
        """
        populate the utilities table with data
        :param utilitiesData:
        :return:
        """
        for column, (key, values) in enumerate(utilitiesData.items()):
            for row, value in enumerate(values):
                if column == 0 and row == 1:
                    continue
                item = QTableWidgetItem(str(value))
                self.utilitiesTable.setItem(row, column, item)
    def _populateTemperatureTable(self, temperatureParameters):
        """
        populate the temperature table with data
        :param temperatureParameters:
        :return:
        """
        for row, t in enumerate(temperatureParameters["Temperature (°C)"].values()):
            itemTemp = QTableWidgetItem(str(t))
            self.temperatureTable.setItem(row, 0, itemTemp)

        for row, cost in enumerate(temperatureParameters["Costs (€/MWh)"].values()):
            itemCost = QTableWidgetItem(str(cost))
            self.temperatureTable.setItem(row, 1, itemCost)

    def _saveData(self):
        """
        Save the data from the tables to the central data manager
        """

        # collects and updates the utility data in the DTO and the central data manager simulataniously
        self._collectUtilitiesData()
        self._collectTemperatureData()

        print(self.centralDataManager.utilityData.utilityParameters)
        print(self.centralDataManager.utilityData.temperatureParameters)


    def _collectUtilitiesData(self):
        """
        Collect the data from the utilities table and update the utilityDTO (as DTO is connected to the central data
        manager, it is also updated)
        :return:
        """
        for column in range(self.utilitiesTable.rowCount()):
            name = self.utilitiesTable.horizontalHeaderItem(column).text()
            for row in range(self.utilitiesTable.rowCount()):
                value = self.utilitiesTable.item(row, column).text()
                if value == "":
                    value = 0
                self.utilityDTO.utilityParameters[name][row] = float(value)

    def _collectTemperatureData(self):
        """
        Collect the data from the temperature table and update the utilityDTO (as DTO is connected to the central data
        manager, it is also updated)
        :return:
        """

        for row in range(self.temperatureTable.rowCount()):
            temp = self.temperatureTable.item(row, 0).text()
            cost = self.temperatureTable.item(row, 1).text()
            keys = list(self.utilityDTO.temperatureParameters["Temperature (°C)"].keys())
            self.utilityDTO.temperatureParameters["Temperature (°C)"][keys[row]] = float(temp)
            self.utilityDTO.temperatureParameters["Costs (€/MWh)"][keys[row]] = float(temp)
            #temperatureData.append([temp, cost])
        # print(temperatureData)

    # def _loadUtilityData(self):
    #     utilityLoad = self.centralDataManager.data["utilitiesData"]
    #     utilityCleaned = []
    #     for row in utilityLoad:
    #         utilityCleaned.append([row[1], row[2], row[3]])
    #         self._populateUtilitiesTable(utilityCleaned)
    #
    # def _loadTemperatureData(self):
    #     tempLoad = self.centralDataManager.data["temperatureData"]
    #     self._populateTemperatureTable(tempLoad)

