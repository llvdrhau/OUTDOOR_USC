from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel, QTableWidget, QTableWidgetItem
from PyQt5.QtCore import Qt, QPoint

import bw2data as bw
import bw2calc as bc
import pandas as pd
#from bw2data.backends import Activity
import difflib
from outdoor.user_interface.data.ComponentDTO import ComponentDTO


class LCADialog(QDialog):
    """
    Opens a dialog to set the input parameters for the input icon. The dialog allows the user to set the source name,
    price input, components, CO2 emission factor, lower limit, and upper limit. The components are entered in a table
    format with two columns: Component Name and % Composition. The user can add multiple rows to enter multiple
    components and their composition in the feedstock.
    """

    def __init__(self, initialData: ComponentDTO):
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
        self.bios = bw.Database('biosphere3')
        self.outd = bw.Database('outdoor')

        layout = QVBoxLayout(self)
        self.dto = initialData
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
        self.lcaColumns = ["Demand", "Unit", "Region", "Reference", "ID"]
        self.selectedProcessesTable = QTableWidget(0, 5, self)
        self.selectedProcessesTable.setHorizontalHeaderLabels(self.lcaColumns)
        self.selectedProcessesTable.horizontalHeader().setStretchLastSection(True)
        self.selectedProcessesTable.verticalHeader().setVisible(False)
        layout.addWidget(QLabel("Processes:"))
        layout.addWidget(self.selectedProcessesTable)

        # persistButton = QPushButton("Persist", self)
        # persistButton.clicked.connect(self.persistProcesses)
        # layout.addWidget(persistButton)

        saveButton = QPushButton("Save Inventory", self)
        saveButton.clicked.connect(self.persistLCA)
        layout.addWidget(saveButton)
        calculateButton = QPushButton("Calculate LCA", self)
        calculateButton.clicked.connect(self.calculateLCA)
        layout.addWidget(calculateButton)

        self.loadInitialData()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Backspace | Qt.Key_Delete:
            all = self.selectedProcessesTable.selectedItems()
            rows = []
            for item in all:
                if item.row() not in rows:
                    rows.append(item.row())
            print(rows)
            for row in rows:
                index = self.lcaColumns.index("ID")
                id = self.selectedProcessesTable.item(row, index).text()
                self.dto.LCA.pop(id)
                self.selectedProcessesTable.removeRow(row)

    def search(self):
        self.componentsTable.setRowCount(0)
        name = self.searchLine.text()
        location = self.regionLine.text()
        loc_results = [m for m in self.eidb if name in m['name'] and location in m['location']]
        self.addRowToTable(Type="Blank", Head="Preferred Region", Table="Search")
        for item in sorted(loc_results, key=lambda x: difflib.SequenceMatcher(None, x['name'], name).ratio(),
                           reverse=True):
            self.addRowToTable(Reference=item['name'], Unit=item['unit'], Activity=item['type'],
                               Region=item['location'], ID=item['code'], Table="Search")
        gen_results = [m for m in self.eidb if name in m["name"] and location not in m["location"]]
        self.addRowToTable(Type="Blank", Head="Non-preferred Regions", Table="Search")
        for item in sorted(gen_results, key=lambda x: difflib.SequenceMatcher(None, x['name'], name).ratio(),
                           reverse=True):
            self.addRowToTable(Reference=item['name'], Unit=item['unit'], Activity=item['type'],
                               Region=item['location'], ID=item['code'], Table="Search")
        self.addRowToTable(Type="Blank", Head="Biosphere", Table="Search")
        biosphere_results = [m for m in self.bios if name in m['name']] + [m for m in self.bios if
                                                                           name.capitalize() in m['name']]
        for item in sorted(biosphere_results, key=lambda x: difflib.SequenceMatcher(None, x['name'], name).ratio(),
                           reverse=True):
            self.addRowToTable(Reference=item['name'], Unit=item['unit'], Activity=item['type'],
                               Region=str(item['categories']), ID=item['code'], Table="Search")

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
        if "Type" in kwargs:
            if kwargs["Type"] == "Blank":
                for col in columns:
                    index = columns.index(col)
                    insert = QTableWidgetItem(kwargs["Head"]) if index == 0 else QTableWidgetItem("---")
                    insert.setBackground(QColor(218, 222, 227))
                    insert.setFlags(Qt.NoItemFlags)
                    table.setItem(rowPosition, index, insert)
                return

        for item in kwargs.items():
            if item[0] in columns:
                col = columns.index(item[0])
                insert = QTableWidgetItem(item[1])
                insert.setFlags(insert.flags() | Qt.ItemIsSelectable)  # Ensure the item is selectable but not editable
                table.setItem(rowPosition, col, insert)

    def addLCAProcess(self):
        selectedItems = self.componentsTable.selectedItems()
        for item in selectedItems:
            if item.column() == 4:
                if item.text() not in self.dto.LCA:
                    self.dto.LCA[item.text()] = {
                        "Reference": self.componentsTable.item(item.row(), 0).text(),
                        "Unit": self.componentsTable.item(item.row(), 1).text(),
                        "Region": self.componentsTable.item(item.row(), 3).text(),
                        "Demand": "0",
                        "Parameter": "bw_param_name",
                        "DB": self.componentsTable.item(item.row(), 2).text(),
                    }
                    self.addRowToTable(Demand=self.dto.LCA[item.text()]["Demand"],
                                       Unit=self.dto.LCA[item.text()]["Unit"],
                                       Region=self.dto.LCA[item.text()]["Region"],
                                       Reference=self.dto.LCA[item.text()]["Reference"],
                                       ID=item.text(),
                                       Table="LCA")
        self.componentsTable.clearSelection()

    def updateLCAProcesses(self):
        if self.selectedProcessesTable.rowCount() > 1:
            for i in range(self.selectedProcessesTable.rowCount()):
                id = self.selectedProcessesTable.item(i, 3).text()
                print(self.selectedProcessesTable.item(i, 0).text())
                self.dto.LCA[id]["Demand"] = self.selectedProcessesTable.item(i, 0).text()
                self.dto.LCA[id]["Reference"] = self.selectedProcessesTable.item(i, 3).text()
                self.dto.LCA[id]["Unit"] = self.selectedProcessesTable.item(i, 1).text()
                self.dto.LCA[id]["Region"] = self.selectedProcessesTable.item(i, 2).text()

    def loadInitialData(self):
        for key, value in self.dto.LCA.items():
            print(key, value)
            self.addRowToTable(Demand=value["Demand"], Unit=value["Unit"], Region=value["Region"], Reference=value["Reference"], ID=key,
                               Table="LCA")

    def persistLCA(self):
        process = {
            "location": "GLO",
            "name": self.dto.uid,
            "type": "process",
            "unit": "kilogram",
            "exchanges": []
        }
        tup = ("outdoor", self.dto.uid)
        self.outd.write({tup: process})

        calc_act = [m for m in self.outd if m['name'] == self.dto.uid][0]
        ext_list = []
        for row in range(self.selectedProcessesTable.rowCount()):
            demand = self.selectedProcessesTable.item(row, 0).text()
            id = self.selectedProcessesTable.item(row, 4).text()
            self.dto.LCA[id]["Demand"] = demand
        for id, dic in self.dto.LCA.items():
            if dic["DB"] == "process":
                ex = [m for m in self.eidb if m['code'] == id][0]
                ext_list.append((ex, dic["Demand"], dic["Unit"], dic["DB"]))
            else:
                ex = [m for m in self.bios if m['code'] == id][0]
                ext_list.append((ex, dic["Demand"], dic["Unit"], dic["DB"]))

        for tup in ext_list:
            ex = tup[0]
            calc_act.new_exchange(
                input=(ex['database'], ex['code']),
                amount=float(tup[1]),
                unit=ex['unit'],
                type="biosphere" if ex['database'] == "biosphere3" else "technosphere",
            ).save()
        calc_act.save()

    def calculateLCA(self):
        midpoint = [m for m in bw.methods if "ReCiPe 2016 v1.03, midpoint (H)" in str(m) and not "no LT" in str(m)]
        endpoints = [ m for m in bw.methods if "ReCiPe 2016 v1.03, endpoint (H)" in str(m) and not "no LT" in str(m) and "total" in str(m)]
        meths = midpoint + endpoints
        try:
            activ = [m for m in self.outd if m['name'] == self.dto.uid][0]
            calc_setup = {"inv":[{activ:1}],"ia":meths}
            bw.calculation_setups["set"] = calc_setup
            mlca = bc.MultiLCA("set")
            indic = []

            for f in mlca.func_units:
                indic.append(f"{str(f).replace('{', '').replace('}', '')}")
            dfresults = pd.DataFrame(mlca.results, columns=mlca.methods, index=indic)
            print(dfresults)
            self.dto.LCA["Results"]=dfresults
            self.dto.calculated = True
        except Exception as e:
            if type(e) is IndexError:
                print("Didn't find the uuid in bw, ", self.dto.uid)

