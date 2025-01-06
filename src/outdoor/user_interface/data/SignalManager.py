from PyQt5.QtCore import QObject, pyqtSignal  # needed to emmit signals

class SignalManager(QObject):
    # Signal that is emitted when outputList changes
    outputListUpdated = pyqtSignal()
    inputListUpdated = pyqtSignal()

    def __init__(self, centralDataManager):
        super().__init__()

        self._inputList: list[str] = []
        self._outputList: list[str] = []
        self.centralDataManager = centralDataManager


    @property
    def outputList(self):
        return self._outputList

    @outputList.setter
    def outputList(self, new_list):
        self._outputList = new_list
        # Emit the signal to indicate that the list has been updated
        self.outputListUpdated.emit()

    @property
    def inputList(self):
        return self._inputList

    @inputList.setter
    def inputList(self, new_list):
        self._inputList = new_list
        # Emit the signal
        self.inputListUpdated.emit()

    def importLists(self):
        for unit in self.centralDataManager.unitProcessData.values():
            if unit.type.value == 7:
                self._outputList.append(unit.name)
            elif unit.type.value == 0:
                self._inputList.append(unit.name)

