import os.path
import shiboken2

from Qt import QtCompat
from Qt.QtCore import Signal
from Qt.QtWidgets import QWidget

from brigks.utils import gui
from brigks.config import LOCATIONS
from brigks.systems import getSystemWidgetClass, getSystemVersions
from brigks.gui.connectionWidget import ConnectionWidget
from brigks.gui.scriptWidget import ScriptWidget

class SystemSettingsWidget(QWidget):

	systemChanged = Signal(object)
	systemRenamed = Signal(str)

	def __init__(self, system):
		super(SystemSettingsWidget, self).__init__()
		uiPath = os.path.join(os.path.dirname(__file__), "ui", "systemSettingsWidget.ui")
		QtCompat.loadUi(uiPath, self)

		self._system = None
		self._connectionWidgets = {}
		self._settingsWidgets = {}
		self._settingsWidget = None

		self.uiPreScriptWDG = ScriptWidget("pre")
		self.uiScriptsTAB.layout().addWidget(self.uiPreScriptWDG)
		self.uiPostScriptWDG = ScriptWidget("post")
		self.uiScriptsTAB.layout().addWidget(self.uiPostScriptWDG)

		if system:
			self.setSystem(system)

		# Connect Signals
		self.uiTypeCBOX.currentIndexChanged.connect(self.swap)
		self.uiVersionCBOX.currentIndexChanged.connect(self.swap)
		self.uiLocationCBOX.currentIndexChanged.connect(self.rename)
		self.uiNameLINE.editingFinished.connect(self.rename)
		self.uiAddConnectionBTN.clicked.connect(self.addConnection)
		self.uiConnectionPortCBOX.currentIndexChanged.connect(self.loadConnectionTypes)

		self.uiPreScriptWDG.updated.connect(self.scriptUpdated)
		self.uiPostScriptWDG.updated.connect(self.scriptUpdated)

	def setSystem(self, system):
		self._system = system

		# Block Signals
		self.blockSignals(True)

		# Common
		compatibleSystems = [self._system.type()] + self._system.markerCompatibility.keys()
		self.uiTypeCBOX.clear()
		self.uiTypeCBOX.addItems(compatibleSystems)
		self.uiTypeCBOX.setCurrentIndex(0)

		versions = getSystemVersions(self._system.type())
		self.uiVersionCBOX.clear()
		self.uiVersionCBOX.addItems(versions)
		self.uiVersionCBOX.setCurrentIndex(versions.index(self._system.version()))

		self.uiLocationCBOX.clear()
		self.uiLocationCBOX.addItems(LOCATIONS.values())
		self.uiLocationCBOX.setCurrentIndex(LOCATIONS.keys().index(system.settings("location")))

		self.uiNameLINE.setText(system.settings("name"))

		# Settings
		if self._settingsWidget:
			self.uiSettingsTAB.layout().removeWidget(self._settingsWidget)
			self._settingsWidget.setVisible(False)
			#TODO shiboken2 delete?

		if system.type() not in self._settingsWidgets:
			WidgetClass = getSystemWidgetClass(system.type())
			self._settingsWidgets[system.type()] = WidgetClass(system)
		else:
			self._settingsWidgets[system.type()].setSystem(system)

		self._settingsWidget = self._settingsWidgets[system.type()]
		self.uiSettingsTAB.layout().addWidget(self._settingsWidget)
		self._settingsWidget.setVisible(True)

		# Add Connections Widget
		self.clearConnectionWidgets()
		connections = sorted(system.connections().items(), key=lambda x: x[0])
		for port, connection in connections:
			self.addConnectionWidget(port, connection)

		# Script Widgets
		self.uiPreScriptWDG.setObject(system)
		self.uiPostScriptWDG.setObject(system)

		# Block Signals
		self.blockSignals(False)

	def blockSignals(self, block):
		self.uiTypeCBOX.blockSignals(block)
		self.uiVersionCBOX.blockSignals(block)
		self.uiLocationCBOX.blockSignals(block)
		self.uiNameLINE.blockSignals(block)

	def commit(self):
		self._system.guide().commit()

	# ----------------------------------------------------------------------------------
	# SYSTEMS
	# ----------------------------------------------------------------------------------
	def rename(self):
		location = LOCATIONS.keys()[self.uiLocationCBOX.currentIndex()]
		name = self.uiNameLINE.text()
		self._system.rename(location, name)

		self.systemRenamed.emit(self._system.key())

	def swap(self):
		systemType = self.uiTypeCBOX.currentText()
		systemVersion = self.uiVersionCBOX.currentText()

		newSystem = self._system.layer().swapSystem(self._system, systemType, systemVersion)
		self.setSystem(newSystem)
		self.commit()

		self.systemChanged.emit(newSystem)

	# ----------------------------------------------------------------------------------
	# CONNECTIONS
	# ----------------------------------------------------------------------------------
	def clearConnectionWidgets(self):
		self.updateConnectionWidgets()
		for widget in self._connectionWidgets.values():
			self.uiConnectionsLAY.removeWidget(widget)
			widget.deleteLater()
			# sip.delete(widget)
		self._connectionWidgets = {}

	def updateConnectionWidgets(self):
		hasPortAvailable = len(self.portsAvailable()) > 0
		self.uiAddConnectionBTN.setEnabled(hasPortAvailable)
		self.uiConnectionPortCBOX.setEnabled(hasPortAvailable)
		self.uiConnectionTypeCBOX.setEnabled(hasPortAvailable)

		self.loadConnectionPorts()
		self.loadConnectionTypes()

	def portsAvailable(self):
		allPorts = self._system.connectionPorts().keys()
		cnxPorts = self._system.connections().keys()
		return [p for p in allPorts if p not in cnxPorts]

	def loadConnectionPorts(self):
		self.uiConnectionPortCBOX.clear()
		self.uiConnectionPortCBOX.addItems(sorted(self.portsAvailable()))

	def loadConnectionTypes(self):
		self.uiConnectionTypeCBOX.clear()
		port = self.uiConnectionPortCBOX.currentText()
		if port:
			types = self._system.connectionPorts()[port]
			self.uiConnectionTypeCBOX.addItems(types)

	def addConnection(self):
		port = self.uiConnectionPortCBOX.currentText()
		connectionType = self.uiConnectionTypeCBOX.currentText()

		connection = self._system.addConnection(port, connectionType)
		self.addConnectionWidget(port, connection)

		self.commit()

	def addConnectionWidget(self, port, connection):
		if port in self._connectionWidgets:
			raise RuntimeError("Port {} already exists".format(port))

		widget = ConnectionWidget(port, connection, self._system)
		widget.deleted.connect(lambda: self.deleteConnectionWidget(port))
		self.uiConnectionsLAY.addWidget(widget)
		self._connectionWidgets[port] = widget

		self.updateConnectionWidgets()

	def deleteConnectionWidget(self, port):
		# Delete Connection from System
		self._system.deleteConnection(port)
		self.commit()

		# Delete Connection Widget
		widget = self._connectionWidgets.pop(port)
		self.uiConnectionsLAY.removeWidget(widget)
		shiboken2.delete(widget)

		self.updateConnectionWidgets()

	# ----------------------------------------------------------------------------------
	# SCRIPTS
	# ----------------------------------------------------------------------------------
	def scriptUpdated(self, settings):
		self._system.setSettings(**settings)
		self.commit()