# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'BS_List.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PySide2 import QtCore, QtGui, QtWidgets


class Ui_BS_ListMain(object):
    def setupUi(self, BS_ListMain):
        BS_ListMain.setObjectName("BS_ListMain")
        BS_ListMain.resize(317, 624)
        self.verticalLayout = QtWidgets.QVBoxLayout(BS_ListMain)
        self.verticalLayout.setContentsMargins(6, 6, 6, 6)
        self.verticalLayout.setObjectName("verticalLayout")
        self.list_widget = QtWidgets.QWidget(BS_ListMain)
        self.list_widget.setObjectName("list_widget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.list_widget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.load_hb = QtWidgets.QHBoxLayout()
        self.load_hb.setObjectName("load_hb")
        self.load_btn = MPushButton().small()
        font = QtGui.QFont()
        font.setFamily("Consolas")
        self.load_btn.setFont(font)
        self.load_btn.setObjectName("load_btn")
        self.load_hb.addWidget(self.load_btn)
        self.load_le = MLineEdit()
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        self.load_le.setFont(font)
        self.load_le.setObjectName("load_le")
        self.load_hb.addWidget(self.load_le)
        self.verticalLayout_2.addLayout(self.load_hb)
        self.bs_hb = QtWidgets.QHBoxLayout()
        self.bs_hb.setObjectName("bs_hb")
        self.bs_lb = MLabel()
        self.bs_lb.setMinimumSize(QtCore.QSize(0, 0))
        self.bs_lb.setMaximumSize(QtCore.QSize(16777215, 16777215))
        font = QtGui.QFont()
        font.setFamily("Consolas")
        self.bs_lb.setFont(font)
        self.bs_lb.setObjectName("bs_lb")
        self.bs_hb.addWidget(self.bs_lb)
        self.bs_cb = MComboBox()
        font = QtGui.QFont()
        font.setFamily("Consolas")
        self.bs_cb.setFont(font)
        self.bs_cb.setObjectName("bs_cb")
        self.bs_cb.addItem("")
        self.bs_hb.addWidget(self.bs_cb)
        self.verticalLayout_2.addLayout(self.bs_hb)
        self.target_lb = MLabel()
        font = QtGui.QFont()
        font.setFamily("Consolas")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.target_lb.setFont(font)
        self.target_lb.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.target_lb.setAlignment(QtCore.Qt.AlignCenter)
        self.target_lb.setObjectName("target_lb")
        self.verticalLayout_2.addWidget(self.target_lb)
        self.search_le = MLineEdit()
        self.search_le.setMaximumSize(QtCore.QSize(16777215, 20))
        self.search_le.setObjectName("search_le")
        self.verticalLayout_2.addWidget(self.search_le)
        self.target_list = QtWidgets.QListWidget(self.list_widget)
        self.target_list.setMinimumSize(QtCore.QSize(0, 300))
        self.target_list.setObjectName("target_list")
        self.verticalLayout_2.addWidget(self.target_list)
        self.edit_hb = QtWidgets.QHBoxLayout()
        self.edit_hb.setSpacing(2)
        self.edit_hb.setObjectName("edit_hb")
        self.add_btn = MPushButton().small()
        self.add_btn.setObjectName("add_btn")
        self.edit_hb.addWidget(self.add_btn)
        self.edit_btn = MPushButton().small()
        self.edit_btn.setMaximumSize(QtCore.QSize(16777215, 16777215))
        font = QtGui.QFont()
        font.setFamily("Consolas")
        self.edit_btn.setFont(font)
        self.edit_btn.setToolTip("")
        self.edit_btn.setStyleSheet("")
        self.edit_btn.setObjectName("edit_btn")
        self.edit_hb.addWidget(self.edit_btn)
        spacerItem = QtWidgets.QSpacerItem(60, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.edit_hb.addItem(spacerItem)
        self.ccs_btn = QtWidgets.QPushButton(self.list_widget)
        self.ccs_btn.setMinimumSize(QtCore.QSize(20, 20))
        self.ccs_btn.setMaximumSize(QtCore.QSize(10, 20))
        self.ccs_btn.setStyleSheet("QPushButton{\n"
"border-image: url(:/icon/SHAPES_comboMembers_200.png);\n"
"}\n"
"QPushButton:hover{\n"
"border-image: url(:/icon/SHAPES_comboMembers_200_light.png);\n"
"}\n"
"QPushButton:pressed{\n"
"border-image: url(:/icon/SHAPES_comboMembers_200_light.png);\n"
"}")
        self.ccs_btn.setText("")
        self.ccs_btn.setObjectName("ccs_btn")
        self.edit_hb.addWidget(self.ccs_btn)
        self.dup_btn = QtWidgets.QPushButton(self.list_widget)
        self.dup_btn.setMinimumSize(QtCore.QSize(20, 20))
        self.dup_btn.setMaximumSize(QtCore.QSize(20, 20))
        self.dup_btn.setStyleSheet("QPushButton{\n"
"border-image: url(:/icon/SHAPES_weightPaste_200.png);\n"
"}\n"
"QPushButton:hover{\n"
"border-image: url(:/icon/SHAPES_weightPaste_200_light.png);\n"
"}\n"
"QPushButton:pressed{\n"
"border-image: url(:/icon/SHAPES_weightPaste_200_light.png);\n"
"}")
        self.dup_btn.setText("")
        self.dup_btn.setObjectName("dup_btn")
        self.edit_hb.addWidget(self.dup_btn)
        self.extr_btn = QtWidgets.QPushButton(self.list_widget)
        self.extr_btn.setMinimumSize(QtCore.QSize(20, 20))
        self.extr_btn.setMaximumSize(QtCore.QSize(20, 20))
        self.extr_btn.setStyleSheet("QPushButton{\n"
"border-image: url(:/icon/SHAPES_weightExport_200.png);\n"
"}\n"
"QPushButton:hover{\n"
"border-image: url(:/icon/SHAPES_weightExport_200_light.png);\n"
"}\n"
"QPushButton:pressed{\n"
"border-image: url(:/icon/SHAPES_weightExport_200_light.png);\n"
"}")
        self.extr_btn.setText("")
        self.extr_btn.setObjectName("extr_btn")
        self.edit_hb.addWidget(self.extr_btn)
        self.verticalLayout_2.addLayout(self.edit_hb)
        self.verticalLayout.addWidget(self.list_widget)

        self.retranslateUi(BS_ListMain)
        QtCore.QMetaObject.connectSlotsByName(BS_ListMain)

    def retranslateUi(self, BS_ListMain):
        _translate = QtCore.QCoreApplication.translate
        BS_ListMain.setWindowTitle(_translate("BS_ListMain", "Form"))
        self.load_btn.setToolTip(u"加载模型")
        self.load_btn.setText(u"加载")
        self.load_le.setPlaceholderText(u"加载所选模型")
        self.bs_lb.setText(u"BS名称")
        self.bs_cb.setItemText(0, _translate("BS_ListMain", "None"))
        self.target_lb.setText(u"BlendShape目标体列表")
        self.add_btn.setText(u"创建")
        self.edit_btn.setText(u"编辑")
        self.ccs_btn.setToolTip(u"创建CCS")
        self.dup_btn.setToolTip(u"复制模型")
        self.extr_btn.setToolTip(u"提取目标体")
from dayu_widgets.combo_box import MComboBox
from dayu_widgets.label import MLabel
from dayu_widgets.line_edit import MLineEdit
from dayu_widgets.push_button import MPushButton
from dayu_widgets.static import icon_rc
