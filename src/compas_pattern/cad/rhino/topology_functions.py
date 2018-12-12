import compas

try:
	import rhinoscriptsyntax as rs

except ImportError:
    compas.raise_if_ironpython()

from compas_pattern.topology.conway_operators import *

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2018, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'


__all__ = [
	'reset_topology_mesh',
	'global_topology',
	'local_topology'
]

def reset_topology_mesh(pattern):
	"""Reeset topology mesh from density mesh.

	Parameters
	----------

	Returns
	-------

	"""

	pattern.topology_mesh = pattern.density_mesh

def global_topology(pattern):
	"""Global topological editing of the density mesh.

	Parameters
	----------
	pattern : Pattern
		The pattern instance.

	Returns
	-------

	"""

	conway_operators = {
		'conway_dual': conway_dual,
		'conway_join': conway_join,
		'conway_ambo': conway_ambo,
		'conway_kis': conway_kis,
		'conway_needle': conway_needle,
		'conway_zip': conway_zip,
		'conway_truncate': conway_truncate,
		'conway_ortho': conway_ortho,
		'conway_expand': conway_expand,
		'conway_gyro': conway_gyro,
		'conway_snub': conway_snub,
		'conway_meta': conway_meta,
		'conway_bevel': conway_bevel
	}

	op =  rs.GetString('topology', strings = list(conway_operators))
	if op in conway_operators:
		pattern.topology_mesh = conway_operators[op](pattern.topology_mesh)

def local_topology(pattern):
	"""Local topological editing of the density mesh.

	Parameters
	----------

	Returns
	-------

	"""




# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	import compas