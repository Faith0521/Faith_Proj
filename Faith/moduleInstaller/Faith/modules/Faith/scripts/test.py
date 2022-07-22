# !/usr/bin/python3
# -*-coding:utf-8-*-
# Author: Yin Yu Fei
# Github: https://github.com/
# CreatDate: 2022-07-21 14:13
# Description:

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLineEdit, QDoubleSpinBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.title = "PyQt5 button"
        self.left = 10
        self.top = 10
        self.width = 320
        self.height = 200
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        """在窗体内创建button对象"""
        button = QPushButton("PyQt5 Button", self)
        self.line = QDoubleSpinBox(self)
        """方法setToolTip在用户将鼠标停留在按钮上时显示的消息"""
        button.setToolTip("This is an example button")
        """按钮坐标x = 100, y = 70"""
        button.move(100, 70)
        """按钮与鼠标点击事件相关联"""
        button.clicked.connect(self.on_click)

        self.show()

    """创建鼠标点击事件"""

    @pyqtSlot()
    def on_click(self):
        self.line.setStyleSheet("background:rgb(20,81,179);")
        print("PyQt5 button click")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())




