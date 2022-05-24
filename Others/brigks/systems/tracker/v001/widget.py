

from brigks.systems.systemWidget import SystemWidget

# TODO

class TrackerSystemWidget(SystemWidget):


	def setSystem(self, guide):
		self.definitions = {}
		self.ordered = []
		self.interpTypes = ["None","Linear","Smooth","Spline"]
		super(TrackerSystemWidget, self).setSystem(guide)

	def connectWidgets(self, widgets):
		super(TrackerSystemWidget, self).connectWidgets(widgets)

		self.uiNameLINE.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp('[A-Z][0-9a-zA-Z]+'), self.uiNameLINE))

		self.uiGrabMinBTN.clicked.connect(lambda:self.grabFromRig("min"))
		self.uiGrabMaxBTN.clicked.connect(lambda:self.grabFromRig("max"))

		self.uiAddBTN.clicked.connect(self.addAttrDefinition)
		self.uiRemoveBTN.clicked.connect(self.deleteAttrDefinition)
		self.uiUpBTN.clicked.connect(lambda : self.moveAttrDefinition("up"))
		self.uiDownBTN.clicked.connect(lambda : self.moveAttrDefinition("down"))

		self.uiDriverLIST.currentItemChanged.connect(self.loadDefinition)

		self.connectDefinitionChanged()

	def connectDefinitionChanged(self):
		self.uiNameLINE.editingFinished.connect(self.attrNameChanged)
		self.uiInterpTypeCBOX.currentIndexChanged.connect(self.attrDefinitionChanged)
		self.uiAxisCBOX.currentIndexChanged.connect(self.attrDefinitionChanged)
		self.uiMinSPN.valueChanged.connect(self.attrDefinitionChanged)
		self.uiMaxSPN.valueChanged.connect(self.attrDefinitionChanged)

	def disconnectDefinitionChanged(self):
		self.uiNameLINE.editingFinished.disconnect(self.attrNameChanged)
		self.uiInterpTypeCBOX.currentIndexChanged.disconnect(self.attrDefinitionChanged)
		self.uiAxisCBOX.currentIndexChanged.disconnect(self.attrDefinitionChanged)
		self.uiMinSPN.valueChanged.disconnect(self.attrDefinitionChanged)
		self.uiMaxSPN.valueChanged.disconnect(self.attrDefinitionChanged)

	# -------------------------------------------------------------
	# LOAD / SAVE
	# -------------------------------------------------------------
	def load(self):
		self._definitions = copy.deepcopy(self.settings("definitions"))

		self.ordered = [attrName for attrName in self.settings("order") if attrName in self._definitions]

		for attrName in self._definitions.keys():
			if attrName not in self.ordered:
				self.ordered.append(attrName)

		self.uiDriverLIST.clear()
		self.uiDriverLIST.addItems(self.ordered)

		self.commit()

	def loadDefinition(self):
		attrName = self._getCurrentAttrName()
		if not attrName:
			self.uiDefinitionGRP.setEnabled(False)
			return 

		self.uiDefinitionGRP.setEnabled(True)

		self.disconnectDefinitionChanged()


		definition = self._definitions[attrName]
		self.uiNameLINE.setText(attrName)

		self.uiAxisCBOX.setCurrentIndex

		axis_ = definition["axis"]
		interpolation_ = definition["interpolation"]
		self.uiInterpTypeCBOX.setCurrentIndex(self.interpTypes.index(interpolation_))
		self.uiAxisCBOX.setCurrentIndex("XYZ".index(axis_))
		self.uiMinSPN.setValue(definition["min"])
		self.uiMaxSPN.setValue(definition["max"])

		self.connectDefinitionChanged()

	def commit(self):
		settings = dict(
			order=self.ordered, 
			definitions=copy.deepcopy(self._definitions)
			)

		self.setSettings(**settings)
		self._guide.commit()


	# -------------------------------------------------------------
	# BUTTONS
	# -------------------------------------------------------------
	def addAttrDefinition(self):
		attrName = self._getNextAvailableName("NewDriver")

		self.uiDriverLIST.addItem(attrName)


		definition = {	"axis":"Z",
					    "min":0,
					   	"max":0,
					   	"interpolation":"Linear"}

		self._definitions[attrName] = definition

		self.attrOrderChanged()

		self.uiDriverLIST.setCurrentRow(self.ordered.index(attrName))

	def deleteAttrDefinition(self):
		index = self.uiDriverLIST.currentRow()
		item = self.uiDriverLIST.takeItem(index)
		attrName = str(item.text())

		self._definitions.pop(attrName)

		self.attrOrderChanged()

	def moveAttrDefinition(self, direction="up"):
		index = self.uiDriverLIST.currentRow()

		newIndex = index - 1 if direction == "up" else index + 1
		if newIndex < 0 or newIndex > self.uiDriverLIST.count():
			return 

		item = self.uiDriverLIST.takeItem(index)
		self.uiDriverLIST.insertItem(newIndex, item)
		self.uiDriverLIST.setCurrentItem(item)

		self.attrOrderChanged()

	def grabFromRig(self, minMax):
		if not self.access():
			self.warning("Tracker hasn't been built")
			return

		driverName = self._getCurrentAttrName()
		axis = "XYZ".index(self._definitions[driverName]["axis"])
		currentValue = cmds.getAttr(self.getAttribute("OutRot"))[axis]
		self._definitions[driverName][minMax] = currentValue

		self.commit()
		self.loadDefinition()

		# set the value back into the rig, if created
		attr = self.getAttribute("{}{}".format(driverName, minMax.capitalize()))
		if attr:
			cmds.setAttr(attr, currentValue)

	# -------------------------------------------------------------
	# EDIT
	# -------------------------------------------------------------
	def attrNameChanged(self):
		oldName = self._getCurrentAttrName()
		if not oldName:
			return 

		newName = str(self.uiNameLINE.text())
		if newName == oldName:
			return 

		newName = self._getNextAvailableName(newName)

		self.disconnectDefinitionChanged()
		self.uiNameLINE.setText(newName)
		item = self.uiDriverLIST.currentItem()
		item.setText(newName)
		self.connectDefinitionChanged()

		self.ordered[self.ordered.index(oldName)] = newName
		self._definitions[newName] = self._definitions.pop(oldName)

		self.commit()

	def attrDefinitionChanged(self):
		attrName = self._getCurrentAttrName()
		if not attrName:
			return 

		definition = dict(
			interpolation=self.uiInterpTypeCBOX.currentText(),
			axis=str(self.uiAxisCBOX.currentText()),
			min=self.uiMinSPN.value(),
			max=self.uiMaxSPN.value()
			)

		self._definitions[attrName].update(definition)

		self.commit()

	def attrOrderChanged(self):
		self.ordered = []
		for index in xrange(self.uiDriverLIST.count()):
			item = self.uiDriverLIST.item(index)
			self.ordered.append(str(item.text()))

		self.commit()

	# -------------------------------------------------------------
	# MISC
	# -------------------------------------------------------------
	def _getCurrentAttrName(self):
		if not self.uiDriverLIST.currentItem():
			return

		attrName = str(self.uiDriverLIST.currentItem().text())
		if attrName not in self._definitions:
			logging.error("Brigks : tracker system : Can't Find Attr in the list")
			return

		return attrName

	def _getNextAvailableName(self, name):
		if name not in self.settings("definitions"):
			return name

		i = 1
		while True:
			newName = name + str(i)
			if newName not in self.settings("definitions"):
				return newName

			i += 1 
