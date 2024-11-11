
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableWidget


class CustomTableWidget(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Backspace:
            selectedItems = self.selectedItems()
            if selectedItems:
                selectedRow = selectedItems[0].row()  # Get the row of the first selected item
                self.removeRow(selectedRow)
        else:
            super().keyPressEvent(event)
