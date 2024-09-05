import uuid

from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QPushButton, QLabel, QTableWidgetItem, QDialog
from PyQt5.QtCore import Qt

from outdoor.user_interface.data.ComponentDTO import ComponentDTO
from outdoor.user_interface.dialogs.LCADialog import LCADialog
from outdoor.user_interface.dialogs.LcaButton import LcaButton
from outdoor.user_interface.utils.DoubleDelegate import DoubleDelegate


class ComponentsTab(QWidget):
    """
    This class creates a tab for the chemical components and related data (e.g., molar weight, LHV, heat capacity, etc.)
    This is the tab that defines each chemical component and its properties used throught the flow sheet.
    """

    def __init__(self, centralDataManager, parent=None):
        super().__init__(parent)
        self.centralDataManager = centralDataManager
        self.componentList: list[ComponentDTO] = centralDataManager.componentData
        self.layout = QVBoxLayout(self)

        # Title for the component tab
        self.title = QLabel("Components and related Data")
        self.title.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.title)

        # Table for the component data
        self.componentsTable = QTableWidget()
        self.componentsTable.setColumnCount(5)
        self.columnsList = [
            "Component", "Lower heating Value (MWh/t)",
            "Heat capacity (kJ/kg/K)", "Molecular weight (g/mol)",
            "LCA Data"
        ]
        self.columnsShortnames = ["name", "lowerHeat", "heatCapacity", "molecularWeight", "LCA"]
        self.componentsTable.setHorizontalHeaderLabels(self.columnsList)

        # adjust the width of the columns
        self.componentsTable.setColumnWidth(0, 150)
        self.componentsTable.setColumnWidth(1, 230)
        self.componentsTable.setColumnWidth(2, 180)
        self.componentsTable.setColumnWidth(3, 210)
        self.componentsTable.setColumnWidth(4, 150)
        self.componentsTable.itemDoubleClicked.connect(self.doubleClickEvent)

        # Set validators for the numeric columns using a custom delegate class
        self.doubleDelegate = DoubleDelegate(self.componentsTable)
        #self.doubleValidator = QDoubleValidator(0.0, 9999.99, 4)


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
        self.importData()
        if self.componentsTable.rowCount() == 0:
            self.addComponentRow()

    def addComponentRow(self, data: ComponentDTO | None = None):
        rowPosition: int
        if data is None or not isinstance(data, ComponentDTO):
            rowPosition = self.componentsTable.rowCount()
            uid = uuid.uuid4().__str__()
            data = ComponentDTO(rowPosition, uid)
            self.componentList.append(data)
        else:
            rowPosition = data.rowPosition
        self.componentsTable.insertRow(rowPosition)

        for key, value in data.as_dict().items():
            try:
                index = self.columnsShortnames.index(key)
                if key == "LCA":
                    if "Results" in value:
                        btn = LcaButton(self.componentsTable, data)
                        btn.setText("Defined")
                        btn.clicked.connect(btn.lcaAction)
                        self.componentsTable.setCellWidget(rowPosition, index, btn)
                    else:
                        btn = LcaButton(self.componentsTable, data)
                        btn.setText("Not Defined")
                        btn.clicked.connect(btn.lcaAction)
                        self.componentsTable.setCellWidget(rowPosition, index, btn)
                else:
                    insert = QTableWidgetItem(value)
                    insert.setFlags(insert.flags() | Qt.ItemIsEditable)
                    self.componentsTable.setItem(rowPosition, index, insert)
            except ValueError:
                #This happens because there are more keys in the componentdto dictionary than there are columns.
                #It isn't a problem.
                continue

        # for i in range(self.componentsTable.columnCount()):
        #     item = QTableWidgetItem(str(data[i]))
        #     self.componentsTable.setItem(rowPosition, i, item)
        #     if i in [1, 2, 3]:  # Set the validator for numeric columns
        #         # Set the delegate for the column where only double values are allowed
        #         self.componentsTable.setItemDelegateForColumn(i, self.doubleDelegate)
        #     if i == 4:
        #         btn = LcaButton(self.componentsTable, rowPosition)
        #         btn.setText("Not Defined")
        #         btn.clicked.connect(btn.lcaAction)
        #         self.componentsTable.setCellWidget(rowPosition, i, btn)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Backspace | Qt.Key_Delete:
            selectedItems = self.componentsTable.selectedItems()
            if selectedItems:
                selectedRow = selectedItems[0].row()  # Get the row of the first selected item
                self.componentsTable.removeRow(selectedRow)
                target = [u for u in self.componentList if u.rowPosition == selectedRow][0]
                self.componentList.remove(target)
                for c in [u for u in self.componentList if u.rowPosition >= selectedRow]:
                    c.updateRow()
        else:
            super().keyPressEvent(event)

    def doubleClickEvent(self, item):
        print(item.row(), item.column())

    def saveData(self):
        self.collectData()
        # Save the data to the central data manager
        # self.centralDataManager.addData("chemicalComponentsData")

        # Change the border of OK button to green
        # self.okButton.setStyleSheet("border: 2px solid green;")

    def collectData(self):
        # Collect data from the table
        for row in range(self.componentsTable.rowCount()):
            edit = [u for u in self.componentList if u.rowPosition == row][0]
            rowData = []
            for column in self.columnsList:
                sindex = self.columnsList.index(column)
                item = self.componentsTable.item(row, sindex)
                if column in ["Component", "Lower heating Value (MWh/t)", "Heat capacity (kJ/kg/K)", "Molecular weight (g/mol)"]:
                    edit.upadateField(self.columnsShortnames[sindex], item.text())
                if column == "LCA":
                    # this is handled inside the DTO
                    pass

    def sortComponentDTO(self,dto: ComponentDTO):
        return dto.rowPosition
    def importData(self):
        try:
            #tabledata = self.centralDataManager.data["chemicalComponentsData"]
            tabledata = self.componentList
            for row in tabledata:
                self.addComponentRow(row)
        except Exception as e:
            raise e
            pass
            # it only gets here if there aren't any saved rows, like in a new project


