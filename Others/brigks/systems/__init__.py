import os
from collections import defaultdict

def getSystemGuideClass(systemType, version=None):
	return _getClass(systemType, "guide", "SystemGuide", version)

def getSystemBuilderClass(systemType, version=None):
	return _getClass(systemType, "builder", "SystemBuilder", version)

def getSystemWidgetClass(systemType, version=None):
	return _getClass(systemType, "widget", "SystemWidget", version)

def _getClass(systemType, moduleName, classSuffix, version=None):
	if version is None:
		version = getSystemVersions(systemType)[-1]

	# Get Module
	moduleName = ".".join(["brigks", "systems", systemType, version, moduleName])
	module = __import__(moduleName, globals(), locals(), ["*"], -1)

	# Get Class
	className = systemType.title()+classSuffix
	try:
		Class = getattr(module, className)
	except AttributeError:
		msg = "'{m}' object has no attribute '{c}'".format(m=moduleName, c=className)
		raise AttributeError(msg)

	return Class


def getSystemList():
	folder = os.path.dirname(__file__)
	for root, dirs, files in os.walk(folder, topdown=True):
	   	return sorted(dirs)

def getSystemListByCategory():
	categories = defaultdict(list)
	folder = os.path.dirname(__file__)
	for root, dirs, files in os.walk(folder, topdown=True):
	   	for systemType in sorted(dirs):
			moduleName = ".".join(["brigks", "systems", systemType])
			module = __import__(moduleName, globals(), locals(), ["*"], -1)
			for cat in module.categories:
				categories["ALL"].append(systemType)
				categories[cat].append(systemType)
		break
	return categories

def getSystemVersions(systemType):
	# Get Module
	moduleName = ".".join(["brigks", "systems", systemType])
	module = __import__(moduleName, globals(), locals(), ["*"], -1)

	folder = os.path.dirname(module.__file__)
	for root, dirs, files in os.walk(folder, topdown=True):
	   	return sorted(dirs)