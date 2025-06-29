from PyQt5.QtWidgets import QPushButton, QDialog

from outdoor.user_interface.data.OutdoorDTO import OutdoorDTO
from outdoor.user_interface.dialogs.LCADialog import LCADialog


class LcaButton(QPushButton):
    def __init__(self, parent, data: OutdoorDTO):
        super().__init__(parent)
        self.data = data

    def lcaAction(self):
        dialog = LCADialog(self.data)
        result = dialog.exec_()

        if result == QDialog.Rejected or result == QDialog.Accepted:
            self.changeColorBnt()

    def changeColorBnt(self):
        if self.data.calculated:
            self.setText("Calculated")
            # color green
            self.setStyleSheet("background-color: #0000FF")
        elif len(self.data.LCA['exchanges']) > 0:
            self.setText("Defined")
            # color red
            self.setStyleSheet("background-color: #00FF00")
        else:
            self.setText("Not Defined")
            self.setStyleSheet("background-color: #FF0000")
        # self.setEnabled(True)
        # self.setStyleSheet("background-color: #00FF00")
