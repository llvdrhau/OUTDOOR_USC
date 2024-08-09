from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel, QWidget, QTableWidget, QTabWidget, \
    QApplication, QHBoxLayout, QTableWidgetItem, QFormLayout, QComboBox, QFrame, QToolTip
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDoubleValidator, QFont, QCursor, QIntValidator

from outdoor.user_interface.dialogs.PhysicalProcessDialog import PhysicalProcessesDialog

class StoichiometricReactorDialog(PhysicalProcessesDialog):
    def __init__(self, initialData, centralDataManager):
        super().__init__(initialData, centralDataManager)  # Initialize the parent class
        # Additional initialization for StoichiometricReactorDialog

        tabWidget = self.tabWidget
        tabWidget.addTab(self._createStoichiometricDialogTab(), "Stoichiometric")

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

        # create subtitel
        self._createSectionTitle(text="Reactants", layout=layout)


        # create table for the components
        self.reactantsTable = QTableWidget(0, 4, self)  # Initial rows, columns
        self.reactantsTable.setHorizontalHeaderLabels(["Reactant Name", "Stoichiometric",
                                                                      "Conversion Factor","Reaction Number"])
        self.reactantsTable.setColumnWidth(0, 200)  # make column 1 wider
        self.reactantsTable.setColumnWidth(1, 200)  # make column 2 wider
        self.reactantsTable.setColumnWidth(2, 200)  # make column 3 wider
        self.reactantsTable.setColumnWidth(3, 200)  # make column 4 wider

        #  add the tabel to the widget
        tooltipText = """define the stoichiometric factors for the reactants (on a mass bassis! g/g), their conversion factors and to what
                               reaction number them belong to. Numbers needed to distinguish between reactions"""
        self._addRowWithTooltip(layout, labelText="Components:", widget=self.reactantsTable,
                                tooltipText=tooltipText)
        self.reactantsTable.setSelectionBehavior(QTableWidget.SelectRows)  # Row selection
        self.reactantsTable.setSelectionMode(QTableWidget.SingleSelection)  # Single row at a time
        self.reactantsTable.setObjectName("reactantsTable")

        # Add a row to tabel button
        self.addRowButtonReactantsTable = QPushButton("Add Component", self)
        self.addRowButtonReactantsTable.clicked.connect(self._addRowToTable)
        # set object name
        self.addRowButtonReactantsTable.setObjectName("addRowButtonReactantsTable")
        layout.addWidget(self.addRowButtonReactantsTable)
        # Initialize the table with an example row (optional)
        self._addRowToTable(tabName="reactantsTable")

        # creat subtitel for Products of the reaction
        self._createSectionTitle(text="Products", layout=layout)

        # create table for the components
        self.productsTable = QTableWidget(0, 3, self)  # Initial rows, columns
        self.productsTable.setHorizontalHeaderLabels(["Component Name", "Stoichiometric", "Reaction Number"])
        self.productsTable.setColumnWidth(0, 200)  # make column 1 wider
        self.productsTable.setColumnWidth(1, 200)  # make column 2 wider
        self.productsTable.setColumnWidth(2, 200) # make column 3 wider
        #  add the tabel to the widget
        tooltipText = """The chemicals that are produced. define stoichiometric factors (mass! g/g) for the products and
         to what reaction number them belong to. Numbers needed to distinguish between reactions."""
        # add same table to the layout
        self._addRowWithTooltip(layout, labelText="Components:", widget=self.productsTable, tooltipText=tooltipText)
        self.productsTable.setSelectionBehavior(QTableWidget.SelectRows)  # Row selection
        self.productsTable.setSelectionMode(QTableWidget.SingleSelection)  # Single row at a time
        self.productsTable.setObjectName("productsTable")

        # add row button
        self.addRowButtonProductsTable = QPushButton("Add Component", self)
        self.addRowButtonProductsTable.clicked.connect(self._addRowToTable)
        # set object name
        self.addRowButtonProductsTable.setObjectName("addRowButtonProductsTable")
        layout.addWidget(self.addRowButtonProductsTable)
        # Initialize the table with an example row (optional)
        self._addRowToTable(tabName="productsTable")

        # return the widget
        widget.setLayout(layout)
        return widget
