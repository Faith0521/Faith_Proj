# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\UI.ui'
#
# Created: Wed Aug  3 17:41:11 2022
#      by: pyside2-uic  running on PySide2 2.0.0~alpha0
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(325, 488)
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setContentsMargins(3, 3, 3, 3)
        self.verticalLayout.setObjectName("verticalLayout")
        self.Content = QtWidgets.QFrame(Form)
        self.Content.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.Content.setFrameShadow(QtWidgets.QFrame.Raised)
        self.Content.setObjectName("Content")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.Content)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.Main_frame = QtWidgets.QFrame(self.Content)
        self.Main_frame.setStyleSheet("")
        self.Main_frame.setObjectName("Main_frame")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.Main_frame)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.node_hb = QtWidgets.QHBoxLayout()
        self.node_hb.setContentsMargins(0, 0, 0, -1)
        self.node_hb.setObjectName("node_hb")
        self.pushButton = QtWidgets.QPushButton()
        self.pushButton.setEnabled(False)
        self.pushButton.setMinimumSize(QtCore.QSize(0, 30))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        self.pushButton.setFont(font)
        self.pushButton.setObjectName("pushButton")
        self.node_hb.addWidget(self.pushButton)
        self.node_le = QtWidgets.QLineEdit(self.Main_frame)
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        self.node_le.setFont(font)
        self.node_le.setStyleSheet("")
        self.node_le.setReadOnly(True)
        self.node_le.setObjectName("node_le")
        self.node_hb.addWidget(self.node_le)
        self.load_btn = MPushButton()
        self.load_btn.setMinimumSize(QtCore.QSize(0, 20))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        self.load_btn.setFont(font)
        self.load_btn.setStyleSheet("")
        self.load_btn.setObjectName("load_btn")
        self.node_hb.addWidget(self.load_btn)
        self.verticalLayout_3.addLayout(self.node_hb)
        self.direc_hb = QtWidgets.QHBoxLayout()
        self.direc_hb.setObjectName("direc_hb")
        self.pushButton_2 = QtWidgets.QPushButton()
        self.pushButton_2.setEnabled(False)
        self.pushButton_2.setMinimumSize(QtCore.QSize(0, 30))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        self.pushButton_2.setFont(font)
        self.pushButton_2.setObjectName("pushButton_2")
        self.direc_hb.addWidget(self.pushButton_2)
        self.frnt_rbtn = MRadioButton()
        self.frnt_rbtn.setMinimumSize(QtCore.QSize(0, 30))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        self.frnt_rbtn.setFont(font)
        self.frnt_rbtn.setStyleSheet("")
        self.frnt_rbtn.setChecked(True)
        self.frnt_rbtn.setObjectName("frnt_rbtn")
        self.direc_hb.addWidget(self.frnt_rbtn)
        self.after_rbtn = MRadioButton()
        self.after_rbtn.setMinimumSize(QtCore.QSize(0, 30))
        font = QtGui.QFont()
        font.setFamily("Nirmala UI")
        self.after_rbtn.setFont(font)
        self.after_rbtn.setStyleSheet("")
        self.after_rbtn.setObjectName("after_rbtn")
        self.direc_hb.addWidget(self.after_rbtn)
        self.verticalLayout_3.addLayout(self.direc_hb)
        self.list_mainvb = QtWidgets.QVBoxLayout()
        self.list_mainvb.setObjectName("list_mainvb")
        self.listVb = QtWidgets.QVBoxLayout()
        self.listVb.setObjectName("listVb")
        self.driver_vb = QtWidgets.QVBoxLayout()
        self.driver_vb.setObjectName("driver_vb")
        self.driver_lb = QtWidgets.QLabel(self.Main_frame)
        self.driver_lb.setMinimumSize(QtCore.QSize(0, 20))
        font = QtGui.QFont()
        font.setFamily("Fixedsys")
        self.driver_lb.setFont(font)
        self.driver_lb.setStyleSheet("")
        self.driver_lb.setObjectName("driver_lb")
        self.driver_vb.addWidget(self.driver_lb)
        self.driver_list = DragQListView(self.Main_frame)
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        self.driver_list.setFont(font)
        self.driver_list.setObjectName("driver_list")
        self.driver_vb.addWidget(self.driver_list)
        self.listVb.addLayout(self.driver_vb)
        self.driven_lb = QtWidgets.QLabel(self.Main_frame)
        self.driven_lb.setMinimumSize(QtCore.QSize(0, 20))
        font = QtGui.QFont()
        font.setFamily("Fixedsys")
        self.driven_lb.setFont(font)
        self.driven_lb.setStyleSheet("")
        self.driven_lb.setObjectName("driven_lb")
        self.listVb.addWidget(self.driven_lb)
        self.driven_list = DragQListView(self.Main_frame)
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        self.driven_list.setFont(font)
        self.driven_list.setObjectName("driven_list")
        self.listVb.addWidget(self.driven_list)
        self.bottomBtn_hb = QtWidgets.QHBoxLayout()
        self.bottomBtn_hb.setObjectName("bottomBtn_hb")
        self.refresh_btn = MPushButton()
        self.refresh_btn.setMinimumSize(QtCore.QSize(0, 30))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        self.refresh_btn.setFont(font)
        self.refresh_btn.setStyleSheet("")
        self.refresh_btn.setObjectName("refresh_btn")
        self.bottomBtn_hb.addWidget(self.refresh_btn)
        self.mirror_btn = MPushButton()
        self.mirror_btn.setMinimumSize(QtCore.QSize(0, 30))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        self.mirror_btn.setFont(font)
        self.mirror_btn.setStyleSheet("")
        self.mirror_btn.setObjectName("mirror_btn")
        self.bottomBtn_hb.addWidget(self.mirror_btn)
        self.listVb.addLayout(self.bottomBtn_hb)
        self.list_mainvb.addLayout(self.listVb)
        self.verticalLayout_3.addLayout(self.list_mainvb)
        self.horizontalLayout_2.addWidget(self.Main_frame)
        self.verticalLayout.addWidget(self.Content)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtWidgets.QApplication.translate("Form", "SDK_TOOL v0.0.1", None, -1))
        self.pushButton.setText(QtWidgets.QApplication.translate("Form", "Node", None, -1))
        self.node_le.setPlaceholderText(QtWidgets.QApplication.translate("Form", "Please select one node.", None, -1))
        self.load_btn.setText(QtWidgets.QApplication.translate("Form", "L o a d", None, -1))
        self.pushButton_2.setText(QtWidgets.QApplication.translate("Form", "Direction", None, -1))
        self.frnt_rbtn.setText(QtWidgets.QApplication.translate("Form", "F r o n t", None, -1))
        self.after_rbtn.setText(QtWidgets.QApplication.translate("Form", "A f t e r", None, -1))
        self.driver_lb.setText(QtWidgets.QApplication.translate("Form", "Driver:", None, -1))
        self.driven_lb.setText(QtWidgets.QApplication.translate("Form", "Driven:", None, -1))
        self.refresh_btn.setText(QtWidgets.QApplication.translate("Form", "Refresh", None, -1))
        self.mirror_btn.setText(QtWidgets.QApplication.translate("Form", "Mirror", None, -1))

from dayu_widgets.push_button import MPushButton
from Faith.Core.aboutUI import DragQListView
from dayu_widgets.radio_button import MRadioButton
