
from brigks import config

# ----------------------------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------------------------
def getSystemKey(location, name):
	'''Returns the sysyem key from location and name

	Args:
		location (str): System location (L,R,M,X...)
		name (str): name of the system
	
	Returns:
		str
	'''
	return "{name}_{location}".format(location=location, name=name)


def getObjectName(use, location, name, part):
	'''Returns the object name, matching the naming convention defined in the config

	Args:
		use (str): config.USE_GDE, USE_RIG, USE_JNT, USE_CTL
		location (str): System location (L,R,M,X...)
		name (str): Name of the system
		part (str): The unique name of the system part
	
	Returns:
		str
	'''
	return config.TOKENS.format(
					use=use,
					loc=location,
					name=name,
					part=part)