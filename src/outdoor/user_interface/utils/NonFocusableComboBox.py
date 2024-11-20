
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QComboBox


class NonFocusableComboBox(QComboBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure the combo box cannot gain focus
        self.setFocusPolicy(Qt.NoFocus)

    # def keyPressEvent(self, event):
    #     event.ignore()
