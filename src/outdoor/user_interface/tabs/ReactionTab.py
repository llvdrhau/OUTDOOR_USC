import logging
import uuid

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QPushButton, QLabel, QTableWidgetItem, QMenu

from outdoor.user_interface.data.ReactionDTO import ReactionDTO
from outdoor.user_interface.dialogs.ReactionDialog import ReactionDialog
from outdoor.user_interface.utils.DoubleDelegate import DoubleDelegate
from outdoor.user_interface.utils.OutdoorLogger import outdoorLogger


class ReactionsTab(QWidget):
    """
    This class creates a tab to define the reactions that will be used in the simulation. It allows the user to define
    the reactants and products of each reaction, as well as the stoichiometry of each component in the reaction.
    """

    def __init__(self, centralDataManager, parent=None):
        super().__init__(parent)

        # add the logger
        self.logger = logging.getLogger(__name__)
        # add row flag to check if a row is being added, to False
        self.addingRowFlag = False

        self.centralDataManager = centralDataManager
        self.reactionList: list[ReactionDTO] = centralDataManager.reactionData
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
        self.title = QLabel("Reactions")
        self.title.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.title)

        # Table for the component data
        self.reactionTable = QTableWidget()
        self.reactionTable.setColumnCount(3)
        self.columnsList = ["Reaction Name", "Reaction Equation", "Edit button"]
        self.reactionTable.setHorizontalHeaderLabels(self.columnsList)

        # adjust the width of the columns
        self.reactionTable.setColumnWidth(0, 150)
        self.reactionTable.setColumnWidth(1, 430)
        self.reactionTable.setColumnWidth(2, 150)

        # Variable to store old value
        self.oldValue = None
        # save if something is changed in the table
        self.reactionTable.itemChanged.connect(self.handleItemChanged)  # saves and updates data
        self.reactionTable.currentItemChanged.connect(self.trackOldValue)

        # Set validators for the numeric columns using a custom delegate class
        self.doubleDelegate = DoubleDelegate(self.reactionTable)

        # Add the table to the layout
        self.layout.addWidget(self.reactionTable)

        # Add Row Button
        self.addRowButton = QPushButton("Add New Reaction")
        self.addRowButton.clicked.connect(self.addReactionRow)
        self.layout.addWidget(self.addRowButton)

        # Ensure the widget can receive focus to detect key presses
        self.setFocusPolicy(Qt.StrongFocus)
        self.setLayout(self.layout)

        # if self.reactionTable.rowCount() == 0: # optinal
        #     self.addReactionRow()

        # import the data from the central data manager to load the saved into the table
        self.importData()

    def addReactionRow(self, data: ReactionDTO | None = None):
        """
        Add a new row to the reaction table
        :param data:
        :return:
        """

        rowPosition: int

        self.addingRowFlag = True

        if data is None or not isinstance(data, ReactionDTO):
            rowPosition = self.reactionTable.rowCount()
            uid = uuid.uuid4().__str__()
            data = ReactionDTO(rowPosition, uid)
            self.centralDataManager.addData('reactionData', data)

        else:
            rowPosition = data.rowPosition

        self.reactionTable.insertRow(rowPosition)

        # the first column should not be editable
        if data.name != "":
            insert = QTableWidgetItem(data.name)
            insert.setForeground(QColor(0, 0, 0))  # make the font color of the full_tomato_case_study black
        else:
            insert = QTableWidgetItem('None')
            insert.setForeground(QColor(0, 0, 0))  # make the font color of the full_tomato_case_study black
            insert.setBackground(QColor(218, 222, 227))  # make the background color of the cell grey
        insert.setFlags(Qt.NoItemFlags)
        self.reactionTable.setItem(rowPosition, 0, insert)


        # the second column should not be editable
        if data.reactionEquation != "":
            insert = QTableWidgetItem(data.reactionEquation)
            insert.setForeground(QColor(0, 0, 0))  # make the font color of the full_tomato_case_study black
        else:
            insert = QTableWidgetItem("No reaction defined")
            insert.setBackground(QColor(218, 222, 227))
        insert.setFlags(Qt.NoItemFlags)
        self.reactionTable.setItem(rowPosition, 1, insert)


        # Create the Edit button and add it to the table
        edit_button = QPushButton("Edit Reaction")
        edit_button.clicked.connect(lambda _, row=rowPosition: self.editReaction(row))
        self.reactionTable.setCellWidget(rowPosition, 2, edit_button)

        self.addingRowFlag = False

    def editReaction(self, row, executeDialog=True):

        # Get the current reaction data for the selected row
        data = self.reactionList[row]

        if executeDialog:
            # Create an instance of the ReactionDialog with the current data
            dialog = ReactionDialog(data, centralDataManager=self.centralDataManager, rowPosition=row)
            dialog.exec_()  # Open the dialog

        # redundant code?
        # # Open the dialog and check if the user accepts (e.g., presses Save)
        #         # if dialog.exc_() == QDialog.Accepted:
        #     self.logger.info("Editing reaction button accepted")

        if data.name != "" and data.reactionEquation != "":
            # properties of the first column the name of the reaction
            insertName = QTableWidgetItem(data.name)
            insertName.setForeground(QColor(0, 0, 0))
            insertName.setFlags(Qt.NoItemFlags)

            # properties of the second column the reaction equation
            insertEquation = QTableWidgetItem(data.reactionEquation)
            insertEquation.setForeground(QColor(0, 0, 0))
            insertEquation.setFlags(Qt.NoItemFlags)

            # update the data in the dialog with the current data
            self.reactionTable.setItem(row, 0, insertName)
            self.reactionTable.setItem(row, 1, insertEquation)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Backspace | Qt.Key_Delete:
            selectedItems = self.reactionTable.selectedItems()
            if selectedItems:
                selectedRow = selectedItems[0].row()  # Get the row of the first selected item
                self.reactionTable.removeRow(selectedRow)
                target = [u for u in self.reactionList if u.rowPosition == selectedRow][0]
                self.reactionList.remove(target)
                for c in [u for u in self.reactionList if u.rowPosition >= selectedRow]:
                    c.updateRow()
        else:
            super().keyPressEvent(event)

    def doubleClickEvent(self, item):
        pass

    def saveData(self):
        # a bit redundant, every time you add/edit a reaction it is automatically saved in the Reaction Dialog class
        pass

    def importData(self):
        """
        Import the data from the central data manager to load the saved data into the table
        """
        if self.reactionList:
            for data in self.reactionList:
                self.addReactionRow(data)


    def contextMenuEvent(self, event):
        """
        Handle the context menu event for the reaction table to delete rows
        :param event: that is a right click event
        :return:
        """
        # Create a context menu
        context_menu = QMenu(self)

        # Add actions for deleting rows from both tables
        deleteAction = context_menu.addAction("Delete Row")

        # Execute the context menu and get the selected action
        action = context_menu.exec_(self.mapToGlobal(event.pos()))

        # Determine which table was clicked
        reaction_pos = self.reactionTable.viewport().mapFrom(self, event.pos())

        if self.reactionTable.geometry().contains(event.pos()) and action == deleteAction:
            # Determine the row that was clicked in the reactants table
            row = self.reactionTable.rowAt(reaction_pos.y())
            if row != -1:
                self.reactionTable.removeRow(row)

            # update the dto list containing the reactions (remove the deleted row, and update the rowPositions)
            self.centralDataManager.updateData('reactionData', row)

    def handleItemChanged(self, item):
        """
        Handle the item changed event for the reaction table in the 1st column
        :param item:
        :return:
        """

        if not self.addingRowFlag and item.column() == 0: # only bothered to track changes in the first column (reaction name)
            rowPosition = item.row()
            for reactionDTO in self.centralDataManager.reactionData:
                if reactionDTO.rowPosition == rowPosition:
                    # get the old and new name of the chemical component
                    oldValue = reactionDTO.oldName
                    newValue = item.text()
                    # Reset old value
                    reactionDTO.oldName = newValue
                    self.updateData(oldValue, newValue)



    def trackOldValue(self, current, previous):
        """Track the old value of the currently selected item."""
        # if current and current.column() == 0:  # Check if the item is in the first row
        #     self.oldValue = current.text()
        # not used anymore the old value is tracked in the reactionDTO
        pass

    def updateData(self, oldReactionName, newReactionName):
        # go over the unit data
        for dto in self.centralDataManager.unitProcessData.values():
            a = dto.name
            # only if it has filled in data, go ahead and modify
            if dto.dialogData and dto.type.value == 2:
                reactions = dto.dialogData['Reactions']
                for reactionTuple in reactions:
                    if oldReactionName == reactionTuple[0]:  # if the old reaction name is used in the unit process
                        index = reactions.index(reactionTuple)
                        reactionTuple = list(reactionTuple)  # Ensure the tuple is mutable
                        reactionTuple[0] = newReactionName
                        reactions[index] = tuple(reactionTuple)  # Convert back to tuple if needed
                        dto.dialogData['Reactions'] = reactions

