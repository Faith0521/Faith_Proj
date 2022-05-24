from Qt.QtWidgets import QTreeWidgetItem
from Qt.QtGui import QBrush, QColor

COLOR_DEFAULT = QColor(100,100,100)
# COLOR_BUILT = QColor(72,170,180)
COLOR_BUILT = QColor(200,200,200)
COLOR_ERROR = QColor(200,20,20)

# ----------------------------------------------------------------------------------
# GUIDE
# ----------------------------------------------------------------------------------
class GuideTreeWidgetItem(QTreeWidgetItem):

	def __init__(self, parent, guide):
		super(GuideTreeWidgetItem, self).__init__(parent, ["Guide"])

		self._guide = guide

		sortedLayers = sorted(guide.layers().items(), key=lambda x: x[0])
		for name, layer in sortedLayers:
			LayerTreeWidgetItem(self, layer)

	def object(self):
		return self._guide

# ----------------------------------------------------------------------------------
# LAYER
# ----------------------------------------------------------------------------------
class LayerTreeWidgetItem(QTreeWidgetItem):

	def __init__(self, parent, layer):
		super(LayerTreeWidgetItem, self).__init__(parent, [layer.name()])

		self._layer = layer
		self.setExpanded(self._layer.settings()["expanded"])

		sortedSubLayers = sorted(layer.layers().items(), key=lambda x: x[0])
		for subName, subLayer in sortedSubLayers:
			LayerTreeWidgetItem(self, subLayer)

		sortedSystems = sorted(layer.systems().items(), key=lambda x: x[0])
		for key, system in sortedSystems:
			item = SystemTreeWidgetItem(self, system)

		color = COLOR_BUILT if self.isBuilt() else COLOR_DEFAULT
		self.setForeground(0, QBrush(color))

	def object(self):
		return self._layer

	def setLayerName(self, layerName):
		self.setText(0, layerName)

	def systems(self):
		systems = []
		for index in range(self.childCount()):
			item = self.child(index)
			if isinstance(item, LayerTreeWidgetItem):
				systems.extend(item.systems())
			else:
				systems.append(item.object())
		return systems

	def isBuilt(self):
		for system in self.systems():
			if system.isBuilt():
				return True
		return False


# ----------------------------------------------------------------------------------
# SYSTEM
# ----------------------------------------------------------------------------------
class SystemTreeWidgetItem(QTreeWidgetItem):

	def __init__(self, parent, system):
		super(SystemTreeWidgetItem, self).__init__(parent, [system.key(), system.type()])

		self._system = None
		self.setSystem(system)

		color = COLOR_BUILT if self._system.isBuilt() else COLOR_DEFAULT
		self.setForeground(0, QBrush(color))

		if system.settings()["location"] == "X":
			SubSystemTreeWidgetItem(self, system, location="L")
			SubSystemTreeWidgetItem(self, system, location="R")

	def object(self):
		return self._system

	def setSystem(self, system):
		self._system = system
		self.setText(1, system.type())

	def setSystemName(self, systemKey):
		self.setText(0, systemKey)


# ----------------------------------------------------------------------------------
# SUBSYSTEM
# ----------------------------------------------------------------------------------
class SubSystemTreeWidgetItem(QTreeWidgetItem):

	def __init__(self, parent, system, location):
		super(SubSystemTreeWidgetItem, self).__init__(parent, [system.key().replace("X", location)])

		self._system = system

	def object(self):
		return self._system


