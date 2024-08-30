from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel, QTableWidget, QTableWidgetItem, \
    QGroupBox, QCheckBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDoubleValidator


class ConfigEditor(QDialog):
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
        self.setWindowTitle("Configuration Editor")
        self.setGeometry(100, 100, 400, 300)  # Adjust size as needed

        self.layout = QVBoxLayout(self)
        self.calctypes = self.centralDataManager.configs["calcConfigs"]
        self.componentTypes = self.centralDataManager.configs["componentConfigs"]
        self.dumpButton = QPushButton("Dump")
        self.dumpButton.clicked.connect(self.dataDump)

        confbox = self._enableTypes()
        self.layout.addWidget(confbox)

        compbox = self._enableStructureComponents()
        self.layout.addWidget(compbox)

        self.savebutton = QPushButton("Save")
        self.savebutton.clicked.connect(self.save_changes)

        self.layout.addWidget(self.savebutton)
        self.layout.addWidget(self.dumpButton)

    def dataDump(self):
        self.centralDataManager.dataDump()
    def _enableTypes(self):
        typegroup = QGroupBox("Calculations")
        typesBoxLayout = QVBoxLayout()
        types = ['Cost', 'Utility Consumption', 'Heating', 'Concentration', 'LCA', 'Stoichiometry']
        self.calcChecks = {}
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
            self.calcChecks[i] = checkbox
        typegroup.setLayout(typesBoxLayout)
        return typegroup

    def _enableStructureComponents(self):
        typegroup = QGroupBox("Superstructure Components")
        typesBoxLayout = QVBoxLayout()
        types = ['Physical Process', 'Stoichiometric Reactor', 'Yield Reactor', 'Generator (Elec)', 'Generator (Heat)', 'LCA']
        self.componentChecks = {}
        for i in types:
            checkbox = QCheckBox(i, self)
            checkbox.setObjectName(i)
            if i in self.componentTypes:
                if self.componentTypes[i] == 'True':
                    checkbox.setChecked(True)
                else:
                    checkbox.setChecked(False)
                checkbox.setObjectName(i)
            else:
                self.componentTypes[i] = 'False'
            typesBoxLayout.addWidget(checkbox)
            self.componentChecks[i] = checkbox
        typegroup.setLayout(typesBoxLayout)
        return typegroup

    def save_changes(self):
        for i in self.calcChecks.keys():
            self.calctypes[i] = str(self.calcChecks[i].isChecked())
        for i in self.componentChecks.keys():
            self.componentTypes[i] = str(self.componentChecks[i].isChecked())
        update = {}
        update['calcConfigs'] = self.calctypes
        update['componentConfigs'] = self.componentTypes
        self.centralDataManager.updateConfigs(update)




