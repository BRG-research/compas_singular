import compas

try:
	import rhinoscriptsyntax as rs

except ImportError:
    compas.raise_if_ironpython()

from compas_pattern.algorithms.medial_axis_singularity_mesh import medial_axis_singularity_mesh_from_surface

from compas_pattern.cad.rhino.input_functions import input_objects

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2018, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'


__all__ = [
	'medial_axis_singularity_mesh',
	'edit_singularity_mesh',
]

def medial_axis_singularity_mesh(pattern):
	"""Generate singularity mesh from medial axis.

	Parameters
	----------
	pattern : Pattern
		The pattern instance.

	Returns
	-------

	"""

	surfaces, point_features, curve_features = input_objects()

	discretisation = pattern.settings['discretisation']

	if len(surfaces) == 1:
		pattern.singularity_mesh = medial_axis_singularity_mesh_from_surface(surfaces[0], point_features, curve_features, discretisation = discretisation)

	else:
		print 'there should be only one input surface'

def edit_singularity_mesh(pattern):
	"""Edit existing singularity mesh.

	Parameters
	----------
	pattern : Pattern
		The pattern instance.

	Returns
	-------

	"""




# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	import compas