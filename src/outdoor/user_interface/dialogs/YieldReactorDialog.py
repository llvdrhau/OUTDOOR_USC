from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel, QWidget, QTableWidget, QTabWidget, \
    QApplication, QHBoxLayout, QTableWidgetItem, QFormLayout, QComboBox, QFrame, QToolTip
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDoubleValidator, QFont, QCursor, QIntValidator

from outdoor.user_interface.dialogs.PhysicalProcessDialog import PhysicalProcessesDialog, ProcessType

class YieldReactorDialog(PhysicalProcessesDialog):
    def __init__(self, initialData, centralDataManager, iconID):
        super().__init__(initialData, centralDataManager, iconID)  # Initialize the parent class
        # Additional initialization for YieldReactorDialog
        self.UnitType = ProcessType.YIELD

        # Add Yield Reaction Tab to the tab widget of the parent class
        self.tabWidget.addTab(self._createYieldTab(), "Yield Reaction")

        if initialData.dialogData:
            self._populateYieldTab(initialData.dialogData)


    def _createYieldTab(self):
        # Cost Related Factors Tab
        widget = QWidget()
        layout = QFormLayout()

        self._createSectionTitle(text="Yield Reaction Tab", layout=layout)

        # add a description
        description = QLabel("The Yield Reaction tab is used to define the yield of the reactor. The yield is the "
                             "\nfraction of the input mass that is converted to the targeted product. You can also "
                             "select chemicals that do to get converted, i.e. that are Inert \n"
                             "---------   Product = Yield Factor * (Input Mass - Inert Mass)   ---------")
        description.setWordWrap(True)
        layout.addRow(description)

        # Reference Flow type
        self.product = QComboBox(self)
        # add options to ComboBox
        chemicalNames = self.centralDataManager.getChemicalComponentNames()
        self.product.addItems(chemicalNames)
        self.product.setObjectName("product")

        tooltipText = """ What products is made in the yield reactor"""

        self._addRowWithTooltip(layout, labelText="Product", widget=self.product,
                                tooltipText=tooltipText)


        # Reference Flow input
        self.yieldFactor = QLineEdit(self)
        self.yieldFactor.setValidator(QDoubleValidator(0.00, 1.00, 3))
        # set object name
        self.yieldFactor.setObjectName("yieldFactor")

        tooltipText = """The yield of all input mass to the targeted product [0, 1]."""
        self._addRowWithTooltip(layout, labelText="Yield Factor", widget=self.yieldFactor, tooltipText=tooltipText)

        # Components table
        # layout.addWidget(QLabel("Components:"))
        self.inertComponentsTable = QTableWidget(0, 1, self)  # Initial rows, columns
        self.inertComponentsTable.setHorizontalHeaderLabels(["Component Name"])
        self.inertComponentsTable.setColumnWidth(0, 200)  # make column 1 wider

        # add the table to the layout
        tooltipText = """The chemicals species that do not participate in the reaction (are thus excluded)."""
        self._addRowWithTooltip(layout, labelText="Inert Chemicals", widget=self.inertComponentsTable,
                                tooltipText=tooltipText)

        # make selectable, so rows can be deleted by pressing the delete key
        self.inertComponentsTable.setSelectionBehavior(QTableWidget.SelectRows)  # Row selection
        self.inertComponentsTable.setSelectionMode(QTableWidget.SingleSelection)  # Single row at a time
        self.inertComponentsTable.setObjectName("inertComponentsTable")

        # Add a row to tabel button
        self.addRowButton = QPushButton("Add Component", self)
        self.addRowButton.clicked.connect(self._addRowToTable)
        # set object name
        self.addRowButton.setObjectName("addRowButtonYieldTable")
        layout.addWidget(self.addRowButton)
        # Initialize the table with an example row (optional)
        self._addRowToTable(tabName="yield")

        widget.setLayout(layout)
        return widget


    def collectData(self):
        # First, call the parent's collectData to collect the common data
        dialogData = super().collectData()
        dialogDataYield = self._collectDataYield()
        # add dialogDataYield to dialogData
        dialogData.update(dialogDataYield)

        return dialogData

    def _collectDataYield(self):
        """
        Collects the data from the dialog and saves it to the central data manager. Use existing methods to collect data
        and add elements not yet implemented in the parent class (PhysicalProcessesDialog).
        :return:
        """


        # collect the data from the dialog
        product = self.product.currentText()
        yieldFactor = self.yieldFactor.text()

        # handeling empty strings
        if yieldFactor == "":
            yieldFactor = 0
        else:
            yieldFactor = float(yieldFactor)

        inertComponents = []
        for row in range(self.inertComponentsTable.rowCount()):
            cellText = self.inertComponentsTable.cellWidget(row, 0).currentText()
            inertComponents.append(cellText)

        # add the data to the dictionary

        dialogDataYield ={'Product': product,
                           'Yield Factor': yieldFactor,
                           'Inert Components': inertComponents}


        return dialogDataYield


    def _populateYieldTab(self, dialogData):
        """
        Populates the reaction table with the given reactions.
        :param reactions: A list of tuples containing the reaction name, conversion efficiency, and reactant.
        """
        # Populate the Yield tab
        self.product.setCurrentText(dialogData['Product'])
        self.yieldFactor.setText(str(dialogData['Yield Factor']))
        for component in dialogData['Inert Components']:
            self._addRowToTable(tabName="yield", componentName=component)
