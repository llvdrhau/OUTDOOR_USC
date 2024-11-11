from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton, QLabel


class CalculationWarning(QDialog):
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
        self.setWindowTitle("Are you sure?")
        self.setGeometry(100, 100, 100, 100)  # Adjust size as needed

        self.layout = QVBoxLayout(self)

        warningtext = QLabel("This will activate the calculation process and could take a while. Are you certain you wish to proceed?")
        self.layout.addWidget(warningtext)

        self.okButton = QPushButton("OK", self)
        self.okButton.clicked.connect(self.dataDump)
        self.layout.addWidget(self.okButton)
        self.cancelButton = QPushButton("Cancel", self)
        self.cancelButton.clicked.connect(self.reject)
        self.layout.addWidget(self.cancelButton)

    def dataDump(self):
        self.centralDataManager.dataDump()
        self.accept()
