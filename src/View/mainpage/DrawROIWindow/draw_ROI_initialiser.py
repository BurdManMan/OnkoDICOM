from PySide6 import QtWidgets, QtGui
from PySide6.QtGui import QPen, QKeyEvent
from PySide6.QtCore import Qt
from src.View.mainpage.DrawROIWindow.Toolbar import CutsomToolbar
from src.View.mainpage.DrawROIWindow.Left_P import LeftPannel
from src.View.mainpage.DrawROIWindow.Canvas import CanvasLabel
from src.View.mainpage.DrawROIWindow.Units_Box import UnitsBox
from src.View.mainpage.DicomAxialView import DicomAxialView
from src.View.StyleSheetReader import StyleSheetReader
from src.View.mainpage.DicomView import CustomGraphicsView
from src.Model.PatientDictContainer import PatientDictContainer
from src.View.mainpage.DrawROIWindow.scroll_loader_4_dicom_image import Scroll_Wheel

#Sourcery.ai Is this true
class RoiInitialiser(QtWidgets.QWidget):
    """Class to hold the draw ROI features"""
    def __init__(self, host_main_window: QtWidgets.QMainWindow, rois, dataset_rtss, parent=None):
        super().__init__(parent)
        self.host = host_main_window
        self.central = QtWidgets
        self.p = PatientDictContainer()
        self.display_pixmaps = []
        self.get_pixmaps()
        
        self.setWindowTitle("ROI Prototype")
        print("1")

        # Temporary hard coded directory path
        self.last_point = None

        # Initialize the pen
        self.pen = QPen()
        self.pen.setWidth(6)
        self.pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        self.pen.setColor("blue")

        # Initalises the calsses
        self.dicom_viewer = DicomAxialView()
        self.scroller = Scroll_Wheel(self.display_pixmaps)
        self.scroller.valueChanged.connect(self.change_image)
        

        # 1) Scene on the view
        self.scene = QtWidgets.QGraphicsScene(self)
        self.pleaseWork = CustomGraphicsView()
        self.pleaseWork.setScene(self.scene)        # <-- REQUIRED

        # 2) Base image item
        self.image = self.display_pixmaps[self.scroller.value()]

        self.image_item = QtWidgets.QGraphicsPixmapItem(self.image)
        self.image_item.setZValue(0)
        self.scene.addItem(self.image_item)

        # 3) Overlay item (your CanvasLabel subclass of QGraphicsPixmapItem)
        self.canvas_labal = CanvasLabel(self.pen,self.scroller)     # no QGraphicsView as parent
        self.scene.addItem(self.canvas_labal)
        self.scene.setSceneRect(self.image_item.boundingRect())

        # 4) Transparent pixmap for drawing
        overlay_pm = QtGui.QPixmap(self.image.size())
        overlay_pm.fill(Qt.transparent)
        self.canvas_labal.setPixmap(overlay_pm)

        # 5) Align & configure
        self.canvas_labal.setPos(self.image_item.pos())
        self.canvas_labal.setZValue(10)
        self.canvas_labal.setAcceptedMouseButtons(Qt.LeftButton)
        self.canvas_labal.setShapeMode(QtWidgets.QGraphicsPixmapItem.BoundingRectShape)
        self.canvas_labal.setAcceptedMouseButtons(Qt.LeftButton)
        # (optional) self.canvas_labal.setAcceptHoverEvents(True)

        # 6) View interaction settings (so the item gets the mouse)
        self.pleaseWork.setDragMode(QtWidgets.QGraphicsView.NoDrag)  # while drawing
        self.pleaseWork.setInteractive(True)
        self.pleaseWork.setRenderHints(
            QtGui.QPainter.Antialiasing | QtGui.QPainter.SmoothPixmapTransform
        )

         

        self.view = QtWidgets.QGraphicsView(self.scene)
        self.view.setDragMode(QtWidgets.QGraphicsView.NoDrag)
        self.view.setInteractive(True)
        self.view.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.SmoothPixmapTransform)
        self.view.setFrameShape(QtWidgets.QFrame.NoFrame) 
        

        self.units_box = UnitsBox(self, self.pen, self.canvas_labal)
        self.left_label = LeftPannel(self, self.pen, self.canvas_labal)

        # Creates a layout for the tools to fit inside
        tools_layout = QtWidgets.QVBoxLayout()
        tools_container = QtWidgets.QWidget()
        tools_container.setLayout(tools_layout)
        tools_layout.addWidget(self.left_label)
        tools_layout.addWidget(self.units_box)


        # Create a layout to hold the left panel and the main canvas
        # Create a QWidget to hold both the left panel and the central label
        # Add the left panel to the layout
        # Add the canvas label to the layout
        # Set the central widget to be our layout container
        main = QtWidgets.QHBoxLayout(self)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(8)
        main.addWidget(tools_container)
        main.addWidget(self.scroller)
        main.addWidget(self.view, 1)

        # keep a toolbar factory if you like (QMainWindow will add it)
        self._toolbar = CutsomToolbar(self, self.canvas_labal, self.left_label)
        self._toolbar.colour.connect(self.left_label.update_colour)

    def build_toolbar(self) -> QtWidgets.QToolBar:
        """Creates and adds the toolbar to the ui"""
        return self._toolbar

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Up:
            self.dicom_viewer.slider.setValue(self.dicom_viewer.slider.value() +1)
            self.canvas_labal.ds_is_active = False
        if event.key() == Qt.Key_Down:
            self.dicom_viewer.slider.setValue(self.dicom_viewer.slider.value() -1)
            self.canvas_labal.ds_is_active = False
        return super().keyPressEvent(event)


    def apply_zoom(self):
        factor = self.dicom_viewer.zoom
        idx = self.dicom_viewer.slider.value()
        base = self.canvas_labal.base_canvas[idx]     # keep an unscaled master!
        scaled = base.scaled(base.size() * factor,Qt.KeepAspectRatio,
                                            Qt.SmoothTransformation)
        self.canvas_labal.canvas[idx] = scaled
        self.canvas_labal.setPixmap(scaled)           # if CanvasLabel is a QLabel
        self.canvas_labal.update()

    def get_pixmaps(self):
        """Gets all of the pixmap data and returns it"""
        pixmaps = self.p.get("pixmaps_axial")
        i = len(pixmaps)
        j = 0
        for _ in range(i):
            self.display_pixmaps.append(pixmaps[j])
            j +=1
    def change_image(self, v):
        """Changes the image according to the value"""
        image = self.display_pixmaps[self.scroller.value()]
        self.image_item.setPixmap(image)