# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'driver.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PySide2 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(354, 584)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.node_hb = QtWidgets.QHBoxLayout()
        self.node_hb.setObjectName("node_hb")
        self.node_lb = MLabel()
        font = QtGui.QFont()
        font.setFamily("Consolas")
        self.node_lb.setFont(font)
        self.node_lb.setObjectName("node_lb")
        self.node_hb.addWidget(self.node_lb)
        self.node_combo = MComboBox()
        font = QtGui.QFont()
        font.setFamily("Consolas")
        self.node_combo.setFont(font)
        self.node_combo.setObjectName("node_combo")
        self.node_combo.addItem("")
        self.node_hb.addWidget(self.node_combo)
        self.nodeSelect_btn = QtWidgets.QPushButton(Form)
        self.nodeSelect_btn.setMinimumSize(QtCore.QSize(20, 20))
        self.nodeSelect_btn.setMaximumSize(QtCore.QSize(20, 20))
        self.nodeSelect_btn.setStyleSheet("QPushButton{\n"
"border-image: url(:/icon/SHAPES_select_150.png);\n"
"}\n"
"QPushButton:hover{\n"
"border-image: url(:/icon/SHAPES_select_150_light.png);\n"
"}\n"
"QPushButton:pressed{\n"
"border-image: url(:/icon/SHAPES_select_150_light.png);\n"
"}")
        self.nodeSelect_btn.setText("")
        self.nodeSelect_btn.setObjectName("nodeSelect_btn")
        self.node_hb.addWidget(self.nodeSelect_btn)
        self.nodeSave_btn = QtWidgets.QPushButton(Form)
        self.nodeSave_btn.setMinimumSize(QtCore.QSize(20, 20))
        self.nodeSave_btn.setMaximumSize(QtCore.QSize(20, 20))
        self.nodeSave_btn.setStyleSheet("QPushButton{\n"
"border-image: url(:/icon/save_fill.png);\n"
"}\n"
"QPushButton:hover{\n"
"border-image: url(:/icon/save_fill_light.png);\n"
"}\n"
"QPushButton:pressed{\n"
"border-image: url(:/icon/save_fill_light.png);\n"
"}")
        self.nodeSave_btn.setText("")
        self.nodeSave_btn.setObjectName("nodeSave_btn")
        self.node_hb.addWidget(self.nodeSave_btn)
        self.nodeOpen_btn = QtWidgets.QPushButton(Form)
        self.nodeOpen_btn.setMinimumSize(QtCore.QSize(20, 20))
        self.nodeOpen_btn.setMaximumSize(QtCore.QSize(20, 20))
        self.nodeOpen_btn.setStyleSheet("QPushButton{\n"
"border-image: url(:/icon/SHAPES_addGroup.png);\n"
"}\n"
"QPushButton:hover{\n"
"border-image: url(:/icon/SHAPES_addGroup_light.png);\n"
"}\n"
"QPushButton:pressed{\n"
"border-image: url(:/icon/SHAPES_addGroup_light.png);\n"
"}")
        self.nodeOpen_btn.setText("")
        self.nodeOpen_btn.setObjectName("nodeOpen_btn")
        self.node_hb.addWidget(self.nodeOpen_btn)
        self.verticalLayout_2.addLayout(self.node_hb)
        self.driver_vb = QtWidgets.QVBoxLayout()
        self.driver_vb.setObjectName("driver_vb")
        self.driverObj_hb = QtWidgets.QHBoxLayout()
        self.driverObj_hb.setObjectName("driverObj_hb")
        self.driver_lb = MLabel()
        font = QtGui.QFont()
        font.setFamily("Consolas")
        self.driver_lb.setFont(font)
        self.driver_lb.setObjectName("driver_lb")
        self.driverObj_hb.addWidget(self.driver_lb)
        self.driver_le = MLineEdit()
        font = QtGui.QFont()
        font.setFamily("Consolas")
        self.driver_le.setFont(font)
        self.driver_le.setObjectName("driver_le")
        self.driverObj_hb.addWidget(self.driver_le)
        self.driverSelect_btn = QtWidgets.QPushButton(Form)
        self.driverSelect_btn.setMinimumSize(QtCore.QSize(20, 20))
        self.driverSelect_btn.setMaximumSize(QtCore.QSize(20, 20))
        self.driverSelect_btn.setStyleSheet("QPushButton{\n"
"border-image: url(:/icon/SHAPES_select_150.png);\n"
"}\n"
"QPushButton:hover{\n"
"border-image: url(:/icon/SHAPES_select_150_light.png);\n"
"}\n"
"QPushButton:pressed{\n"
"border-image: url(:/icon/SHAPES_select_150_light.png);\n"
"}")
        self.driverSelect_btn.setText("")
        self.driverSelect_btn.setObjectName("driverSelect_btn")
        self.driverObj_hb.addWidget(self.driverSelect_btn)
        self.driver_vb.addLayout(self.driverObj_hb)
        self.parent_hb = QtWidgets.QHBoxLayout()
        self.parent_hb.setObjectName("parent_hb")
        self.parent_lb = MLabel()
        font = QtGui.QFont()
        font.setFamily("Consolas")
        self.parent_lb.setFont(font)
        self.parent_lb.setObjectName("parent_lb")
        self.parent_hb.addWidget(self.parent_lb)
        self.parent_le = MLineEdit()
        font = QtGui.QFont()
        font.setFamily("Consolas")
        self.parent_le.setFont(font)
        self.parent_le.setObjectName("parent_le")
        self.parent_hb.addWidget(self.parent_le)
        self.parentSelect_btn = QtWidgets.QPushButton(Form)
        self.parentSelect_btn.setMinimumSize(QtCore.QSize(20, 20))
        self.parentSelect_btn.setMaximumSize(QtCore.QSize(20, 20))
        self.parentSelect_btn.setStyleSheet("QPushButton{\n"
"border-image: url(:/icon/SHAPES_select_150.png);\n"
"}\n"
"QPushButton:hover{\n"
"border-image: url(:/icon/SHAPES_select_150_light.png);\n"
"}\n"
"QPushButton:pressed{\n"
"border-image: url(:/icon/SHAPES_select_150_light.png);\n"
"}")
        self.parentSelect_btn.setText("")
        self.parentSelect_btn.setObjectName("parentSelect_btn")
        self.parent_hb.addWidget(self.parentSelect_btn)
        self.driver_vb.addLayout(self.parent_hb)
        self.control_hb = QtWidgets.QHBoxLayout()
        self.control_hb.setObjectName("control_hb")
        self.contrl_lb = MLabel()
        font = QtGui.QFont()
        font.setFamily("Consolas")
        self.contrl_lb.setFont(font)
        self.contrl_lb.setObjectName("contrl_lb")
        self.control_hb.addWidget(self.contrl_lb)
        self.control_le = MLineEdit()
        font = QtGui.QFont()
        font.setFamily("Consolas")
        self.control_le.setFont(font)
        self.control_le.setObjectName("control_le")
        self.control_hb.addWidget(self.control_le)
        self.controlSelect_btn = QtWidgets.QPushButton(Form)
        self.controlSelect_btn.setMinimumSize(QtCore.QSize(20, 20))
        self.controlSelect_btn.setMaximumSize(QtCore.QSize(20, 20))
        self.controlSelect_btn.setStyleSheet("QPushButton{\n"
"border-image: url(:/icon/SHAPES_select_150.png);\n"
"}\n"
"QPushButton:hover{\n"
"border-image: url(:/icon/SHAPES_select_150_light.png);\n"
"}\n"
"QPushButton:pressed{\n"
"border-image: url(:/icon/SHAPES_select_150_light.png);\n"
"}")
        self.controlSelect_btn.setText("")
        self.controlSelect_btn.setObjectName("controlSelect_btn")
        self.control_hb.addWidget(self.controlSelect_btn)
        self.driver_vb.addLayout(self.control_hb)
        self.verticalLayout_2.addLayout(self.driver_vb)
        self.allow_hb = QtWidgets.QHBoxLayout()
        self.allow_hb.setObjectName("allow_hb")
        self.allow_cb = MCheckBox()
        font = QtGui.QFont()
        font.setFamily("Consolas")
        self.allow_cb.setFont(font)
        self.allow_cb.setChecked(True)
        self.allow_cb.setObjectName("allow_cb")
        self.allow_hb.addWidget(self.allow_cb)
        self.checkBox = MCheckBox()
        font = QtGui.QFont()
        font.setFamily("Consolas")
        self.checkBox.setFont(font)
        self.checkBox.setChecked(True)
        self.checkBox.setObjectName("checkBox")
        self.allow_hb.addWidget(self.checkBox)
        self.verticalLayout_2.addLayout(self.allow_hb)
        self.axis_hb = QtWidgets.QHBoxLayout()
        self.axis_hb.setObjectName("axis_hb")
        self.label = MLabel()
        font = QtGui.QFont()
        font.setFamily("Consolas")
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.axis_hb.addWidget(self.label)
        self.comboBox = MComboBox()
        font = QtGui.QFont()
        font.setFamily("Consolas")
        self.comboBox.setFont(font)
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.axis_hb.addWidget(self.comboBox)
        self.verticalLayout_2.addLayout(self.axis_hb)
        self.mode_hb = QtWidgets.QHBoxLayout()
        self.mode_hb.setObjectName("mode_hb")
        self.mode_lb = MLabel()
        font = QtGui.QFont()
        font.setFamily("Consolas")
        self.mode_lb.setFont(font)
        self.mode_lb.setObjectName("mode_lb")
        self.mode_hb.addWidget(self.mode_lb)
        self.mode_combo = MComboBox()
        font = QtGui.QFont()
        font.setFamily("Consolas")
        self.mode_combo.setFont(font)
        self.mode_combo.setObjectName("mode_combo")
        self.mode_combo.addItem("")
        self.mode_combo.addItem("")
        self.mode_combo.addItem("")
        self.mode_hb.addWidget(self.mode_combo)
        self.verticalLayout_2.addLayout(self.mode_hb)
        self.create_hb = QtWidgets.QHBoxLayout()
        self.create_hb.setObjectName("create_hb")
        self.verticalLayout_2.addLayout(self.create_hb)
        self.create_btn = MPushButton(Form)
        font = QtGui.QFont()
        font.setFamily("Consolas")
        self.create_btn.setFont(font)
        self.create_btn.setObjectName("create_btn")
        self.verticalLayout_2.addWidget(self.create_btn)
        self.bridge_list = QtWidgets.QListWidget(Form)
        self.bridge_list.setObjectName("bridge_list")
        self.verticalLayout_2.addWidget(self.bridge_list)
        self.apply_hb = QtWidgets.QHBoxLayout()
        self.apply_hb.setObjectName("apply_hb")
        self.apply_btn = MPushButton()
        font = QtGui.QFont()
        font.setFamily("Consolas")
        font.setPointSize(11)
        font.setBold(False)
        font.setWeight(50)
        self.apply_btn.setFont(font)
        self.apply_btn.setObjectName("apply_btn")
        self.apply_hb.addWidget(self.apply_btn)
        self.mirror_btn = MPushButton()
        font = QtGui.QFont()
        font.setFamily("Consolas")
        font.setPointSize(11)
        font.setBold(False)
        font.setWeight(50)
        self.mirror_btn.setFont(font)
        self.mirror_btn.setObjectName("mirror_btn")
        self.apply_hb.addWidget(self.mirror_btn)
        self.verticalLayout_2.addLayout(self.apply_hb)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.node_lb.setText(u"WD 节点")
        self.node_combo.setItemText(0, _translate("Form", "New"))
        self.nodeSelect_btn.setToolTip(u"选择")
        self.nodeSave_btn.setToolTip(u"导出")
        self.nodeOpen_btn.setToolTip(u"导入")
        self.driver_lb.setText(u"驱动骨骼")
        self.driver_le.setPlaceholderText(u"请选择一个驱动骨骼.")
        self.driverSelect_btn.setToolTip(u"选择")
        self.parent_lb.setText(u"父级")
        self.parentSelect_btn.setToolTip(u"选择")
        self.contrl_lb.setText(u"控制物体")
        self.controlSelect_btn.setToolTip(u"选择")
        self.allow_cb.setText(u"允许负值")
        self.checkBox.setText(u"显示UI")
        self.label.setText(u"Twist 轴向")
        self.comboBox.setItemText(0, _translate("Form", "X"))
        self.comboBox.setItemText(1, _translate("Form", "Y"))
        self.comboBox.setItemText(2, _translate("Form", "Z"))
        self.mode_lb.setText(u"模式")
        self.mode_combo.setItemText(0, _translate("Form", "Rotate"))
        self.mode_combo.setItemText(1, _translate("Form", "Rotate/Twist"))
        self.mode_combo.setItemText(2, _translate("Form", "Twist"))
        self.create_btn.setText(u"创建")
        self.apply_btn.setText(u"确认")
        self.mirror_btn.setText(u"镜像")
from dayu_widgets.check_box import MCheckBox
from dayu_widgets.combo_box import MComboBox
from dayu_widgets.label import MLabel
from dayu_widgets.line_edit import MLineEdit
from dayu_widgets.push_button import MPushButton
from dayu_widgets.static import icon_rc
