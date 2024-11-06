from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel, QWidget, QTableWidget, QTabWidget, \
    QApplication, QHBoxLayout, QTableWidgetItem, QFormLayout, QComboBox, QFrame, QToolTip, QMenu
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDoubleValidator, QFont, QCursor, QIntValidator, QColor

from outdoor.user_interface.dialogs.PhysicalProcessDialog import PhysicalProcessesDialog, ProcessType
from outdoor.user_interface.data.ProcessDTO import ProcessDTO

class StoichiometricReactorDialog(PhysicalProcessesDialog):
    def __init__(self, initialData, centralDataManager, iconID):
        super().__init__(initialData, centralDataManager, iconID)  # Initialize the parent class
        # Additional initialization for StoichiometricReactorDialog
        self.UnitType = ProcessType.STOICHIOMETRIC

        # List of reactions that are in the dialog
        self.reactionIDs = []

        #self.tabWidget = self.tabWidget # in the parent class
        self.tabWidget.addTab(self._createStoichiometricDialogTab(), "Reactions")

        # populate the dialog with existing data (initialData) if it is not empty
        if initialData.dialogData: # if the dialogData is not empty then populate the dialog with the data
            # Populate the reaction table with the initial data if it exists
            # the other data is populated in the parent class
            self._populateReactionTable(initialData.dialogData)

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

        # create text to explain the tab using a QLabel
        self.reactionDescription = QLabel(self)
        textExplanation = ("This tab allows you to define the reactions that take place in the unit operation.\n"
                           "You can also define the conversion efficiency of the main reactant in %.")

        self.reactionDescription.setText(textExplanation)
        layout.addRow(self.reactionDescription)



        # create a table for the reactions
        self.reactionTableUnitProcess = QTableWidget()
        self.reactionTableUnitProcess.setColumnCount(4)
        self.reactionTableUnitProcess.setHorizontalHeaderLabels(["Reaction Name", "Reaction", "Conversion (%)", "Reactant"])
        self.reactionTableUnitProcess.setColumnWidth(0, 150)
        self.reactionTableUnitProcess.setColumnWidth(1, 300)
        self.reactionTableUnitProcess.setColumnWidth(2, 100)
        self.reactionTableUnitProcess.setColumnWidth(3, 100)


        layout.addWidget(self.reactionTableUnitProcess)


        # Add Row Button for Products Table
        addButton = QPushButton("Add Reaction", self)
        addButton.clicked.connect(self._addReactionRow)
        layout.addWidget(addButton)

        # return the widget
        widget.setLayout(layout)
        return widget


    def _addReactionRow(self, data=None):
        # Add a new row to the reaction Table
        rowPosition = self.reactionTableUnitProcess.rowCount()
        self.reactionTableUnitProcess.insertRow(rowPosition)

        # Create a drop-down for reactions
        reactionComboList = QComboBox()
        reactionComboList.addItems(self.getReactionList())  # Populate the combo box with allowed chemicals
        # initialising the combo box with the first item ""
        reactionComboList.setCurrentIndex(-1)
        self.updateReactionString(rowPosition)
        self.reactionTableUnitProcess.setCellWidget(rowPosition, 0, reactionComboList)

        # Connect the signal to the update function
        reactionComboList.currentIndexChanged.connect(lambda: self.updateReactionString(rowPosition))
        reactionComboList.currentIndexChanged.connect(lambda: self.updateReactantList(rowPosition))


        # the second column is for the reaction string should not be editable
        insert = QTableWidgetItem("No reaction given")
        insert.setBackground(QColor(218, 222, 227))
        insert.setFlags(Qt.NoItemFlags)
        self.reactionTableUnitProcess.setItem(rowPosition, 1, insert)

        # the third column is for the conversion efficiency should be editable
        lineEdit = QLineEdit()
        validator = QDoubleValidator(0.0, 100, 2)  # Values between 0 and 100, up to 2 decimal places
        validator.setNotation(QDoubleValidator.StandardNotation)
        lineEdit.setValidator(validator)
        lineEdit.setText("100")
        self.reactionTableUnitProcess.setCellWidget(rowPosition, 2, lineEdit)

        # the fourth column is for the reactant that is the main reactant which has a specific conversion efficiency
        # is a drop down list of the chemical reactants of the reaction
        reactantsComboList = QComboBox()
        # updateReactantList(rowPosition)
        # reactantsComboList.addItems()  # Populate the combo box with allowed chemicals
        self.reactionTableUnitProcess.setCellWidget(rowPosition, 3, reactantsComboList)

        if data:
            # Populate columns for stoichiometric table if data given
            self.reactionTableUnitProcess.cellWidget(rowPosition, 0).setCurrentText(data[0])
            self.reactionTableUnitProcess.cellWidget(rowPosition, 2).setText(data[1])
            self.reactionTableUnitProcess.cellWidget(rowPosition, 3).setCurrentText(data[2])
            # update the reaction table so reactions are displayed correctly in colum 1
            self.updateReactionString(rowPosition)  # method is in the stoichiometricReactorDialog.py file


    def getReactionList(self):
        # Get the list of reactions from the central data manager
        reactionDTOs = self.centralDataManager.reactionData
        return [reaction.name for reaction in reactionDTOs]

    def getReactantList(self, reactionName):
        # Get the list of reactions from the central data manager
        reactionDTOs = self.centralDataManager.reactionData
        for reaction in reactionDTOs:
            if reaction.name == reactionName:
                return reaction.reactants

    def getProductList(self, reactionName):
        # Get the list of reactions from the central data manager
        # horrendously inefficient but it works for now
        reactionDTOs = self.centralDataManager.reactionData
        for reaction in reactionDTOs:
            if reaction.name == reactionName:
                return reaction.products


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

    def updateReactantList(self, row):
        # get the name of the reaction selected
        comboBox = self.reactionTableUnitProcess.cellWidget(row, 0)
        if comboBox and isinstance(comboBox, QComboBox):
            # Get the selected reaction name
            reactionName = comboBox.currentText()
            reactantsComboList = self.reactionTableUnitProcess.cellWidget(row, 3)
            reactantsComboList.clear()
            reactantsComboList.addItems(self.getReactantList(reactionName))

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


    def collectData(self):
        # First, call the parent's collectData to collect the common data
        dialogData = super().collectData()
        dialogData['Reactions'] = self._collectDataStoich()['Reactions']

        return dialogData

    def _collectDataStoich(self):
        """
        Collects the data from the dialog and saves it to the central data manager. Use existing methods to collect data
        and add elements not yet implemented in the parent class (PhysicalProcessesDialog).
        :return:
        """

        # collect the data from the dialog
        dialogDataReactions = {}
        # collect the data from the reaction table
        reactions = []
        for row in range(self.reactionTableUnitProcess.rowCount()):
            reactionName = self.reactionTableUnitProcess.cellWidget(row, 0).currentText()
            conversion = self.reactionTableUnitProcess.cellWidget(row, 2).text()
            reactant = self.reactionTableUnitProcess.cellWidget(row, 3).currentText()
            reactions.append((reactionName, conversion, reactant))

        dialogDataReactions['Reactions'] = reactions

        return dialogDataReactions


    def _populateReactionTable(self, dialogData):
        """
        Populates the reaction table with the given reactions.
        :param reactions: A list of tuples containing the reaction name, conversion efficiency, and reactant.
        """
        reactionData = dialogData['Reactions']
        for rowData in reactionData:
            self._addReactionRow(rowData)

    def _addFoundComponents(self):
        """
        Adds incoming components to the specified table. In this case the products of reactions need to be added
        to the components table.
        :param tableName: The name of the table to which the components will be added.
        """
        super()._addFoundComponents()
        # Add incoming components to the reaction table, these will also be leaving the process

        # Retive the reactions from the current dialog
        referenceFlowType = self._getReferenceFlowType()

        if "Exiting" in referenceFlowType:
            # get the products of the reactions if the exiting flow is selected because these chemicals are in the
            # exiting flow now and should be added to the table

            # loop over the reactions table and get the reaction names
            products = []
            for row in range(self.reactionTableUnitProcess.rowCount()):
                reactionName = self.reactionTableUnitProcess.cellWidget(row, 0).currentText()
                # get the reactants of the reaction
                products += self.getProductList(reactionName)


            # if its already in the table don't add it again
            table, _ = self._findTable()
            chemicalsFromTable = self._collectTableData(table)

            # Remove the chemicals that are already in the filledInChemicals using set difference
            chemicalsSet = set(products)  # Convert to set for efficient lookup, also removes duplicates
            chemicalsFromTableSet = set(chemicalsFromTable)  # Convert table data to set

            # Perform set difference to find chemicals that are not in chemicalsFromTable
            products = list(chemicalsSet - chemicalsFromTableSet)

            # add the chemicals to the components table
            if products:
                for component in products:
                    self._addRowToTable(componentName=component)










