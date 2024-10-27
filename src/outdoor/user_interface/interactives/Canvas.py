import uuid

from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsObject, QGraphicsItem, \
    QApplication, QMessageBox, QGraphicsPathItem
from PyQt5.QtCore import QRectF, Qt, QPointF
from PyQt5.QtGui import QPainter, QPen, QColor, QPainterPath, QFont, QPainterPathStroker

from outdoor.user_interface.dialogs.InputParametersDialog import InputParametersDialog
from outdoor.user_interface.dialogs.OutputParametersDialog import OutputParametersDialog
from outdoor.user_interface.dialogs.PhysicalProcessDialog import PhysicalProcessesDialog
from outdoor.user_interface.dialogs.SplittingDialog import SplittingDialog
from outdoor.user_interface.dialogs.StoichiometricReactorDialog import StoichiometricReactorDialog
from outdoor.user_interface.dialogs.YieldReactorDialog import YieldReactorDialog
from outdoor.user_interface.dialogs.GeneratorDialog import GeneratorDialog
from outdoor.user_interface.dialogs.LCADialog import LCADialog


class Canvas(QGraphicsView):
    """
    A widget (QGraphicsView) for the right panel where icons can be dropped onto it. Here is where the user can create
    the superstructure by dragging and dropping icons from the left panel. This class also handles the connections between
    the icons.
    """

    def __init__(self, centralDataManager, iconLabels):
        super().__init__()
        # Store the icon data manager for use in the widget
        self.centralDataManager = centralDataManager
        # store the icon labels
        self.iconLabels = iconLabels
        # Set up the scene for scalable graphics
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)  # For better visual quality
        # Enable drag and drop events
        self.setAcceptDrops(True)
        # To keep a reference to the currently selected icon
        self.selectedElement = None

        self.setStyleSheet("background-color: white;")
        self.iconData = {}  # Add this line to store dialog data
        # add index to icons according to the type of icon:
        # use UUIDs for the indexs!
        self.index_input = []
        self.index_process = []
        self.index_split = []
        self.index_output = []
        self.UUID = None

        # track the start and end points of the line
        self.startPoint = None
        self.endPoint = None
        self.currentLine = None
        self.drawingLine = False
        self.endPort = None
        self.startPort = None

        self.setMouseTracking(True)  # Enable mouse tracking

        # Define scale factors for zooming
        self.zoomInFactor = 1.25  # Zoom in factor (25% larger)
        self.zoomOutFactor = 1 / self.zoomInFactor  # Zoom out factor (inverse of zoom in)
        self.scaleFactor = 1.0  # Initial scale factor

    def wheelEvent(self, event):
        # Get the angle delta of the wheel event
        angleDelta = event.angleDelta().y()
        if angleDelta > 0:
            # Wheel scrolled up, zoom in
            self.scaleView(self.zoomInFactor)
        else:
            # Wheel scrolled down, zoom out
            self.scaleView(self.zoomOutFactor)

    def scaleView(self, scaleFactor):
        # Apply the scale factor to the view
        factor = self.transform().scale(scaleFactor, scaleFactor).mapRect(QRectF(0, 0, 1, 1)).width()
        if factor < 0.07 or factor > 100:
            # Prevent zooming out too much or zooming in too much
            return

        self.scale(scaleFactor, scaleFactor)
        self.scaleFactor *= scaleFactor

    def dragEnterEvent(self, e):
        print('Iniciate dragging icon')
        e.accept()

    def dragMoveEvent(self, event):
        #print("Drag Move Event")
        event.accept()

    def dropEvent(self, event):
        print('dropped icon')
        mimeData = event.mimeData()
        if mimeData.hasText():
            # Extract the necessary information from the MIME data
            text = mimeData.text()
            position = event.pos()
            scenePos = self.mapToScene(position)
            # get the correct icon type based on the text
            icon = self.createMovableIcon(text, event.pos())

            # Set the icon's position to the mouse cursor's position
            icon.setPos(scenePos)
            self.scene.addItem(icon)  # Add the created icon to the scene
            event.accept()

    def createMovableIcon(self, text, position):
        """
        This method should create a new instance of MovableIcon or similar class based on the text
        :param text: (string) The text of the icon to identify the type
        :param position: QPoint position of the mouse click
        :return:
        """

        # Mapping of text to icon_type and index
        icon_map = {
            "Boolean Distributor": ("bool_split", self.index_split),
            "Distributor": ("distributor_split", self.index_split),

            "Input": ("input", self.index_input),
            "Output": ("output", self.index_output),
            "LCA": ("lca", self.index_process),

            "Physical Process": ("physical_process", self.index_process),
            "Stoichiometric Reactor": ("stoichiometric_reactor", self.index_process),
            "Yield Reactor": ("yield_reactor", self.index_process),

            "Generator": ("generator", self.index_process),
        }

        # Check if the text is in the icon_map
        if text in icon_map:
            icon_type, index_list = icon_map[text]
            # Create unique UUID
            UUID = uuid.uuid4().__str__()
            index_list.append(UUID)
            # Create MovableIcon
            iconWidget = MovableIcon(text, centralDataManager=self.centralDataManager, iconID=UUID, icon_type=icon_type)
            iconWidget.setPos(self.mapToScene(position))
            return iconWidget
        else:
            # Raise error if the icon type is not recognized
            raise Exception("Icon type not recognized")  # You can handle this error in a more user-friendly way

    def mouseMoveEvent(self, event):
        if self.currentLine is not None:
            # Map the mouse position to scene coordinates
            scenePos = self.mapToScene(event.pos())
            # Update the current line's endpoint to follow the mouse
            # This is where you need to adjust for the InteractiveLine class
            self.currentLine.endPoint = scenePos
            self.currentLine.updateAppearance()  # Redraw the line with the new end point

            # If you have any other behavior when moving the mouse, handle it here
        else:
            # Not drawing a line, so pass the event to the base class
            super().mouseMoveEvent(event)

    def startLine(self, port, pos):
        """
        Start drawing a new line from the given port (function called in the IconPort class)
        :param port: IconPort object or TriangleIconPorts object
        :param pos: Position of the mouse click
        :return:
        """
        if port.occupied:
            # do not start a new line if the port is already connected
            return
        else:
            if 'split' not in port.iconType and port.portType == 'exit' and len(port.connectionLines) > 0:
                # the port of an icon that is not a split icon and is an exit port is now occupied only one
                # stream can leave. The extra if statement is to avoid the case where the line was deleted
                # and no longer exists
                port.occupied = True
                # stop the line drawing process with return statement
                return

            # Start drawing a new line from this port
            print('iniciating start line')
            self.startPort = port
            self.startPoint = pos  # Always corresponds to the exit port
            self.currentLine = InteractiveLine(startPoint=pos, endPoint=pos,
                                               startPort=port)  # QGraphicsLineItem(QLineF(pos, pos))
            port.connectionLines.append(self.currentLine)
            self.scene.addItem(self.currentLine)

    def endLine(self, port, pos):
        """
        End drawing a new line from the given port (function called in the IconPort class)
        :param port: IconPort object or TriangleIconPorts object
        :param pos: Position of the mouse click
        :return:
        """
        # Do not start a new line if the startPort is not set error has occured
        if self.startPort is None:
            return

        # Do not end a new line in a port that is already occupied
        if port.occupied:
            return

        if 'split' in port.iconType and port.portType == 'entry' and len(port.connectionLines) > 0:
            port.occupied = True
            # stop the line drawing process with return statement
            return

        print('initiating end line')
        #port.connectionLines.append(self.currentLine)
        self.endPort = port
        self.endPoint = pos  # allways corresponds to the entry port
        # Here you might want to validate if the startPort and endPort can be connected
        print(self.currentLine)
        print(self.startPort != self.endPort)
        if self.currentLine and self.startPort != port:
            self.currentLine.endPoint = pos  # Update the end point
            self.currentLine.endPort = port  # Update the end port
            self.currentLine.updateAppearance()  # Update the line appearance based on its current state
            port.connectionLines.append(self.currentLine)
            self.centralDataManager.addConnection(self.startPort, port, self.startPoint, pos, self.currentLine)

        # rest the positions and switches to None
        self.startPoint = None
        self.endPoint = None
        self.currentLine = None
        self.drawingLine = False

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Backspace:
            for item in self.scene.selectedItems():
                if isinstance(item, MovableIcon):
                    for port in item.ports:
                        #port.occupied = False
                        for line in port.connectionLines:
                            # remove the line from the port object
                            line.startPort.connectionLines.remove(line)
                            # update the occupancy of the port to False
                            line.startPort.occupied = False
                            # remove the line from the port object
                            line.endPort.connectionLines.remove(line)
                            # update the occupancy of the port to False
                            line.endPort.occupied = False

                            # remove the line from the scene
                            self.scene.removeItem(line)
                    self.scene.removeItem(item)

                    # TODO, update any necessary data in the centralDataManager here
                    #self.centralDataManager.removeIconData(item.iconID)

        super().keyPressEvent(event)

    def mousePressEvent(self, event):
        """
        This method is called when the mouse is pressed in the canvas. It is used to deselect icons and lines when
        pressing on an empty space in the canvas.
        :param event: click event
        :return: updates the selected element
        """
        item = self.itemAt(event.pos())

        if isinstance(item, MovableIcon):
            if self.selectedElement is not None and self.selectedElement != item:
                # If there is a previously selected icon and it's not the current item, reset its pen
                self.selectedElement.pen = QPen(Qt.black, 1)

                if isinstance(self.selectedElement, InteractiveLine):
                    self.selectedElement.setSelectedLine(
                        False)  # switch off visibility of the control point for the line
                    self.selectedElement.updateAppearance()

                else:
                    self.selectedElement.update()

            # Update the currently selected icon
            self.selectedElement = item

        elif isinstance(item, InteractiveLine):
            if self.selectedElement is not None and self.selectedElement != item:
                # If there is a previously selected icon and it's not the current item, reset its pen
                self.selectedElement.pen = QPen(Qt.black, 1)
                if isinstance(self.selectedElement, InteractiveLine):
                    self.selectedElement.setSelectedLine(
                        False)  # switch off visibility of the control point for the line
                    self.selectedElement.updateAppearance()
                else:
                    self.selectedElement.update()

            # Update the currently selected icon
            self.selectedElement = item

        elif isinstance(item, ControlPoint):
            pass

        else:  # if the selected element is an icon or a line, reset the pen
            if self.selectedElement is not None:
                # If there is a previously selected line, reset its pen
                self.selectedElement.pen = QPen(Qt.black, 1)

                if isinstance(self.selectedElement, InteractiveLine):
                    self.selectedElement.setSelectedLine(
                        False)  # switch off visibility of the control point for the line
                    self.selectedElement.updateAppearance()
                elif isinstance(self.selectedElement, MovableIcon):
                    self.selectedElement.update()

                self.selectedElement = None  # Reset the currently selected icon

        super().mousePressEvent(event)


class IconPort(QGraphicsEllipseItem):
    """
    A QGraphicsEllipseItem subclass to represent the entry and exit ports of the icons. This class handles the connection
    of lines between the ports.
    """

    def __init__(self, parent, portType, iconID, pos=None):
        super().__init__(-5, -5, 10, 10, parent)  # A small circle
        self.portType = portType  # 'entry' or 'exit'
        self.iconID = iconID
        self.setBrush(Qt.black)
        self.connectionLines = []  # List to store the lines connected to this iconPort
        self.occupied = False  # Flag to indicate if the port is already connected to a line
        self.iconType = parent.icon_type

        if pos:
            self.setPos(pos)  # Set the position if it was passed (for split icons)
        else:
            # Position the port correctly on the parent icon based on portType
            match portType:
                case 'exit':
                    self.setPos(parent.boundingRect().width(), parent.boundingRect().height() / 2)
                case 'entry':
                    self.setPos(0, parent.boundingRect().height() / 2)

    def mousePressEvent(self, event):
        """
        Clicking on an exit port starts drawing a line from it
        """
        if event.button() == Qt.LeftButton and self.portType == 'exit':
            canvas = self.scene().views()[0]  # Get the first (and likely only) view
            if isinstance(canvas, Canvas):  # Check if it's actually your Canvas class
                canvas.startLine(self, event.scenePos())

    def mouseReleaseEvent(self, event):
        """
        The line is drawn from the exit port to the entry port
        """
        if self.portType == 'entry':
            canvas = self.scene().views()[0]  # Get the first (and likely only) view
            if isinstance(canvas, Canvas):  # Check if it's actually your Canvas class
                canvas.endLine(self, event.scenePos())

    def updateConnectedLines(self, centralDataManager):
        """
        Update the position of the lines connected to this port (function called in the Canvas class) when the port is
        moved. or that is when the icon is moved.
        :param centralDataManager:
        :return:
        """
        if self.connectionLines:
            # Loop through all lines connected to this port
            for line in self.connectionLines:
                # Update the position of the line's start or end, depending on the port's type
                if self.portType == "exit":
                    # If this is an exit port, update the line's start position
                    line.setStartPoint(self.scenePos())
                else:
                    # If this is an entry port, update the line's end position
                    line.setEndPoint(self.scenePos())

                # Redraw the line with its new position
                line.updateAppearance()

                # Optionally, TODO update any necessary data in the centralDataManager here
                # For example, you might update the stored positions of the line's endpoints
                # if you are tracking those for any reason (not shown in this example).


class MovableIcon(QGraphicsObject):
    """
    A QGraphicsObject subclass to represent the icons that can be dragged and dropped onto the canvas. This class also
    handles the ports of the icons. The icon type is used to determine the number and position of the ports. This class
    is used to create the icons in the canvas and makes them draggable, handels their appearance and opens dialogos.
    """

    def __init__(self, text, centralDataManager, icon_type, iconID=None):
        super().__init__()


        self.text = text
        # make a map of abbreviations to full names of the icons
        self.iconAbbreviation = {'Input': 'Input',
                                 'Output': 'Output',
                                 'Physical Process': 'Phy. Process',
                                 'Stoichiometric Reactor': 'Stoi. Reactor',
                                 'Yield Reactor': 'Yield Reactor',
                                 'Generator (Elec)': 'Gen. (Elec)',
                                 'Generator (Heat)': 'Gen. (Heat)',
                                 'Generator': 'Generator',
                                 'Boolean Distributor': 'Bool Distr.',
                                 'Distributor': 'Distr.',
                                 'LCA': 'LCA'}


        self.icon_type = icon_type
        self.iconID = iconID
        self.centralDataManager = centralDataManager  # to Store and handel dialog data for each icon

        # set the flags for the icon to be movable and selectable
        self.setFlags(QGraphicsObject.ItemIsMovable)  # Enable the movable flag
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)  # Enable item change notifications
        self.setFlag(QGraphicsItem.ItemIsSelectable)  # Enable the selectable flag

        self.dragStartPosition = None

        # initiation of port logic
        self.activeStreams = [True, False, False] # stream 1 is always active

        self.pen = QPen(Qt.black, 1)  # Default pen for drawing the border
        #self.penBoarder = QPen(Qt.NoPen)
        # define the ports:
        self.ports = []
        match icon_type:
            case 'input':
                self.ports.append(IconPort(self, portType='exit', iconID=iconID))
            case 'output':
                self.ports.append(IconPort(self, portType='entry', iconID=iconID))
            case 'bool_split':
                self.addSplitPorts()
            case 'distributor_split':
                self.addSplitPorts()

            # otherwise give port for entry and exit
            case _:
                self.ports.append(IconPort(self, portType='exit', iconID=iconID))
                self.ports.append(IconPort(self, portType='entry', iconID=iconID))

    def addSplitPorts(self):
        # Add an entry port
        entryPort = IconPort(self, portType='entry', iconID=self.iconID,
                             pos=QPointF(0, self.boundingRect().height() / 2))
        self.ports.append(entryPort)

        # Add exit ports
        exitPort = IconPort(self, pos=QPointF(self.boundingRect().width(), self.boundingRect().height() / 2),
                            portType='exit', iconID=self.iconID)
        self.ports.append(exitPort)


    def updateExitPorts(self, nExitPortsNew):
        # Calculate the new step size
        hightTriangle = self.boundingRect().height()
        step = hightTriangle / (nExitPortsNew + 1)

        if nExitPortsNew > self.nExitPorts:
            # Add new ports if the new count is greater than the existing number of ports
            # Update positions of existing ports
            existingPorts = [port for port in self.childItems() if
                             isinstance(port, IconPort) and port.portType == 'exit']
            minPorts = min(len(existingPorts), nExitPortsNew)
            for i in range(minPorts):
                hightPosition = step * (i + 1)
                existingPorts[i].setPos(QPointF(self.boundingRect().width(), hightPosition))

            # Add new ports if the new count is greater than the existing number of ports
            for i in range(len(existingPorts), nExitPortsNew):
                hightPosition = step * (i + 1)
                newPorts = IconPort(self, QPointF(self.boundingRect().width(), hightPosition), 'exit')
                self.ports.append(newPorts)
            # update the number of exit ports
            self.nExitPorts = nExitPortsNew
        else:
            # Remove ports if the new count is less than the existing number of ports
            # Remove existing exit ports
            for port in self.childItems():
                if isinstance(port, IconPort) and port.portType == 'exit':
                    self.scene().removeItem(port)
                    del port

            # Recalculate positions and add new exit ports
            hightTriangle = self.boundingRect().height()
            step = hightTriangle / (nExitPortsNew + 1)
            for n in range(nExitPortsNew):
                hightPosition = step * (n + 1)
                exitPort = IconPort(self, portType='exit', pos=QPointF(self.boundingRect().width(), hightPosition),
                                    iconID=self.iconID)
                self.ports.append(exitPort)

            # update the number of exit ports
            self.nExitPorts = nExitPortsNew

    def boundingRect(self):
        if 'split' in self.icon_type:
            return QRectF(0, 0, 60, 60)
        else:
            return QRectF(0, 0, 120, 40)

    def paint(self, painter, option, widget=None):

        if 'split' in self.icon_type:
            # Set background color based on the icon type
            backgroundColor = QColor(self.getBackgroundColor(self.icon_type))
            painter.setBrush(backgroundColor)

            # Create a QPainterPath object
            path = QPainterPath()
            path.moveTo(0, 30)
            path.lineTo(60, 60)
            path.lineTo(60, 0)
            path.closeSubpath()

            # Draw the triangle
            painter.fillPath(path, painter.brush())
            painter.setPen(self.pen)
        else:
            # Set background color based on the icon type
            backgroundColor = QColor(self.getBackgroundColor(self.icon_type))
            painter.setBrush(backgroundColor)
            painter.setPen(self.pen)
            painter.drawRoundedRect(self.boundingRect(), 10, 10)

            painter.setPen(Qt.black)
            font = QFont("Arial", 10)
            painter.setFont(font)

            # get the start name of the icon from the map
            iconText = self.iconAbbreviation.get(self.text, self.text)
            painter.drawText(self.boundingRect(), Qt.AlignCenter, iconText)

    def getBackgroundColor(self, icon_type):
        if icon_type == 'input':
            return "#a8d5e2"  # pastel blue (a bit darker than the original)

        elif icon_type == 'output':
            return "#ffdab9"  # pastel peach (more distinct from orange)

        elif icon_type == 'physical_process':
            return "#f7c6d9"  # pastel pink (distinct from the other colors)

        elif icon_type == 'stoichiometric_reactor':
            return "#c8e6c9"  # pastel green (slightly different)

        elif icon_type == 'yield_reactor':
            return "#d4b3ff"  # pastel lavender (more distinguishable from pink)

        elif icon_type == 'generator_elec':
            return "#fff4a3"  # pastel yellow (brighter but still soft)

        elif icon_type == 'generator_heat':
            return "#ffb3b3"  # pastel soft red (more vibrant but still light)

        elif icon_type == 'generator':
            return "#fff4a3"  # pastel yellow (brighter but still soft)

        elif icon_type == 'bool_split':
            return "#ffd1dc"  # pastel rose (different from light red)

        elif icon_type == 'distributor_split':
            return "#b2f2bb"  # pastel mint green (to distinguish from green)

        # if none of the above, return a gray color
        return "#D3D3D3"

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Change the pen color to indicate the icon is selected black
            self.pen = QPen(QColor("red"), 2)  # 3 is the width of the pen
            self.update()  # Update the icon's appearance
            self.setCursor(Qt.ClosedHandCursor)
            self.dragStartPosition = event.pos()

        super().mousePressEvent(event)  # Ensure the event is propagated

    def mouseMoveEvent(self, event):
        if not self.dragStartPosition:
            return
        dragDistance = (event.pos() - self.dragStartPosition).manhattanLength()
        if dragDistance >= QApplication.startDragDistance():
            # Calculate the new position
            newPos = event.scenePos() - self.dragStartPosition
            self.setPos(newPos)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.setCursor(Qt.OpenHandCursor)
        self.dragStartPosition = None
        super().mouseReleaseEvent(event)  # Ensure the event is propagated

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            if 'split' in self.icon_type:
                # self.openSplittingDialog()
                pass
            else:
                self.openParametersDialog()

    # methods to manage the positions of lines between the icons
    def itemChange(self, change, value):
        if change == QGraphicsObject.ItemPositionHasChanged:
            for port in self.childItems():
                if hasattr(port, 'updateConnectedLines'):
                    port.updateConnectedLines(self.centralDataManager)
        return super().itemChange(change, value)


    def openParametersDialog(self):
        """
        Handles the data entered by the user after pressing OK for the icon parameters dialog
        :return:
        """

        # Retrieve existing data for this icon
        existingData = self.centralDataManager.unitProcessData.get(self.iconID,
                                                        {})  # if the iconID is not in the dict, return an empty dict

        # choose the dialog to open based on the type of icon that was double clicked
        if self.icon_type == 'input':
            dialog = InputParametersDialog(initialData=existingData, centralDataManager=self.centralDataManager, iconID=self.iconID)

        elif self.icon_type == 'output':
            dialog = OutputParametersDialog(initialData=existingData, centralDataManager=self.centralDataManager, iconID=self.iconID)

        elif self.icon_type == 'physical_process':
            dialog = PhysicalProcessesDialog(initialData=existingData, centralDataManager=self.centralDataManager, iconID=self.iconID)

        elif self.icon_type == 'stoichiometric_reactor':
            dialog = StoichiometricReactorDialog(initialData=existingData, centralDataManager=self.centralDataManager, iconID=self.iconID)

        elif self.icon_type == 'yield_reactor':
            dialog = YieldReactorDialog(initialData=existingData, centralDataManager=self.centralDataManager,
                                        iconID=self.iconID)

        elif self.icon_type == 'generator':
             dialog = GeneratorDialog(initialData=existingData, centralDataManager=self.centralDataManager,
                                      iconID=self.iconID)


        elif self.icon_type == 'lca':
            dialog = LCADialog(initialData=existingData)

        else:
            raise Exception("Icon type {} not recognized".format(self.icon_type))  # You can handle this error in a more user-friendly way


        # open the dialog and handle the data entered by the user after pressing OK
        if dialog.exec_():
            unitDTO = self.centralDataManager.unitProcessData[self.iconID]

            try:
                newSourceName = unitDTO.name
            except:
                newSourceName = ''

            if newSourceName:
                self.text = newSourceName  # Update the text attribute to reflect the new source name
                self.update()  # Update the icon's appearance i.e., repaint the icon name

            # update the outlet port of the icon based on the dialog data
            if unitDTO.type != 0 or unitDTO.type == 7: # not input or output
                stream2 = unitDTO.dialogData['Check box stream 2']
                stream3 = unitDTO.dialogData['Check box stream 3']
                activeStreamsList = [True, stream2, stream3] # stream 1 is always active
                self.updateIconExitPorts(activeStreamsList)




            print("{} Dialog accepted".format(self.icon_type))
        else:
            print("{} Dialog canceled".format(self.icon_type))

    def updateIconExitPorts(self, ports2Active: list):
        """
        Updates the exit ports of the icon based on the provided list of active ports.
        Adds or removes exit ports as needed.
        :param ports2Active: A list with boolean values indicating if each stream (port) should be active.
        """
        # Calculate the new step size
        heightIcon = self.boundingRect().height()
        widthIcon = self.boundingRect().width()

        # Loop through the ports2Active list and compare it with self.activeStreams
        for index, shouldBeActive in enumerate(ports2Active):
            # If the port should be active but is not currently active, add it
            if shouldBeActive and not self.activeStreams[index]:
                # Calculate the position for the new port
                if index == 1:
                    # Port 2 (upper port)
                    x = widthIcon / 2
                    y = 0

                elif index == 2:
                    # Port 3 (lower port)
                    x = widthIcon / 2
                    y = heightIcon
                else:
                    continue  # Stream 1 is always active and has already been added

                # Create and add the new port
                newPort = IconPort(self, pos=QPointF(x, y), portType='exit', iconID=self.iconID)
                self.ports.append(newPort)
                self.activeStreams[index] = True

            # If the port should not be active but is currently active, remove it
            elif not shouldBeActive and self.activeStreams[index]:
                # Find and remove the corresponding port
                for port in self.ports:
                    if isinstance(port, IconPort) and port.portType == 'exit':
                        portPos = port.pos()
                        if ((index == 1 and portPos == QPointF(widthIcon / 2, 0)) or
                            (index == 2 and portPos == QPointF(widthIcon / 2, heightIcon))):
                            # Remove the port from the scene
                            self.scene().removeItem(port)
                            self.ports.remove(port)
                            del port
                            break

                # Update activeStreams list
                self.activeStreams[index] = False

        # Update the icon after modifications
        self.update()


class ControlPoint(QGraphicsEllipseItem):
    """
    A QGraphicsEllipseItem subclass to represent the control point for curved lines. This class is used to create the
    control points when a line is curved and allows the user to adjust the curve by moving the control point.
    """

    def __init__(self, x, y, parent=None):
        super().__init__(-5, -5, 10, 10, parent)  # A small circle as the control point
        self.setBrush(QColor(255, 0, 0))  # Red color
        self.setFlag(QGraphicsEllipseItem.ItemIsMovable)
        self.setFlag(QGraphicsEllipseItem.ItemSendsGeometryChanges)
        self.setFlag(QGraphicsItem.ItemIsFocusable)  # Enable focus

        self.setPos(x, y)  # Set initial position

    def itemChange(self, change, value):
        if change == QGraphicsEllipseItem.ItemPositionHasChanged and self.parentItem():
            self.parentItem().updateAppearance()  # Update the line's appearance when the control point is moved, the methode is in the InteractiveLine class (the parent)
        return super().itemChange(change, value)


class InteractiveLine(QGraphicsPathItem):
    """
    This class is used to create the lines between the icons. It allows the user to draw straight or curved lines by
    double-clicking on the line to toggle between the two modes. The control point for curved lines is only shown when
    the line is curved and selected.
    """

    def __init__(self, startPoint, endPoint, startPort=None, endPort=None, parent=None):
        super().__init__(parent)
        self.startPoint = startPoint
        self.endPoint = endPoint
        self.isCurved = False  # Line starts as straight
        self.controlPoint = None  # Control point is not created until needed
        self.startPort = startPort
        self.endPort = endPort

        # set Flags
        # self.setAcceptHoverEvents(True)  # Enable hover events
        # self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsFocusable)  # Enable focus

        self.selected = True  # Track selection state
        self.pen = QPen(Qt.black, 1)  # Default pen for drawing the line
        self.updateAppearance()

    def setStartPoint(self, point):
        self.startPoint = point
        self.updateAppearance()

    def setEndPoint(self, point):
        self.endPoint = point
        self.updateAppearance()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # The user clicked on the line
            self.setSelectedLine(not self.selected)  # Select the line

            if self.selected:
                self.pen = QPen(Qt.red, 1.5)  # Increase line thickness
            else:
                self.pen = QPen(Qt.black, 1)

            self.updateAppearance()  # Update appearance

        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        self.isCurved = not self.isCurved  # Toggle between curved and straight line
        if self.isCurved and not self.controlPoint:
            # Create and add the control point only if transitioning to curved for the first time
            midPoint = QPointF((self.startPoint.x() + self.endPoint.x()) / 2,
                               (self.startPoint.y() + self.endPoint.y()) / 2)
            self.controlPoint = ControlPoint(midPoint.x(), midPoint.y(), self)

        self.updateAppearance()
        super().mouseDoubleClickEvent(event)

    def setSelectedLine(self, selected):
        self.selected = selected
        if self.isCurved and self.controlPoint:
            self.controlPoint.setVisible(self.selected)
        elif not self.isCurved and self.controlPoint:
            self.controlPoint.setVisible(False)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Backspace and self.selected:
            # Delete the line if the Backspace key is pressed while the line is selected
            self.scene().removeItem(self)
            self.setSelectedLine(False)

            # reset the occupied flag of the start and end port
            self.startPort.occupied = False
            self.endPort.occupied = False

            # deleet the line from the connectionLines list of the ports
            self.startPort.connectionLines.remove(self)
            self.endPort.connectionLines.remove(self)

            # todo remove the line from the data dict as well, from the centralDataManager

        super().keyPressEvent(event)

    def updateAppearance(self):
        path = QPainterPath(self.startPoint)
        if self.isCurved and self.controlPoint:
            # Use the control point's current position for the curve
            controlPos = self.controlPoint.pos()
            path.quadTo(controlPos, self.endPoint)
        else:
            path.lineTo(self.endPoint)

        self.setPath(path)
        self.setPen(self.pen)

    def shape(self):
        # Override shape method to return a wider hitbox
        stroker = QPainterPathStroker()
        stroker.setWidth(10)  # Set the hitbox width to be larger than the line width
        return stroker.createStroke(self.path())

    # def hoverEnterEvent(self, event):
    #     # Show the control point when hovering, but only if the line is curved
    #     if self.isCurved and self.controlPoint:
    #         self.controlPoint.setVisible(True)

    # def hoverLeaveEvent(self, event):
    #     # Hide the control point when not hovering
    #     if self.controlPoint:
    #         self.controlPoint.setVisible(False)
