
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel, QHBoxLayout


class SplittingDialog(QDialog):
    """
    Opens a dialog to set the splitting parameters for the split icon. The dialog allows the user to set the number of
    exit ports and the splitting ratio for each exit port.
    """
    def __init__(self, initialData):
        super().__init__()
        self.setWindowTitle("Splitting Parameters")
        self.setGeometry(100, 100, 400, 300)  # Adjust size as needed

        layout = QVBoxLayout(self)

        # define the amount of exit ports
        layout.addWidget(QLabel("Number of exit ports:"))
        self.nExitPorts = QLineEdit(self)
        layout.addWidget(self.nExitPorts)
        # Set validator to restrict to floating-point numbers
        self.nExitPorts.setValidator(QDoubleValidator(2, 10, 0))

        # Splitting Ratio
        # this is a placeholder for now, you can add more fields as needed,
        # should acttualy be a table with the splitting ratio for each exit port and specifiying the components that are
        # split
        layout.addWidget(QLabel("Splitting Ratio:"))
        self.splittingRatio = QLineEdit(self)
        layout.addWidget(self.splittingRatio)
        # Set validator to restrict to floating-point numbers
        self.splittingRatio.setValidator(QDoubleValidator(0.00, 1.00, 2))

        # OK and Cancel buttons
        buttonsLayout = QHBoxLayout()
        self.okButton = QPushButton("OK", self)
        self.okButton.clicked.connect(self.accept)
        buttonsLayout.addWidget(self.okButton)

        self.cancelButton = QPushButton("Cancel", self)
        self.cancelButton.clicked.connect(self.reject)
        buttonsLayout.addWidget(self.cancelButton)

        layout.addLayout(buttonsLayout)

        if initialData:
            self.populateDialog(initialData)

    def collectData(self):
        """Collect data from all fields to save state."""
        data = {
            'splittingRatio': self.splittingRatio.text(),
            'nExitPorts': self.nExitPorts.text(),
        }
        return data

    def populateDialog(self, data):
        """
        Populate the dialog with the data provided in the dictionary.
        The keys in the dictionary should match the names of the widgets.
        :param data: Dictionary with the data to populate the dialog with
        """
        # Directly settable fields
        if 'splittingRatio' in data:
            self.splittingRatio.setText(data['splittingRatio'])
        if 'nExitPorts' in data:
            self.nExitPorts.setText(data['nExitPorts'])
