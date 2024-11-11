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

        if result == QDialog.Rejected:
            if self.data.calculated:
                self.setText("Defined")
            else:
                self.setText("Not Defined")
