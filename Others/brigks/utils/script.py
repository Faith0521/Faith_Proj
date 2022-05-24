import os.path

from maya import cmds

def execute(path, value, args={}):
	'''Execute a script from a given path

	Args:
		path(str): Path to the python file with the code
		value(str): Code to default to, if the path doesn't exist
		args(dict): Extra local variabls to pass to the exexcution
	'''
	if os.path.exists(path):
		with open(path, "r") as f:
			value = f.read()

	exec(value, args, args)