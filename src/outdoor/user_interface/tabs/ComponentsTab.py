import uuid

from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QPushButton, QLabel, QTableWidgetItem, QDialog, QMenu
from PyQt5.QtCore import Qt, pyqtSlot

from outdoor.user_interface.data.ComponentDTO import ComponentDTO
from outdoor.user_interface.dialogs.LCADialog import LCADialog
from outdoor.user_interface.dialogs.LcaButton import LcaButton
from outdoor.user_interface.utils.DoubleDelegate import DoubleDelegate
# retrive the logger
from outdoor.user_interface.utils.OutdoorLogger import outdoorLogger
import logging


class ComponentsTab(QWidget):
    """
    This class creates a tab for the chemical components and related data (e.g., molar weight, LHV, heat capacity, etc.)
    This is the tab that defines each chemical component and its properties used throught the flow sheet.
    """

    def __init__(self, centralDataManager, parent=None):
        super().__init__(parent)
        # add the logger
        self.logger = outdoorLogger(name='outdoor_logger', level=logging.DEBUG)

        # add the central data manager
        self.centralDataManager = centralDataManager
        self.componentList: list[ComponentDTO] = centralDataManager.componentData

        # set the flag of adding a row to false
        self.addingRowFlag = False

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
        self.layout = QVBoxLayout(self)

        # Title for the component tab
        self.title = QLabel("Components and related Data")
        self.title.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.title)

        # Table for the component data
        self.componentsTable = QTableWidget()
        self.componentsTable.setColumnCount(5)
        self.columnsList = [
            "Component", "Lower heating Value (kWh/kg)",
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
        # self.doubleValidator = QDoubleValidator(0.00, 9999.99, 2)

        # save if something is changed in the table
        self.componentsTable.itemChanged.connect(self.saveData)

        # Add the table to the layout
        self.layout.addWidget(self.componentsTable)
        # Add Row Button
        self.addRowButton = QPushButton("Add Chemical Component")
        self.addRowButton.clicked.connect(self.addComponentRow)
        self.layout.addWidget(self.addRowButton)


        # Ensure the widget can receive focus to detect key presses
        self.setFocusPolicy(Qt.StrongFocus)
        self.setLayout(self.layout)

        # if the central data manager has data, import it
        self.importData()

        # if self.componentsTable.rowCount() == 0:
        #     self.addComponentRow()

    def addComponentRow(self, data: ComponentDTO | None = None):
        """
        This method adds a row to the table for the chemical components
        :param data: of type ComponentDTO, the data to be added to the table, can be None
        :return:
        """
        # set the flag of adding a row to true
        self.addingRowFlag = True

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
            if key in self.columnsShortnames:
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

        # set the flag of adding a row to false
        self.addingRowFlag = False


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

    @pyqtSlot()
    def saveData(self):
        if not self.addingRowFlag:
            self.collectData()
            # Save the data to the central data manager
            self.centralDataManager.addData("chemicalComponentsData", self.componentList)
            self.logger.debug("Data saved components tab to central data manager")


    def collectData(self):
        # Collect data from the table
        for row in range(self.componentsTable.rowCount()):
            edit = [u for u in self.componentList if u.rowPosition == row][0]
            rowData = []
            for column in self.columnsList:
                sindex = self.columnsList.index(column)
                item = self.componentsTable.item(row, sindex)
                if column in ["Component", "Lower heating Value (kWh/kg)", "Heat capacity (kJ/kg/K)", "Molecular weight (g/mol)"]:
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

    def contextMenuEvent(self, event):
        # Create a context menu
        context_menu = QMenu(self)

        # Add actions for deleting rows from both tables
        deleteAction = context_menu.addAction("Delete Row")

        # Execute the context menu and get the selected action
        action = context_menu.exec_(self.mapToGlobal(event.pos()))

        # Determine which table was clicked
        component_pos = self.componentsTable.viewport().mapFrom(self, event.pos())

        if self.componentsTable.geometry().contains(event.pos()) and action == deleteAction:
            # Determine the row that was clicked in the reactants table
            row = self.componentsTable.rowAt(component_pos.y())
            if row != -1:
                self.componentsTable.removeRow(row)

            # update the dto list containing the chemical components
            self.centralDataManager.updateData('componentData', row)
            # todo make a consistency check to see if the chemical component is used in any reaction or unit operation
            # open a dialog if the component is used in a reaction or unit operation

