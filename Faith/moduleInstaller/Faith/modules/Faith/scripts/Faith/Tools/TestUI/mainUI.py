from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSlot


class WinForm(QWidget):
    # button_clicked_signal = pyqtSignal(str, int)	# 信号需要传入指定类型的两个参数
    # button_clicked_signal02 = pyqtSignal(str, int)

    def __init__(self):
        super().__init__()
        self.resize(500, 400)
        self.btn_colse = QPushButton('close', self)
        self.btn_colse.clicked.connect(self.btn_clicked)
        self.line_edit = QLineEdit(self)
        self.line_edit.move(200, 200)

    @pyqtSlot()
    def btn_clicked(self):
        if self.btn_colse.text() == "close":
            self.show_edit('btn clicked', 1)
        elif self.btn_colse.text() == "open":
            self.show_edit02('btn clicked', 1)

    def show_edit(self, msg, tag):
        self.line_edit.setText('msg %s, tag: %s' % (msg, tag))
        self.btn_colse.setText("open")

    def show_edit02(self, msg, tag):
        self.line_edit.setText('msg %s, tag: %s.....' % (msg, tag))
        self.btn_colse.setText("close")

if __name__ == '__main__':

    app = QApplication([])
    main = WinForm()
    main.show()
    app.exec()
