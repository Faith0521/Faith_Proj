
from Qt.QtWidgets import QMessageBox

from brigks import Guide
from brigks.utils import gui
from brigks.gui import actions
from brigks.gui.mainWindow import MainWindow

def showWindow():
	# Get Maya Window for parenting
	maya = gui.getMayaWindow()

	guides = actions.findGuides()
	if guides:
		guide = guides[0]
	else:
		if not QMessageBox.question(maya, "Brigks", "No Guide in the scene, do you wante to create a new one?"):
			return 
		guide = Guide()

	window = MainWindow(guide, maya)
	window.show()
	return window

