from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton, QLabel, QLineEdit, QComboBox, QFormLayout


class CalculationSetup(QDialog):
    def __init__(self, centralDataManager, parent=None):
        super().__init__()
        self.centralDataManager = centralDataManager
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
        self.setWindowTitle("Calculation Setup")
        self.setGeometry(100, 100, 100, 100)  # Adjust size as needed

        self.layout = QFormLayout(self)

        #Combo box for the optimization mode
        self.opti_combo = QComboBox(self)
        self.opti_combo.addItems(
            ["Single", "Multi-Objective", "Sensitivity", "Cross-Parameter Sensitivity",
             "2-Stage-Recourse", "Multi-2-Stage-Recourse"])
        self.layout.addRow([QLabel("Optimization Mode:"), self.opti_combo])

        #Combo box for the objective function
        self.objective_combo = QComboBox(self)
        self.objective_combo.addItems(
            ["Earnings Before Income Taxes", "Net Production Costs", "Net Produced CO2 Emissions",
             "Cross-Parameter Sensitivity",
             "Freshwater Demand"])
        self.layout.addRow([QLabel("Objective Function:"), self.objective_combo])

        self.okButton = QPushButton("OK", self)
        self.okButton.clicked.connect(self.dataDump)
        self.layout.addWidget(self.okButton)
        self.cancelButton = QPushButton("Cancel", self)
        self.cancelButton.clicked.connect(self.reject)
        self.layout.addWidget(self.cancelButton)

    def save_setup(self):
        pass

    def load_all_setups(self):
        pass

    def apply_setup(self):
        pass

    def dataDump(self):
        self.centralDataManager.dataDump()
        self.accept()


