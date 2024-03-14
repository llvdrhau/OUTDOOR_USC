# This Python file uses the following encoding: utf-8
import sys
from lca.lca_calc import LCA_Back
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6 import QtCore

# Important:
# You need to run the following command to generate the ui_form.py file
#     pyside6-uic form.ui -o ui_form.py, or
#     pyside2-uic form.ui -o ui_form.py
from ui_form import Ui_OUTDOOR

class OUTDOOR(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_OUTDOOR()
        self.ui.setupUi(self)
        self.lca = LCA_Back("outdoor")

    @QtCore.Slot(name="search_Process")
    def search_Process(self):
        input = self.ui.lineEdit_processSearch.text()
        print(f"searched for {type(input)}")
        res = self.lca.search(term=input)
        self.ui.searchResultList.addItems(res)
        
        print(res)

    # @QtCore.Slot(name="update_SearchResults")
    # def update_SearchResults(self)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = OUTDOOR()
    widget.show()
    sys.exit(app.exec())
