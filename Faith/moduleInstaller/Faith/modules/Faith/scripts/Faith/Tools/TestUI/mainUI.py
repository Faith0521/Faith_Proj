from PySide2 import QtWidgets,QtCore,QtGui
from maya import cmds


class CollapsibleHeader(QtWidgets.QWidget):

    def __init__(self, text="", parent=None):
        super(CollapsibleHeader, self).__init__(parent)

        self.text_lb = QtWidgets.QLabel()

        self.main_layout = QtWidgets.QHBoxLayout(self)
        self.main_layout.setContentsMargins(4, 4, 4, 4)
        self.main_layout.addWidget(self.text_lb)

        self.set_text(text)

    def set_text(self, text):
        self.text_lb.setText(text)


class CollapsibleWidget(QtWidgets.QWidget):

    def __init__(self, text="", parent=None):
        super(CollapsibleWidget, self).__init__(parent)

        self.header_wdg = CollapsibleHeader(text)

        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.header_wdg)


class TestDialog(QtWidgets.QWidget):

    WINDOW_TITLE = "Test Dialog"

    def __init__(self, parent=None):
        super(TestDialog, self).__init__(parent)

        self.setWindowTitle(self.WINDOW_TITLE)
        if cmds.about(ntOS=True):
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        elif cmds.about(macos=True):
            self.setWindowFlags(QtCore.Qt.Tool)

        self.setMinimumSize(250,200)

        self.create_widgets()
        self.create_layouts()

    def create_widgets(self):
        self.collasible_wdg_a = CollapsibleWidget("SectionA")
        self.collasible_wdg_b = CollapsibleWidget("SectionA")

    def create_layouts(self):
        self.body_wdg = QtWidgets.QWidget()

        self.body_layout = QtWidgets.QVBoxLayout(self.body_wdg)
        self.body_layout.setContentsMargins(4,2,4,2)
        self.body_layout.setSpacing(3)
        self.body_layout.setAlignment(QtCore.Qt.AlignTop)

        self.body_layout.addWidget(self.collasible_wdg_a)
        self.body_layout.addWidget(self.collasible_wdg_b)





























