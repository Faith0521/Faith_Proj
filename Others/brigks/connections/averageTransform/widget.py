import os.path
from Qt import QtCompat

from brigks.gui.pickObjectDialog import PickObjectDialog
from brigks.connections.systemConnectionWidget import SystemConnectionWidget


class AverageTransformConnectionWidget(SystemConnectionWidget):

	def __init__(self, connection, system):
		super(AverageTransformConnectionWidget, self).__init__(connection, system)
