import operator

from compas_pattern.algorithms.combination.arrange import arrange_in_spiral
from compas_pattern.cad.rhino.draw import draw_mesh

from compas_pattern.cad.rhino.artist import select_mesh_strip
from compas_pattern.cad.rhino.artist import select_mesh_polyedge

try:
	import rhinoscriptsyntax as rs
	import scriptcontext as sc

	from Rhino.Geometry import Point3d

	find_object = sc.doc.Objects.Find

except ImportError:
	import compas
	compas.raise_if_ironpython()

__all__ = [
	'select_topology_combination',
	'select_topology_combinations',
	'draw_topologies_in_spiral',
	'get_deletion_rule',
	'get_deletion_rules',
	'get_addition_rule',
	'get_addition_rules'
]


def select_topology_combination(topologies, callback=None, callback_args=None):

	guid_to_mesh = draw_topologies_in_spiral(topologies, callback, callback_args)

	guids = rs.GetObjects('select topologies', objects = guid_to_mesh.keys())
		
	rs.DeleteObjects(guid_to_mesh.keys())

	return {guid_to_mesh[guid]: topologies[guid_to_mesh[guid]] for guid in guids}


def select_topology_combinations(topologies, callback=None, callback_args=None):

	selected_topologies = []

	guid_to_mesh = draw_topologies_in_spiral(topologies, callback, callback_args)

	while True:

		guids = rs.GetObjects('select topologies', objects = guid_to_mesh.keys())
		
		if guids is None:
			rs.DeleteObjects(guid_to_mesh.keys())
			break

		selected_topologies.append({guid_to_mesh[guid]: topologies[guid_to_mesh[guid]] for guid in guids})

	return selected_topologies


def draw_topologies_in_spiral(meshes, callback=None, callback_args=None):
	
	if callback and callable(callback):
		new_meshes = {callback(mesh, callback_args): i for i, mesh in enumerate(meshes)}
	else:
		new_meshes = {mesh: i for i, mesh in enumerate(meshes)}
	
	arrange_in_spiral([key for key, value in sorted(new_meshes.items(), key=operator.itemgetter(1))])

	guid_to_mesh = {draw_mesh(mesh): mesh for mesh in new_meshes.keys()}

	return {guid: meshes[new_meshes[guid_to_mesh[guid]]] for guid in guid_to_mesh.keys()}


def get_deletion_rule(mesh):
	return select_mesh_strip(mesh)


def get_deletion_rules(mesh):
	all_skeys = list(mesh.strips())
	skeys = []
	count = 20
	while count:
		count -= 1
		skey = get_deletion_rule(mesh)
		if skey is None:
			break
		skeys.append([skey])

	return skeys


def get_addition_rule(mesh):
	return select_mesh_polyedge(mesh)


def get_addition_rules(mesh):
	polyedges = []
	count = 20
	while count:
		count -= 1
		polyedge = get_addition_rule(mesh)
		if polyedge == []:
			break
		polyedges.append(polyedge)

	return polyedges


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	import compas
	