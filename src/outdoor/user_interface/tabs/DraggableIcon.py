from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import QMimeData, Qt
from PyQt5.QtGui import QDrag

class DraggableIcon(QPushButton):
    """
    A QPushButton subclass that allows the button to be dragged and dropped into the canvas. The button text is used to
    identify the icon type. This class is used to create the icons in the left panel of superstructureMapping Widget.

    """
    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.setCheckable(True)

    def mouseMoveEvent(self, e):
        if e.buttons() != Qt.LeftButton:
            return

        # Start a drag operation when the mouse moves with the left button held down
        drag = QDrag(self)
        mimeData = QMimeData()

        # Use the button's text as the data to be dragged
        mimeData.setText(self.text())
        drag.setMimeData(mimeData)

        drag.exec_(Qt.MoveAction)