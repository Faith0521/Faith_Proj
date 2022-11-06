# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'f:\Code\Faith_Proj\Faith\Tools\BS_Manager\UI\item_widget.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_tab_main(object):
    def setupUi(self, tab_main):
        tab_main.setObjectName("tab_main")
        tab_main.resize(363, 353)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(tab_main)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.mirror_widget = QtWidgets.QWidget(tab_main)
        self.mirror_widget.setObjectName("mirror_widget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.mirror_widget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.axis_hb = QtWidgets.QHBoxLayout()
        self.axis_hb.setObjectName("axis_hb")
        self.axis_lb = MLabel(self.mirror_widget)
        font = QtGui.QFont()
        font.setFamily("Consolas")
        self.axis_lb.setFont(font)
        self.axis_lb.setObjectName("axis_lb")
        self.axis_hb.addWidget(self.axis_lb)
        self.x_rb = MRadioButton(self.mirror_widget)
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        self.x_rb.setFont(font)
        self.x_rb.setObjectName("x_rb")
        self.axis_hb.addWidget(self.x_rb)
        self.y_rb = MRadioButton(self.mirror_widget)
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        self.y_rb.setFont(font)
        self.y_rb.setChecked(True)
        self.y_rb.setObjectName("y_rb")
        self.axis_hb.addWidget(self.y_rb)
        self.z_rb = MRadioButton(self.mirror_widget)
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        self.z_rb.setFont(font)
        self.z_rb.setObjectName("z_rb")
        self.axis_hb.addWidget(self.z_rb)
        self.verticalLayout_2.addLayout(self.axis_hb)
        self.name_hb = QtWidgets.QHBoxLayout()
        self.name_hb.setObjectName("name_hb")
        self.name_lb = MLabel(self.mirror_widget)
        font = QtGui.QFont()
        font.setFamily("Consolas")
        self.name_lb.setFont(font)
        self.name_lb.setObjectName("name_lb")
        self.name_hb.addWidget(self.name_lb)
        self.name_le = MLineEdit(self.mirror_widget)
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        self.name_le.setFont(font)
        self.name_le.setObjectName("name_le")
        self.name_hb.addWidget(self.name_le)
        self.verticalLayout_2.addLayout(self.name_hb)
        self.mirror_tgt_btn = MPushButton(self.mirror_widget)
        font = QtGui.QFont()
        font.setFamily("Consolas")
        font.setBold(True)
        font.setWeight(75)
        self.mirror_tgt_btn.setFont(font)
        self.mirror_tgt_btn.setObjectName("mirror_tgt_btn")
        self.verticalLayout_2.addWidget(self.mirror_tgt_btn)
        self.verticalLayout_3.addWidget(self.mirror_widget)
        self.drive_widget = QtWidgets.QWidget(tab_main)
        self.drive_widget.setObjectName("drive_widget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.drive_widget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.driver_hb = QtWidgets.QHBoxLayout()
        self.driver_hb.setObjectName("driver_hb")
        self.driver_lb = MLabel(self.drive_widget)
        font = QtGui.QFont()
        font.setFamily("Consolas")
        self.driver_lb.setFont(font)
        self.driver_lb.setObjectName("driver_lb")
        self.driver_hb.addWidget(self.driver_lb)
        self.driver_le = MLineEdit(self.drive_widget)
        font = QtGui.QFont()
        font.setFamily("Consolas")
        self.driver_le.setFont(font)
        self.driver_le.setObjectName("driver_le")
        self.driver_hb.addWidget(self.driver_le)
        self.driver_btn = QtWidgets.QPushButton(self.drive_widget)
        self.driver_btn.setMinimumSize(QtCore.QSize(20, 20))
        self.driver_btn.setMaximumSize(QtCore.QSize(20, 20))
        self.driver_btn.setStyleSheet("QPushButton{\n"
"border-image: url(:/icon/SHAPES_select_150.png);\n"
"}\n"
"QPushButton:hover{\n"
"border-image: url(:/icon/SHAPES_select_150_light.png);\n"
"}\n"
"QPushButton:pressed{\n"
"border-image: url(:/icon/SHAPES_select_150_light.png);\n"
"}")
        self.driver_btn.setText("")
        self.driver_btn.setObjectName("driver_btn")
        self.driver_hb.addWidget(self.driver_btn)
        self.verticalLayout.addLayout(self.driver_hb)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.attr_lb = MLabel(self.drive_widget)
        font = QtGui.QFont()
        font.setFamily("Consolas")
        self.attr_lb.setFont(font)
        self.attr_lb.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.attr_lb.setObjectName("attr_lb")
        self.horizontalLayout.addWidget(self.attr_lb)
        self.attr_combo = MComboBox(self.drive_widget)
        font = QtGui.QFont()
        font.setFamily("Consolas")
        self.attr_combo.setFont(font)
        self.attr_combo.setObjectName("attr_combo")
        self.attr_combo.addItem("")
        self.horizontalLayout.addWidget(self.attr_combo)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.time_hb = QtWidgets.QHBoxLayout()
        self.time_hb.setObjectName("time_hb")
        self.time_lb = MLabel(self.drive_widget)
        self.time_lb.setMinimumSize(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setFamily("Consolas")
        self.time_lb.setFont(font)
        self.time_lb.setObjectName("time_lb")
        self.time_hb.addWidget(self.time_lb)
        self.start_spin = QtWidgets.QDoubleSpinBox(self.drive_widget)
        font = QtGui.QFont()
        font.setFamily("Consolas")
        self.start_spin.setFont(font)
        self.start_spin.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.start_spin.setMaximum(9999999.0)
        self.start_spin.setSingleStep(0.001)
        self.start_spin.setObjectName("start_spin")
        self.time_hb.addWidget(self.start_spin)
        self.end_spin = QtWidgets.QDoubleSpinBox(self.drive_widget)
        font = QtGui.QFont()
        font.setFamily("Consolas")
        self.end_spin.setFont(font)
        self.end_spin.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.end_spin.setMaximum(9999999.0)
        self.end_spin.setSingleStep(0.001)
        self.end_spin.setObjectName("end_spin")
        self.time_hb.addWidget(self.end_spin)
        self.verticalLayout.addLayout(self.time_hb)
        self.type_hb = QtWidgets.QHBoxLayout()
        self.type_hb.setObjectName("type_hb")
        self.type_lb = MLabel(self.drive_widget)
        font = QtGui.QFont()
        font.setFamily("Consolas")
        self.type_lb.setFont(font)
        self.type_lb.setObjectName("type_lb")
        self.type_hb.addWidget(self.type_lb)
        self.type_combo = MComboBox(self.drive_widget)
        font = QtGui.QFont()
        font.setFamily("Consolas")
        self.type_combo.setFont(font)
        self.type_combo.setObjectName("type_combo")
        self.type_combo.addItem("")
        self.type_combo.addItem("")
        self.type_combo.addItem("")
        self.type_combo.addItem("")
        self.type_hb.addWidget(self.type_combo)
        self.infi_lb = MLabel(self.drive_widget)
        font = QtGui.QFont()
        font.setFamily("Consolas")
        self.infi_lb.setFont(font)
        self.infi_lb.setObjectName("infi_lb")
        self.type_hb.addWidget(self.infi_lb)
        self.infi_combo = MComboBox(self.drive_widget)
        font = QtGui.QFont()
        font.setFamily("Consolas")
        self.infi_combo.setFont(font)
        self.infi_combo.setObjectName("infi_combo")
        self.infi_combo.addItem("")
        self.infi_combo.addItem("")
        self.infi_combo.addItem("")
        self.infi_combo.addItem("")
        self.type_hb.addWidget(self.infi_combo)
        self.verticalLayout.addLayout(self.type_hb)
        self.create_hb = QtWidgets.QHBoxLayout()
        self.create_hb.setObjectName("create_hb")
        self.apply_btn = MPushButton(self.drive_widget)
        font = QtGui.QFont()
        font.setFamily("Consolas")
        font.setBold(True)
        font.setWeight(75)
        self.apply_btn.setFont(font)
        self.apply_btn.setObjectName("apply_btn")
        self.create_hb.addWidget(self.apply_btn)
        self.mirror_btn = MPushButton(self.drive_widget)
        font = QtGui.QFont()
        font.setFamily("Consolas")
        font.setBold(True)
        font.setWeight(75)
        self.mirror_btn.setFont(font)
        self.mirror_btn.setObjectName("mirror_btn")
        self.create_hb.addWidget(self.mirror_btn)
        self.verticalLayout.addLayout(self.create_hb)
        self.verticalLayout_3.addWidget(self.drive_widget)
        self.side_setting_widget = QtWidgets.QWidget(tab_main)
        self.side_setting_widget.setObjectName("side_setting_widget")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.side_setting_widget)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label = MLabel(self.side_setting_widget)
        self.label.setObjectName("label")
        self.horizontalLayout_2.addWidget(self.label)
        self.lineEdit = MLineEdit(self.side_setting_widget)
        self.lineEdit.setObjectName("lineEdit")
        self.horizontalLayout_2.addWidget(self.lineEdit)
        self.verticalLayout_4.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_2 = MLabel(self.side_setting_widget)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_3.addWidget(self.label_2)
        self.lineEdit_2 = MLineEdit(self.side_setting_widget)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.horizontalLayout_3.addWidget(self.lineEdit_2)
        self.verticalLayout_4.addLayout(self.horizontalLayout_3)
        self.verticalLayout_3.addWidget(self.side_setting_widget)

        self.retranslateUi(tab_main)
        QtCore.QMetaObject.connectSlotsByName(tab_main)

    def retranslateUi(self, tab_main):
        _translate = QtCore.QCoreApplication.translate
        tab_main.setWindowTitle(_translate("tab_main", "Form"))
        self.axis_lb.setText(_translate("tab_main", "方向"))
        self.x_rb.setText(_translate("tab_main", "X"))
        self.y_rb.setText(_translate("tab_main", "Y"))
        self.z_rb.setText(_translate("tab_main", "Z"))
        self.name_lb.setText(_translate("tab_main", "通道命名"))
        self.name_le.setPlaceholderText(_translate("tab_main", "镜像的通道名称"))
        self.mirror_tgt_btn.setText(_translate("tab_main", "镜像目标体"))
        self.driver_lb.setText(_translate("tab_main", "驱动物体"))
        self.driver_le.setPlaceholderText(_translate("tab_main", "选择一个驱动属性"))
        self.driver_btn.setToolTip(_translate("tab_main", "选择"))
        self.attr_lb.setText(_translate("tab_main", "属性"))
        self.attr_combo.setItemText(0, _translate("tab_main", "None"))
        self.time_lb.setText(_translate("tab_main", "开始/结束"))
        self.type_lb.setText(_translate("tab_main", "Type"))
        self.type_combo.setItemText(0, _translate("tab_main", "Linear"))
        self.type_combo.setItemText(1, _translate("tab_main", "Slow"))
        self.type_combo.setItemText(2, _translate("tab_main", "Fast"))
        self.type_combo.setItemText(3, _translate("tab_main", "Smooth"))
        self.infi_lb.setText(_translate("tab_main", "Infinity"))
        self.infi_combo.setItemText(0, _translate("tab_main", "None"))
        self.infi_combo.setItemText(1, _translate("tab_main", "Post"))
        self.infi_combo.setItemText(2, _translate("tab_main", "Pre"))
        self.infi_combo.setItemText(3, _translate("tab_main", "Pre/Post"))
        self.apply_btn.setText(_translate("tab_main", "创建"))
        self.mirror_btn.setText(_translate("tab_main", "镜像"))
        self.label.setText(_translate("tab_main", "左侧"))
        self.lineEdit.setText(_translate("tab_main", "left_, _left, Left_, _Left, lt_, _lt, Lt_, _Lt, lft_, _lft, Lft_, _Lft, Lf_, _Lf, lf_, _lf, l_, _l, L_, _L"))
        self.label_2.setText(_translate("tab_main", "右侧"))
        self.lineEdit_2.setText(_translate("tab_main", "right_, _right, Right_, _Right, rt_, _rt, Rt_, _Rt, rgt_, _rgt, Rgt_, _Rgt, Rg_, _Rg, rg_, _rg, r_, _r, R_, _R"))
from dayu_widgets.combo_box import MComboBox
from dayu_widgets.label import MLabel
from dayu_widgets.line_edit import MLineEdit
from dayu_widgets.push_button import MPushButton
from dayu_widgets.radio_button import MRadioButton
import icon_rc
