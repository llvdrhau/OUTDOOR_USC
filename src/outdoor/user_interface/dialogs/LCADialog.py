from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel, QTableWidget, QTableWidgetItem
from PyQt5.QtCore import Qt, QPoint

import bw2data as bw
from bw2data.backends import Activity
import difflib


class LCADialog(QDialog):
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
        self.setWindowTitle("LCA Lookup")
        self.setGeometry(100, 100, 400, 500)  # Adjust size as needed

        # TODO: Better initialization and handling of BW integration.
        bw.projects.set_current("test")
        self.eidb = bw.Database('ei_391_c')

        layout = QVBoxLayout(self)
        self.lcaProcesses = {}
        # Lookup name
        layout.addWidget(QLabel("Search term:"))
        self.searchLine = QLineEdit(self)
        layout.addWidget(self.searchLine)

        # Lookup region
        layout.addWidget(QLabel("Preferred region (ISO):"))
        self.regionLine = QLineEdit("RER")
        layout.addWidget(self.regionLine)

        # Search button
        self.searchButton = QPushButton("Search", self)
        self.searchButton.clicked.connect(self.search)
        layout.addWidget(self.searchButton)

        # Search table
        self.searchColumns = ["Reference", "Unit", "Activity", "Region", "ID"]
        layout.addWidget(QLabel("Search Results:"))
        self.componentsTable = QTableWidget(0, len(self.searchColumns), self)  # Initial rows, 2 columns
        self.componentsTable.setHorizontalHeaderLabels(self.searchColumns)
        self.componentsTable.horizontalHeader().setStretchLastSection(True)
        self.componentsTable.verticalHeader().setVisible(False)

        self.componentsTable.setEditTriggers(self.componentsTable.NoEditTriggers)
        self.componentsTable.setSelectionMode(self.componentsTable.MultiSelection)
        self.componentsTable.setSelectionBehavior(self.componentsTable.SelectRows)
        layout.addWidget(self.componentsTable)

        # Button to put selection into processes table
        self.addRowButton = QPushButton("Add to Process", self)
        self.addRowButton.clicked.connect(self.addLCAProcess)
        layout.addWidget(self.addRowButton)

        # Processes table
        self.lcaColumns = ["Demand", "Unit", "Region", "Reference"]
        self.selectedProcessesTable = QTableWidget(0, 4, self)
        self.selectedProcessesTable.setHorizontalHeaderLabels(self.lcaColumns)
        self.selectedProcessesTable.horizontalHeader().setStretchLastSection(True)
        self.selectedProcessesTable.verticalHeader().setVisible(False)
        layout.addWidget(QLabel("Processes:"))
        layout.addWidget(self.selectedProcessesTable)

    def search(self):
        self.componentsTable.setRowCount(0)
        name = self.searchLine.text()
        location = self.regionLine.text()
        loc_results = [m for m in self.eidb if name in m['name'] and location in m['location']]
        for item in sorted(loc_results, key=lambda x: difflib.SequenceMatcher(None, x['name'], name).ratio(), reverse=True):
            self.addRowToTable(Reference=item['name'], Unit=item['unit'], Activity=item['type'], Region=item['location'], ID=item['code'], Table="Search")
        gen_results = [m for m in self.eidb if name in m["name"] and location not in m["location"]]
        self.addRowToTable(Reference="---", Unit="---", Activity="---", Region="---", ID="---", Table="Search")
        for item in sorted(gen_results, key=lambda x: difflib.SequenceMatcher(None, x['name'], name).ratio(), reverse=True):
            self.addRowToTable(Reference=item['name'], Unit=item['unit'], Activity=item['type'],
                               Region=item['location'], ID=item['code'], Table="Search")

    def addRowToTable(self, **kwargs):
        rowPosition = 0
        match kwargs["Table"]:
            case "Search":
                columns = self.searchColumns
                rowPosition = self.componentsTable.rowCount()
                table = self.componentsTable
            case "LCA":
                columns = self.lcaColumns
                rowPosition = self.selectedProcessesTable.rowCount()
                table = self.selectedProcessesTable
            case _:
                print("There's been a problem with your table.")
                return
        table.insertRow(rowPosition)
        for item in kwargs.items():
            if item[0] in columns:
                col = columns.index(item[0])
                insert = QTableWidgetItem(item[1])
                if item[1] == "---":
                    insert.setBackground(QColor(218, 222, 227))
                    insert.setFlags(Qt.NoItemFlags)  # No selecting the blank row
                else:
                    insert.setFlags(
                        insert.flags() | Qt.ItemIsSelectable)  # Ensure the item is selectable but not editable
                table.setItem(rowPosition, col, insert)

    def addLCAProcess(self):
        rroo = self.componentsTable.selectedItems()
        for item in rroo:
            if item.column() == 4:
                if item.text() not in self.lcaProcesses:
                    self.lcaProcesses[item.text()] = {
                        "Reference": self.componentsTable.item(item.row(), 0).text(),
                        "Unit": self.componentsTable.item(item.row(), 1).text(),
                        "Region": self.componentsTable.item(item.row(), 3).text(),
                        "Demand": "0",
                        "Parameter": "bw_param_name"
                    }
                    self.addRowToTable(Demand=self.lcaProcesses[item.text()]["Demand"],Unit=self.lcaProcesses[item.text()]["Unit"],Region=self.lcaProcesses[item.text()]["Region"],Reference=self.lcaProcesses[item.text()]["Reference"],Table="LCA")
        self.componentsTable.clearSelection()

    def populateLCATable(self):
        self.selectedProcessesTable.clear()
        for id, info in self.lcaProcesses:
            pass

    def collectData(self):
        """Collect data from all fields to save state."""
        data = {
            "": ""
        }
        return data

