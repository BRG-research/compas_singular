import compas

try:
	import rhinoscriptsyntax as rs

except ImportError:
    compas.raise_if_ironpython()

from compas_rhino.geometry import RhinoGeometry

from compas_pattern.datastructures.pattern import Pattern
from compas_pattern.datastructures.quad_mesh import QuadMesh
from compas_pattern.datastructures.coarse_quad_mesh import CoarseQuadMesh

from compas_pattern.cad.rhino.input_functions import input_add
from compas_pattern.cad.rhino.input_functions import input_delete
from compas_pattern.cad.rhino.input_functions import input_change

from compas_pattern.cad.rhino.singularity_functions import medial_axis_singularity_mesh
from compas_pattern.cad.rhino.singularity_functions import edit_singularity_mesh

from compas_pattern.cad.rhino.density_functions import densification_equal_density_parameters
from compas_pattern.cad.rhino.density_functions import densification_target_based_density_parameters
from compas_pattern.cad.rhino.density_functions import set_strip_density_parameter

from compas_pattern.cad.rhino.topology_functions import reset_topology_mesh
from compas_pattern.cad.rhino.topology_functions import global_topology
from compas_pattern.cad.rhino.topology_functions import local_topology

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2018, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'


__all__ = [
	'main_menu',
	'input_menu',
	'singularity_menu',
	'density_menu',
	'pattern_menu',
	'geometry_menu',
	'settings_menu',
	'initiate_layers',
	'initiate_pattern',
	'explore_pattern',
]


def main_menu():
	"""Display main menu to select what to explore.

	Parameters
	----------

	Returns
	-------
	string
		Which submenu to explore for exploration.

	"""
	return rs.GetString('explore', strings = ['input', 'singularity', 'density', 'topology', 'geometry', 'settings', 'exit'])

def input_menu(pattern):
	"""Modify input.

	Parameters
	----------
	pattern : Pattern
		The pattern instance.

	Returns
	-------

	"""

	functions = {'add': input_add, 'delete': input_delete, 'change': input_change}
	func =  rs.GetString('input', strings = list(functions))
	if func in functions:
		functions[func]()

def singularity_menu(pattern):
	"""Modify singularites.

	Parameters
	----------
	pattern : Pattern
		The pattern instance.

	Returns
	-------
	string
		Which modification to do.

	"""

	functions = {'new_from_medial_axis': medial_axis_singularity_mesh, 'edit_existing': edit_singularity_mesh}
	func =  rs.GetString('singularity', strings = list(functions))
	if func in functions:
		functions[func](pattern)

	pattern.draw_singularity()
	pattern.draw_density()
	pattern.draw_topology()
	pattern.draw_geometry()
	
def density_menu(pattern):
	"""Modify density.

	Parameters
	----------
	pattern : Pattern
		The pattern instance.

	Returns
	-------
	string
		Which modification to do.

	"""

	functions = {'densify_equal': densification_equal_density_parameters, 'densify_target': densification_target_based_density_parameters, 'densify_edit': set_strip_density_parameter}
	func =  rs.GetString('density', strings = list(functions))
	if func in functions:
		functions[func](pattern)

	pattern.draw_density()
	pattern.draw_topology()
	pattern.draw_geometry()

def topology_menu(pattern):
	"""Display topology menu to select what to modify.

	Parameters
	----------
	pattern : Pattern
		The pattern instance.

	Returns
	-------
	string
		Which modification to do.

	"""

	functions = {'reset': reset_topology_mesh, 'global': global_topology, 'local': local_topology}
	func =  rs.GetString('topology', strings = list(functions))
	if func in functions:
		functions[func](pattern)

	pattern.draw_topology()
	pattern.draw_geometry()

def geometry_menu(pattern):
	"""Display geometry menu to select what to modify.

	Parameters
	----------
	pattern : Pattern
		The pattern instance.

	Returns
	-------
	string
		Which modification to do.

	"""
	return rs.GetString('geometry', strings = ['smoothing_type', 'number_of_iterations', 'damping_factor'])

def settings_menu(pattern):

	settings = pattern.settings

	new_values = rs.PropertyListBox(settings.keys(), settings.values(), 'modify setting(s)?', 'Settings')

	pattern.settings = {setting: float(value) for setting, value in zip(settings.keys(), new_values)}

def initiate_layers():
	"""Add layer structure.

	Parameters
	----------

	Returns
	-------

	"""

	layers = ['input', 'singularity', 'density', 'topology', 'geometry', 'default']
	colors = [[255,0,0], [0,0,0], [200,200,200], [100,100,100], [0,0,0], [0,0,0]]
	for layer, color in zip(layers, colors):
		rs.AddLayer(layer, color)

def initiate_pattern(default_settings):
	"""Initiate an empty pattern class with default settings.

	Parameters
	----------
	default_settings : dict
		A dictionary of default settings.

	Returns
	-------
	pattern : Pattern
		A pattern instance
	"""

	pattern = Pattern(default_settings)

	return pattern


def explore_pattern(default_settings = {
										'discretisation': 1.,
										'density_target_length': 1.,
										'density_global_parameter': 2
										}):
	"""Explore!

	Parameters
	----------

	Returns
	-------

	"""

	initiate_layers()
	pattern = initiate_pattern(default_settings)
	pattern.collect_all_data()

	submenus = {
				'input': input_menu,
				'singularity': singularity_menu,
				'density': density_menu,
				'topology': topology_menu,
				'geometry': geometry_menu,
				'settings': settings_menu}

	while 1:
		
		submenu = main_menu()

		if submenu == 'exit':
			break

		else:
			if submenu in submenus:
				submenus[submenu](pattern)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	import compas