import compas

try:
	import rhinoscriptsyntax as rs

except ImportError:
	    compas.raise_if_ironpython()

from compas_pattern.datastructures.coarse_quad_mesh import CoarseQuadMesh

from compas_pattern.algorithms.densification import densify_quad_mesh

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2018, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'


__all__ = [
	'densification_equal_density_parameters',
	'densification_target_based_density_parameters',
	'set_strip_density_parameter'
]

def densification_equal_density_parameters(pattern):
	"""Densify coarse quad mesh based on equal density parameter.

	Parameters
	----------
	pattern : Pattern
		The pattern instance.

	Returns
	-------

	"""

	density_global_parameter = int(pattern.settings['density_global_parameter'])

	pattern.singularity_mesh.density_global_parameter(density_global_parameter)

	mesh = densify_quad_mesh(pattern.singularity_mesh)

	pattern.density_mesh = mesh
	pattern.topology_mesh = mesh
	pattern.geometry_mesh = mesh

def densification_target_based_density_parameters(pattern):
	"""Densify coarse quad mesh based on target length.

	Parameters
	----------
	pattern : Pattern
		The pattern instance.

	Returns
	-------

	"""

	density_target_length = pattern.settings['density_target_length']

	pattern.singularity_mesh.density_target_length(density_target_length)

	mesh = densify_quad_mesh(pattern.singularity_mesh)

	pattern.density_mesh = mesh
	pattern.topology_mesh = mesh
	pattern.geometry_mesh = mesh
	
def set_strip_density_parameter(pattern):

	return 0

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	import compas