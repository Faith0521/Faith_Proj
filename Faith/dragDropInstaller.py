import os,sys,shutil,re
from datetime import datetime

try:
    from maya.app.startup import basic
    from PySide2 import QtWidgets, QtCore, QtGui
    from shiboken2 import wrapInstance
    import maya.OpenMayaUI as omui
    import maya.cmds as cmds
    import maya.api.OpenMaya as om
    use_maya = True

except ImportError():
    use_maya = False

"""
Install Maya module with drag into
"""
TITLE = "Install Faith"
VERSION = 0.1
FAITH_MOD_PATH = "FAITH_MODULE_PATH"
MAYA_MOD_PATH = "MAYA_MODULE_PATH"
PLUGINS = ["FaithNodes.mll"]
ITEMS = ["platforms", "Faith.mod", "scripts", "icons"]
CURRENT_FOLDER = os.path.dirname(__file__)

def onMayaDroppedPythonFile(*args, **kwargs):
    pass

def maya_main_window():

    main_window_ptr = omui.MQtUtil.mainWindow()

    if sys.version_info.major <= 3:
        return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)
    else:
        return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)

class UI(QtWidgets.QDialog):
    """
    Crate Simple UI
    """
    def __init__(self, parent = maya_main_window()):
        super(UI, self).__init__(parent)

        self.setWindowTitle(TITLE)
        self.setFixedSize(550,300)
        self.setWindowFlags(QtCore.Qt.WindowType.Window)

        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def closeEvent(self, event):
        if isinstance(self, UI):
            super(UI, self).closeEvent(event)
        
        self.close()

    def showEvent(self, event):
        super(UI, self).showEvent(event)

        self.setPath_le(
            self.path_le, self.get_custom_mooudle_folder()
        )

    def create_widgets(self):
        self.create_title_lb()

        self.info_lb = QtWidgets.QLabel(
            "Please save your file before install module."
        )
        self.install_lb = QtWidgets.QLabel("Install Path:")
        self.install_lb_info = QtWidgets.QLabel(
            "The path you want to install."
        )
        self.install_lb_info.setDisabled(True)

        self.path_le = QtWidgets.QLineEdit()
        self.path_btn = QtWidgets.QPushButton("..Open..")

        self.install_btn = QtWidgets.QPushButton("Install")
        self.uninstall_btn = QtWidgets.QPushButton("Uninstall")

        self.logging_widget = QtWidgets.QPlainTextEdit()
        self.logging_widget.setReadOnly(True)
        self.logging_widget.setMaximumHeight(120)

    def create_layout(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(6, 6, 6, 6)

        install_group_layout = QtWidgets.QGroupBox("Paths:")
        progress_group_layout = QtWidgets.QGroupBox("Infos:")

        install_layout = QtWidgets.QGridLayout()
        install_layout.addWidget(self.install_lb, 1, 0)
        install_layout.addWidget(self.path_le, 1, 1)
        install_layout.addWidget(self.path_btn, 1, 2)
        install_layout.addWidget(self.install_lb_info, 2, 1)

        install_group_layout.setLayout(install_layout)

        progress_layout = QtWidgets.QVBoxLayout()
        progress_layout.addWidget(self.logging_widget)
        progress_layout.setContentsMargins(6, 6, 6, 6)

        progress_group_layout.setLayout(progress_layout)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.install_btn)
        button_layout.addWidget(self.uninstall_btn)
        button_layout.setSpacing(4)
        
        main_layout.addWidget(self.title_label)
        main_layout.addWidget(install_group_layout)
        main_layout.addWidget(progress_group_layout)
        main_layout.addLayout(button_layout)

        main_layout.setSpacing(3)

    def create_connections(self):
        self.install_btn.clicked.connect(self._install_btn_clicked)
        self.path_btn.clicked.connect(self._path_btn_clicked)
        self.uninstall_btn.clicked.connect(self._uninstall_btn_clicked)

    def create_title_lb(self):
        image_path = os.path.normpath(os.path.join(CURRENT_FOLDER,
                                                   "source",
                                                   "icons",
                                                   "Faith_logo.png"))

        image = QtGui.QImage(image_path)
        pixmap = QtGui.QPixmap()
        pixmap.convertFromImage(image)
        self.title_label = QtWidgets.QLabel("")
        self.title_label.setPixmap(pixmap)

    def _install_btn_clicked(self):
        """

        :return:
        """
        faith_folder = os.path.normpath(
            os.path.join(CURRENT_FOLDER, "source"))

        cmds.flushUndo()

        cmds.file(new = True, force = True)

        install_path = self.getPath_le(self.path_le)

        faith_install_path = os.path.join(install_path, "Faith")

        self.update_logging_widget("{0}".format(faith_install_path))

        # -- in case there is a left over folder
        if os.path.exists(faith_install_path):
            self.remove_directory(mgear_install_path)

        # -- look in install directory for files of same name
        # -- construct path names
        full_path = [os.path.join(install_path, x) for x in DEFAULT_ITEMS]
        print(full_path)
        # # -- files of the same name
        # found = self.files_exist(full_path)
        # if found:
        #     message = "mGear files already exist in the install location.\n"
        #     message += "Would you like to overwrite them?"
        #     message_box = QtWidgets.QMessageBox.warning(
        #         self,
        #         "Delete Existing Files",
        #         message,
        #         QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Close)
        #
        #     # -- don't save was clicked
        #     if message_box == QtWidgets.QMessageBox.Close:
        #         self.update_logging_widget("Installation Cancelled.")
        #         return
        #
        # # -- iterate over folders and remove them
        # self.start_uninstall(install_path)
        # # -- let's copy the folder over
        # shutil.copytree(mgear_folder, mgear_install_path)

    def _path_btn_clicked(self):
        file_path = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            "Select a dictionary",
            os.path.normpath(os.environ["MAYA_APP_DIR"])
        )
        if file_path:
            self.path_le.setText(file_path)

    def _uninstall_btn_clicked(self):
        pass
    
    def setPath_le(self, le, text):
        le.setText(text)

    def getPath_le(self, le):
        return le.text()

    def get_custom_mooudle_folder(self):
        return os.path.normpath(os.path.join(os.environ["MAYA_APP_DIR"],
        "modules"))

    def update_logging_widget(self, message = ""):
        """

        :param message:
        :return:
        """
        if not len(message):
            message = " "
        lines = message if isinstance(message, list) else [message]
        for i in range(len(lines)):
            lines[i] = "{} : {}".format(self.current_time(), lines[i])
        message = "\n".join(lines)

        self.logging_widget.appendPlainText(message)
        QtCore.QCoreApplication.processEvents()

    def current_time(self):
        """Return the current time as a nice formatted string.
        :return: The current date and time.
        :rtype: str
        """
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def remove_directory(self, path):
        """

        :param path:
        :return:
        """
        if os.path.exists(path):
            shutil.rmtree(path)
            self.update_logging_widget("Remove dictionary : {0}".format(path))
        else:
            return False
        return True

def drag_install():
    win = UI()
    win.show()

if use_maya:
    drag_install()

