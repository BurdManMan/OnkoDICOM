from PySide6.QtWidgets import QSlider
from PySide6.QtCore import Qt, Signal

class Scroll_Wheel(QSlider):
    """Creates a scroll wheel for the dicom image loader"""
    slider_value = Signal(int)
    def __init__(self, dicom_image_set = None):
        super().__init__()
        self.dicom_image_set = dicom_image_set
        self.setMaximum(len(self.dicom_image_set))
        self.valueChanged.connect(self.value_changes)
        self.setValue(int(len(self.dicom_image_set)/2))

    def value_changes(self, value):
        """Updates when the spinbox changes"""
        #self.dicom_image_set.spin_box_value_changed(value)
        #self.slider_value.emit(value)
