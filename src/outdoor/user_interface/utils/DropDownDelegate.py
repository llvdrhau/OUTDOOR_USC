
from PyQt5.QtWidgets import QComboBox, QStyledItemDelegate
from PyQt5.QtCore import Qt

class DropDownDelegate(QStyledItemDelegate):
    """
    A delegate class to handle drop-down lists in the QTableWidget. This class is used to display and edit drop-down lists
    in table widgets.
    """
    def __init__(self, items, parent=None):
        super().__init__(parent)
        self.items = ['1','2']

    def createEditor(self, parent, option, index):
        editor = QComboBox(parent)
        editor.addItems(self.items)
        return editor

    def setEditorData(self, comboBox, index):
        value = index.model().data(index, Qt.EditRole)
        comboBox.setCurrentText(value)

    def setModelData(self, comboBox, model, index):
        value = comboBox.currentText()
        model.setData(index, value, Qt.EditRole)
