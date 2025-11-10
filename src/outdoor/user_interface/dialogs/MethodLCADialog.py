from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton

class MethodologyDialog(QDialog):
    def __init__(self, centralDataManager):
        super().__init__()
        self.centralDataManager = centralDataManager
        self.setWindowTitle("Select LCA Methodology")
        self.setFixedWidth(420)
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

        self.selection = None  # will hold the final method choice

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Choose methodology for this calculation:"))

        self.combo = QComboBox()
        # Visible labels (what the user sees)
        self.options = [
            "ReCiPe 2016 v1.03 (default)",
            "ReCiPe 2016 v1.03 [bio=1] (custom: biogenic = fossil)",
            "IPCC 2013",
        ]
        self.combo.addItems(self.options)
        layout.addWidget(self.combo)

        # buttons
        btn_row = QHBoxLayout()
        btn_ok = QPushButton("OK")
        btn_cancel = QPushButton("Cancel")
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_ok)
        layout.addLayout(btn_row)

        btn_ok.clicked.connect(self._accept)
        btn_cancel.clicked.connect(self.reject)

    def _accept(self):
        self.selection = self.combo.currentText()
        self.centralDataManager.methodSelectionLCA = self.selection
        self.accept()

    def use_biogenic_as_one(self) -> bool:
        """Return True if custom [bio=1] is chosen."""
        return self.selection is not None and self.selection.startswith("ReCiPe 2016 v1.03 [bio=1]")
