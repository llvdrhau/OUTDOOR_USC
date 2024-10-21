from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel, QWidget, QTableWidget, QTabWidget, \
    QApplication, QHBoxLayout, QTableWidgetItem, QFormLayout, QComboBox, QFrame, QToolTip, QMenu
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDoubleValidator, QFont, QCursor, QIntValidator, QColor

from outdoor.user_interface.dialogs.PhysicalProcessDialog import PhysicalProcessesDialog

class StoichiometricReactorDialog(PhysicalProcessesDialog):
    def __init__(self, initialData, centralDataManager):
        super().__init__(initialData, centralDataManager)  # Initialize the parent class
        # Additional initialization for StoichiometricReactorDialog

        tabWidget = self.tabWidget
        tabWidget.addTab(self._createStoichiometricDialogTab(), "Reactions")

        # populate the dialog with existing data (initialData) if it is not empty
        if initialData:
            self.populateDialog(initialData)

        self.setFocusPolicy(Qt.StrongFocus)

    def _createStoichiometricDialogTab(self):
        """
        Creates and returns a QWidget containing UI elements for configuring the stoichiometric reactor.
        """


        # initialise widget
        widget = QWidget()
        layout = QFormLayout()

        # Create a title for the tab
        self._createSectionTitle(text="Reaction Tab", layout=layout)

        # create a table for the reactions
        self.reactionTableUnitProcess = QTableWidget()
        self.reactionTableUnitProcess.setColumnCount(2)
        self.reactionTableUnitProcess.setHorizontalHeaderLabels(["Reaction Name", "Reaction"])
        self.reactionTableUnitProcess.setColumnWidth(0, 150)
        self.reactionTableUnitProcess.setColumnWidth(1, 300)

        layout.addWidget(self.reactionTableUnitProcess)


        # Add Row Button for Products Table
        addButton = QPushButton("Add Reaction", self)
        addButton.clicked.connect(self.addReactionRow)
        layout.addWidget(addButton)

        # return the widget
        widget.setLayout(layout)
        return widget


    def addReactionRow(self):
        # Add a new row to the reaction Table
        rowPosition = self.reactionTableUnitProcess.rowCount()
        self.reactionTableUnitProcess.insertRow(rowPosition)

        # Create a drop-down for reactions
        reactantCombo = QComboBox()
        reactantCombo.addItems(self.getReactionList())  # Populate the combo box with allowed chemicals
        self.reactionTableUnitProcess.setCellWidget(rowPosition, 0, reactantCombo)

        # Connect the signal to the update function
        reactantCombo.currentIndexChanged.connect(lambda: self.updateReactionString(rowPosition))

        # the second column is for the reaction string should not be editable
        insert = QTableWidgetItem("No reaction given")
        insert.setBackground(QColor(218, 222, 227))
        insert.setFlags(Qt.NoItemFlags)
        self.reactionTableUnitProcess.setItem(rowPosition, 1, insert)


    def getReactionList(self):
        # Get the list of reactions from the central data manager
        reactionDTOs = self.centralDataManager.reactionData
        return [reaction.name for reaction in reactionDTOs]

    def updateReactionString(self, row):
        """
        Updates the reaction string based on the selected item from the drop-down in the given row.
        """
        # Get the combo box from the specified row and column 0
        comboBox = self.reactionTableUnitProcess.cellWidget(row, 0)
        if comboBox and isinstance(comboBox, QComboBox):
            # Get the selected reaction name
            reactionName = comboBox.currentText()

            reactionEq = "No reaction found"
            # Generate a sample reaction string. You can modify this logic based on your actual requirements.
            for reactionDTO in self.centralDataManager.reactionData:
                if reactionDTO.name == reactionName:
                    reactionEq = reactionDTO[3]

            # Update the corresponding reaction cell (column 1)
            reaction_item = self.reactionTableUnitProcess.item(row, 1)
            if reaction_item:
                reaction_item.setText(reactionEq)


    def contextMenuEvent(self, event):
        # Create a context menu
        context_menu = QMenu(self)

        # Add actions for deleting rows from both tables
        deleteAction = context_menu.addAction("Delete Row")

        # Execute the context menu and get the selected action
        action = context_menu.exec_(self.mapToGlobal(event.pos()))

        # Determine which table was clicked
        component_pos = self.reactionTableUnitProcess.viewport().mapFrom(self, event.pos())

        if self.reactionTableUnitProcess.geometry().contains(event.pos()) and action == deleteAction:
            # Determine the row that was clicked in the reactants table
            row = self.reactionTableUnitProcess.rowAt(component_pos.y())
            if row != -1:
                self.reactionTableUnitProcess.removeRow(row)

            # todo handel the data when deleeting a row
            # update the dto list containing the chemical components
            #self.centralDataManager.updateData('UnitProcess', row)




