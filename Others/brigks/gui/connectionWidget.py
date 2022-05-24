import os.path

from Qt import QtCompat
from Qt.QtWidgets import QWidget
from Qt.QtCore import Signal
from brigks.connections import getConnectionWidgetClass

class ConnectionWidget(QWidget):

	deleted = Signal(str)

	def __init__(self, port, connection, system):
		super(ConnectionWidget, self).__init__()

		uiPath = os.path.join(os.path.dirname(__file__), "ui", "connectionWidget.ui")
		QtCompat.loadUi(uiPath, self)

		self._system = system
		self._connection = connection
		self._port = port

		Widget = getConnectionWidgetClass(connection.type())
		widget = Widget(connection, system)
		self.uiNameGRP.layout().addWidget(widget)
		
		# Set Title
		title = "{k} [{t}]".format(k=self._port, t=self._connection.type().title())
		self.uiNameGRP.setTitle(title)

		# Connect
		self.uiDeleteBTN.clicked.connect(self.delete)


	def delete(self):
		self.deleted.emit(self._port)