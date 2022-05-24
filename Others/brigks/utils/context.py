'''Context Module

This module offer convinient context and decorators
'''
import contextlib
from functools import wraps
import datetime
import logging

from maya import cmds

@contextlib.contextmanager
def selection(*args, **kwargs):
	'''A context manager that resets selections after exiting
	'''
	existing = cmds.ls(selection=True, long=True) or []
	try:
		yield existing
	finally:
		if existing:
			existing = [x for x in existing if cmds.objExists(x)]
			cmds.select(existing, replace=True)
		else:
			cmds.select(clear=True)

class undoChunk(object):
	'''A context to wrap your script in single undo chunk
	'''
	def __init__(self, name="", raise_error=True):
		self.raise_error = raise_error
		self.name = name

	def __enter__(self):
		cmds.undoInfo(openChunk=True, chunkName=self.name)
		cmds.waitCursor(state=True)
		cmds.refresh(suspend =True)

	def __exit__(self, exc_type, exc_val, exc_tb):
		""" Turn refresh on again and raise errors if asked """
		cmds.refresh(suspend =False)
		cmds.refresh()
		cmds.waitCursor(state=False)
		cmds.undoInfo(closeChunk=True)
		if exc_type is not None:
			if self.raise_error:
				import traceback
				traceback.print_tb(exc_tb)
				raise exc_type, exc_val
			else:
				sys.stderr.write("%s" % exc_val)

# ----------------------------------------------------------------------------------
# DECORATOR
# ----------------------------------------------------------------------------------
def command(resetSelection=True):
	'''A decorator to wrap your method with undo, time stamp and reset selection.

	Args:
		resetSelection (bool): Restore the current selection
	'''
	def wrapper(func):
		name = func.__name__
		@wraps(func)
		def decorator(*args, **kwargs):
			ts = datetime.datetime.now()

			if resetSelection:
				with selection():
					with undoChunk(name):
						result = func(*args, **kwargs)
			else:
				with undoChunk(name):
					result = func(*args, **kwargs)

			te = datetime.datetime.now()
			logging.info('{n} [{t}]'.format(n=name, t=te-ts))
			return result 
		return decorator
	return wrapper
