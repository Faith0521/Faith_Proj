


def getSystemConnectionClass(connectionType):
	return _getClass(connectionType, "connection", "SystemConnection")

def getConnectionWidgetClass(connectionType):
	return _getClass(connectionType, "widget", "ConnectionWidget")

def _getClass(connectionType, moduleName, classSuffix):
	# Get Module
	moduleName = ".".join(["brigks", "connections", connectionType, moduleName])	
	module = __import__(moduleName, globals(), locals(), ["*"], -1)

	className = connectionType[0].upper()+connectionType[1:]+classSuffix
	Class = getattr(module, className)

	return Class