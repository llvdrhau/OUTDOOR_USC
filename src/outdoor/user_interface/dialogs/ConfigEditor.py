from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel, QTableWidget, QTableWidgetItem, \
    QGroupBox, QCheckBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDoubleValidator


class ConfigEditor(QDialog):
    def __init__(self, centralDataManager, parent=None):
        super().__init__()
        self.centralDataManager = centralDataManager
        print(centralDataManager.calc_configs())
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
        self.setWindowTitle("Calculations to Perform")
        self.setGeometry(100, 100, 400, 300)  # Adjust size as needed

        self.layout = QVBoxLayout(self)
        self.calctypes = self.centralDataManager.calc_configs()

        self.dumpButton = QPushButton("Dump")
        self.dumpButton.clicked.connect(self.dataDump)

        confbox = self._enableTypes()
        self.layout.addWidget(confbox)
        self.layout.addWidget(self.dumpButton)


    def collectData(self):
        pass

    def populateInputDialog(self, data):
        pass

    def dataDump(self):
        self.centralDataManager.dataDump()
    def _enableTypes(self):
        typegroup = QGroupBox("Calculations")
        typesBoxLayout = QVBoxLayout()
        types = ['Cost', 'Utility Consumption', 'Heating', 'Concentration', 'LCA']
        self.checks = {}
        for i in types:
            checkbox = QCheckBox(i, self)
            checkbox.setObjectName(i)
            if i in self.calctypes:
                if self.calctypes[i] == 'True':
                    checkbox.setChecked(True)
                else:
                    checkbox.setChecked(False)
                checkbox.setObjectName(i)
            else:
                self.calctypes[i] = 'False'
            typesBoxLayout.addWidget(checkbox)
            self.checks[i] = checkbox

        self.savebutton = QPushButton("Save")
        self.savebutton.clicked.connect(self.save_changes)
        typesBoxLayout.addWidget(self.savebutton)
        typegroup.setLayout(typesBoxLayout)
        return typegroup

    def save_changes(self):
        for i in self.checks.keys():
            self.calctypes[i] = str(self.checks[i].isChecked())

        self.centralDataManager.updateConfigs(self.calctypes)




