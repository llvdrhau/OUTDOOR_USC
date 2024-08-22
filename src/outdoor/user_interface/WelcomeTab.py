from PyQt5.QtGui import QFontDatabase, QFont, QPixmap, QIntValidator
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QPushButton, QLabel, QTableWidgetItem, QDialog, \
    QTabWidget, QGroupBox, QCheckBox, QLineEdit, QFormLayout, QComboBox
from PyQt5.QtCore import Qt, QRect
from outdoor.user_interface.dialogs.ConfigEditor import ConfigEditor


class WelcomeTab(QWidget):
    def __init__(self, centralDataManager, parent=None):
        super().__init__(parent)
        self.centralDataManager = centralDataManager
        self.layout = QVBoxLayout(self)

        # Add a custom font from a file
        self.fontId = QFontDatabase.addApplicationFont("Merienda-VariableFont_wght.ttf")
        self.fontFamily = QFontDatabase.applicationFontFamilies(self.fontId)[0]
        self.titleFont = QFont(self.fontFamily, 44, QFont.Bold)

        # Set the title with a larger font
        self.titleLabel = QLabel("OUTDOOR")
        self.titleLabel.setFont(self.titleFont)
        self.titleLabel.setAlignment(Qt.AlignCenter)  # Center the title

        # Load and display the logo image
        self.logoLabel = QLabel()
        self.logoPixmap = QPixmap("outdoor/user_interface/logo.png")
        # Resize the pixmap to the desired size while maintaining aspect ratio
        self.scaledLogoPixmap = self.logoPixmap.scaled(500, 500, Qt.KeepAspectRatio,
                                                       Qt.SmoothTransformation)  # Adjust (200, 200) to desired dimensions
        self.logoLabel.setPixmap(self.scaledLogoPixmap)
        self.logoLabel.setAlignment(Qt.AlignCenter)  # Center the logo

        # Set some descriptive text with a regular font
        self.descFont = QFont("Arial", 10)
        self.descLabel = QLabel("Welcome to OUTDOOR, your open source process simulator. "
                                "Here you can create, simulate, and optimize your industrial processes with ease.")
        self.descLabel.setFont(self.descFont)
        self.descLabel.setWordWrap(True)
        self.descLabel.setAlignment(Qt.AlignCenter)  # Center the text

        # Add widgets to the layout
        self.layout.addWidget(self.titleLabel)
        self.layout.addWidget(self.logoLabel)
        self.layout.addWidget(self.descLabel)
