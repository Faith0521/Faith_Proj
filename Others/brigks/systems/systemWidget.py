import os.path

import logging

from Qt import QtCompat
from Qt.QtWidgets import QWidget, QCheckBox, QComboBox, QSpinBox, QDoubleSpinBox, QLineEdit, QListWidget, QPlainTextEdit

class SystemWidget(QWidget):

	def __init__(self, guide):
		super(SystemWidget, self).__init__()

		self._guide = None
		self._widgets = None
		self._builder = None

		# Load UI File
		module = __import__(self.__module__, globals(), locals(), ["*"], -1)
		uiPath = os.path.join(os.path.dirname(module.__file__), "widget.ui")
		QtCompat.loadUi(uiPath, self)

		if guide:
			self.setSystem(guide)


	def setSystem(self, guide):
		self._guide = guide
		self._builder = None
		self.layer = self._guide.layer
		self.settings = self._guide.settings
		self.setSettings = self._guide.setSettings
		self.count = self._guide.count
		self.isBuilt = self._guide.isBuilt
		self.markers = self._guide.markers

		if not self._widgets:
			self._widgets = self.getSettingWidgets()

		self.load()
		self.connectWidgets(self._widgets)

	def guide(self):
		return self._guide

	# -----------------------------------------------------
	# GET
	# -----------------------------------------------------
	def getObject(self, use, part):
		if not self._builder:
			self._builder = self._guide.builder()
		self._builder.getObject(use, part)

	def getAttribute(self, part):
		if not self._builder:
			self._builder = self._guide.builder()
		self._builder.getAttribute(part)

	# -----------------------------------------------------
	# WIDGETS
	# -----------------------------------------------------
	def getSettingWidgets(self):
		widgets = {}
		for setting in self._guide.settings().keys():
			widgetName = "ui" + setting[0].capitalize() + setting[1:]
			if widgetName not in self.__dict__:
				continue
			widgets[setting] = self.__dict__[widgetName]
		return widgets
	
	def connectWidgets(self, widgets):
		for widget in widgets.values():
			try:
				widget.disconnect()
			except TypeError:
				pass

			if isinstance(widget, QCheckBox):
				widget.stateChanged.connect(self.commit)
			elif isinstance(widget, QComboBox):
				widget.currentIndexChanged.connect(self.commit)
			elif isinstance(widget, QSpinBox) or isinstance(widget, QDoubleSpinBox):
				widget.valueChanged.connect(self.commit)
			elif isinstance(widget, QLineEdit):
				widget.editingFinished.connect(self.commit)
			elif isinstance(widget, QListWidget):
				widget.currentItemChanged.connect(self.commit)
			elif isinstance(widget, QPlainTextEdit):
				widget.textChanged.connect(self.commit)
	
	# -----------------------------------------------------
	# SETTINGS
	# -----------------------------------------------------
	def load(self):
		for setting, value in self._guide.settings().items():
			if setting not in self._widgets:
				continue
			
			widget = self._widgets[setting]
			widget.blockSignals(True)
				
			if isinstance(widget, QCheckBox):
				widget.setChecked(value)
			elif isinstance(widget, QSpinBox) or isinstance(widget, QDoubleSpinBox):
				widget.setValue(value)
			elif isinstance(widget, QLineEdit):
				widget.setText(value)
			elif isinstance(widget, QComboBox):
				allItems = [widget.itemText(i) for i in range(widget.count())]
				if value not in allItems:
					logging.debug("Invalid value for {s} - {v}".format(s=setting, v=value))
					continue
				widget.setCurrentIndex(allItems.index(value))
			elif isinstance(widget, QListWidget):
				for s in value:
					widget.addItem(s)
			elif isinstance(widget, QPlainTextEdit):
				widget.setPlainText(value)

			widget.blockSignals(False)
	
	def commit(self):
		settings = {}
		for setting, widget in self._widgets.iteritems():
			if isinstance(widget, QCheckBox):
				settings[setting] = widget.isChecked()
			elif isinstance(widget, QSpinBox) or isinstance(widget, QDoubleSpinBox):
				settings[setting] = widget.value()
			elif isinstance(widget, QLineEdit):
				settings[setting] = str(widget.text())
			elif isinstance(widget, QComboBox):
				settings[setting] = str(widget.currentText())
			elif isinstance(widget, QListWidget):
				settings[setting] = [str(widget.item(row).text()) for row in xrange(widget.count())]
			elif isinstance(widget, QPlainTextEdit):
				settings[setting] = str(widget.toPlainText())

		self.setSettings(**settings)
		self._guide.commit()