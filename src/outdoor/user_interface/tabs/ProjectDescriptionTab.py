import uuid
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QPushButton, QLabel, QTableWidgetItem,
                             QDialog, QMenu, QTextEdit)
from PyQt5.QtCore import Qt
from src.outdoor.user_interface.utils.OutdoorLogger import outdoorLogger
import logging

class ProjectDescriptionTab(QWidget):
    """
    This class creates a tab for entering a description of the project.
    It features a text box that can be edited with a professional look.
    """

    def __init__(self, centralDataManager, parent=None):
        super().__init__(parent)
        # add the logger
        self.logger = outdoorLogger(name="outdoor_logger", level=logging.DEBUG)

        self.centralDataManager = centralDataManager

        self.setStyleSheet("""
            QWidget {
                background-color: #f2f2f2;
            }
            QLabel {
                color: #333333;
                font-size: 18px;
                font-weight: bold;
            }
            QTextEdit {
                border: 1px solid #cccccc;
                border-radius: 5px;
                padding: 10px;
                background-color: #ffffff;
                selection-background-color: #b0daff;
                font-size: 14px;
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
        """)

        self.layout = QVBoxLayout(self)

        # Title for the component tab
        self.title = QLabel("Project Description")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setFixedHeight(50)
        self.layout.addWidget(self.title)

        # Text box for project description
        self.description = QTextEdit()
        self.layout.addWidget(self.description)
        self.description.setFixedHeight(600)

        # Optional: Add a button to save or submit the description
        self.saveButton = QPushButton("Save Description")
        self.layout.addWidget(self.saveButton)
        self.saveButton.clicked.connect(self.saveDescription)

        # import is there is any description saved
        self.importData()

    def saveDescription(self):
        description_text = self.description.toPlainText()
        self.centralDataManager.projectDescription = description_text
        # Implement the save functionality here, for example:
        self.logger.info("Project Description saved")

    def importData(self):
        if self.centralDataManager.projectDescription:
            self.description.setText(self.centralDataManager.projectDescription)
        else:
            descriptionText = "Enter a description of the project here."
            self.description.setText(descriptionText)
            self.logger.info("Default Project Description added")
