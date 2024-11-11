from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import QStyledItemDelegate, QLineEdit


class DoubleDelegate(QStyledItemDelegate):
    """
    A delegate class to handle double values in the QTableWidget. This class is used to display and edit double values in
    table widgets.
    """
    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        validator = QDoubleValidator(0.00, 999999.99, 2)
        editor.setValidator(validator)
        return editor

    def setEditorData(self, lineEdit, index):
        value = index.model().data(index, Qt.EditRole)
        lineEdit.setText(str(value))

    def setModelData(self, lineEdit, model, index):
        value = float(lineEdit.text())
        model.setData(index, value, Qt.EditRole)
