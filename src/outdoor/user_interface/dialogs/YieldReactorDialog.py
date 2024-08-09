from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel, QWidget, QTableWidget, QTabWidget, \
    QApplication, QHBoxLayout, QTableWidgetItem, QFormLayout, QComboBox, QFrame, QToolTip
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDoubleValidator, QFont, QCursor, QIntValidator

from outdoor.user_interface.dialogs.PhysicalProcessDialog import PhysicalProcessesDialog

class YieldReactorDialog(PhysicalProcessesDialog):
    def __init__(self, initialData, centralDataManager):
        super().__init__(initialData, centralDataManager)  # Initialize the parent class
        # Additional initialization for YieldReactorDialog

        tabWidget = self.tabWidget
        tabWidget.addTab(self._createYieldTab(), "Yeild Reaction")


    def _createYieldTab(self):
        # Cost Related Factors Tab
        widget = QWidget()
        layout = QFormLayout()

        self._createSectionTitle(text="Yield Reaction Tab", layout=layout)

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
        self.yieldFactor.setValidator(QDoubleValidator(0.00, 999999.99, 2))
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
