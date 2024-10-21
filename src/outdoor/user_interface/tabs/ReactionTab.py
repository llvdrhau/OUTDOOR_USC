import uuid

from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QPushButton, QLabel, QTableWidgetItem, QDialog, QMenu
from PyQt5.QtCore import Qt

from outdoor.user_interface.data.ReactionDTO import ReactionDTO
from outdoor.user_interface.utils.DoubleDelegate import DoubleDelegate
from outdoor.user_interface.dialogs.ReactionDialog import ReactionDialog


class ReactionsTab(QWidget):
    """
    This class creates a tab to define the reactions that will be used in the simulation. It allows the user to define
    the reactants and products of each reaction, as well as the stoichiometry of each component in the reaction.
    """

    def __init__(self, centralDataManager, parent=None):
        super().__init__(parent)
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
        self.columnsList = [
            "Reaction Name", "Reaction Equation", "Edit button"
        ]
        self.reactionTable.setHorizontalHeaderLabels(self.columnsList)

        # adjust the width of the columns
        self.reactionTable.setColumnWidth(0, 150)
        self.reactionTable.setColumnWidth(1, 430)
        self.reactionTable.setColumnWidth(2, 150)

        self.reactionTable.itemDoubleClicked.connect(self.doubleClickEvent)

        # Set validators for the numeric columns using a custom delegate class
        self.doubleDelegate = DoubleDelegate(self.reactionTable)

        # Add the table to the layout
        self.layout.addWidget(self.reactionTable)

        # Add Row Button
        self.addRowButton = QPushButton("Add New Reaction")
        self.addRowButton.clicked.connect(self.addReactionRow)
        self.layout.addWidget(self.addRowButton)

        # save button not needed, reaction is saved automatically when edited
        # Save button setup
        # self.okButton = QPushButton("Save")
        # self.okButton.clicked.connect(self.saveData)
        # self.layout.addWidget(self.okButton)

        # Ensure the widget can receive focus to detect key presses
        self.setFocusPolicy(Qt.StrongFocus)
        self.setLayout(self.layout)
        self.importData()
        if self.reactionTable.rowCount() == 0:
            self.addReactionRow()

    def addReactionRow(self, data: ReactionDTO | None = None):
        rowPosition: int

        if data is None or not isinstance(data, ReactionDTO):
            rowPosition = self.reactionTable.rowCount()
            uid = uuid.uuid4().__str__()
            data = ReactionDTO(rowPosition, uid)
            self.centralDataManager.addData('reactionData', data)
            # self.reactionList.append(data)

        else:
            rowPosition = data.rowPosition

        self.reactionTable.insertRow(rowPosition)

        # the first column should not be editable
        insert = QTableWidgetItem('None')
        insert.setFlags(Qt.NoItemFlags)
        self.reactionTable.setItem(rowPosition, 0, insert)


        # the second column should not be editable
        insert = QTableWidgetItem("No reaction defined")
        insert.setBackground(QColor(218, 222, 227))
        insert.setFlags(Qt.NoItemFlags)
        self.reactionTable.setItem(rowPosition, 1, insert)


        # Create the Edit button and add it to the table
        edit_button = QPushButton("Edit Reaction")
        edit_button.clicked.connect(lambda _, row=rowPosition: self.editReaction(row))
        self.reactionTable.setCellWidget(rowPosition, 2, edit_button)

    def editReaction(self, row):
        # Get the current reaction data for the selected row
        data = self.reactionList[row]

        # Create an instance of the ReactionDialog with the current data
        dialog = ReactionDialog(data, centralDataManager=self.centralDataManager, rowPosition=row)

        # Open the dialog and check if the user accepts (e.g., presses Save)
        if dialog.exec_() == QDialog.Accepted:
            updated_data = dialog.dto  # Get the updated data from the dialog

            # Update the data in the reaction list and update the table if needed
            self.reactionList[row] = updated_data

            # Optionally update the table UI with new values
            self.reactionTable.setItem(row, 0, QTableWidgetItem(updated_data.reaction_name))
            self.reactionTable.setItem(row, 1, QTableWidgetItem(updated_data.reaction_equation))

        if data.name != "" and data.reactionEquation != "":
            # update the data in the dialog with the current data
            self.reactionTable.setItem(row, 0, QTableWidgetItem(data.name))
            self.reactionTable.setItem(row, 1, QTableWidgetItem(data.reactionEquation))

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
        pass
        # a bit redundant, every time you add/edit a reaction it is automatically saved.
        # self.collectData()
        # Save the data to the central data manager
        # self.centralDataManager.addData("reactionData", self.reactionList)

        # Change the border of OK button to green
        # print('debugging')
        # self.okButton.setStyleSheet("border: 2px solid green;")

    def collectData(self):
        pass

    def sortComponentDTO(self, dto: ReactionDTO):
        return dto.rowPosition

    def importData(self):
       pass


    def contextMenuEvent(self, event):
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




