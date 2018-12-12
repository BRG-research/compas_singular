try:
	import rhinoscriptsyntax as rs

except ImportError:
    compas.raise_if_ironpython()

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2018, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'


__all__ = [
	'input_add',
	'input_delete',
	'input_change'
	'input_objects',
]

def input_add():
	"""Add input to input layer.

	Parameters
	----------

	Returns
	-------

	"""

	objects = rs.GetObjects('input to add')
	if objects is not None:
		rs.ObjectLayer(objects, 'input')

def input_delete():
	"""Delete input from input layer.

	Parameters
	----------

	Returns
	-------

	"""

	objects = rs.GetObjects('input to delete')
	if objects is not None:
		rs.ObjectLayer(objects, 'default')


def input_change():
	"""Change input in input layer.

	Parameters
	----------

	Returns
	-------

	"""

	input_delete()
	input_add()

def input_objects():
	"""Get input objects.

	Parameters
	----------

	Returns
	-------
	surfaces : list
		The guids of the surfaces
	points : list
		The guids of the points
	curves : list
		The guids of the curves

	"""

	input_objects = rs.ObjectsByLayer('input')
	surfaces = [obj for obj in input_objects if rs.ObjectType(obj) == 8]
	points = [obj for obj in input_objects if rs.ObjectType(obj) == 1]
	curves = [obj for obj in input_objects if rs.ObjectType(obj) == 4]

	return surfaces, points, curves

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	import compas