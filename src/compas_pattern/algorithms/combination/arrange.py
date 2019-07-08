from math import pi

from compas_pattern.datastructures.mesh.operations import mesh_move_by

from compas.datastructures import mesh_bounding_box

from compas.geometry import centroid_points
from compas.geometry import weighted_centroid_points
from compas.geometry import distance_point_point
from compas.geometry import add_vectors
from compas.geometry import subtract_vectors

from compas.geometry import circle_evaluate
from compas.geometry import archimedean_spiral_evaluate

from compas_pattern.utilities.lists import common_items

__all__ = [
	'arrange_in_line',
	'arrange_in_circle',
	'arrange_in_spiral',
	'arrange_in_map'
]

def arrange_in_line(meshes, centre = None):

	if centre is None:
		centre = centroid_points([mesh.vertex_coordinates(vkey) for mesh in meshes for vkey in mesh.vertices()])

	# get object bounding box diagonal length
	widths = []
	for mesh in meshes:
		box = mesh_bounding_box(mesh)
		widths.append(distance_point_point(box[0], box[1]))
	
	# set scale based on maximum guid size
	k = 1.1
	scale = k * max(widths)	

	for i, mesh in enumerate(meshes):
		mesh_move(mesh, subtract_vectors(add_vectors(centre, [(i + 1) * scale, 0, 0]), mesh.centroid()))

def arrange_in_circle(meshes, centre = None, rmin = 0):

	if centre is None:
		centre = centroid_points([mesh.vertex_coordinates(vkey) for mesh in meshes for vkey in mesh.vertices()])

	# get object bounding box diagonal length
	diagonals = []
	for mesh in meshes:
		box = mesh_bounding_box(mesh)
		dx = distance_point_point(box[0], box[1])
		dy = distance_point_point(box[0], box[3])
		diagonals.append((dx ** 2 + dy ** 2) ** .5)
	
	# set scale based on maximum guid size
	scale = max(diagonals)

	# circle radius based on scale to avoid object overlaps
	n = len(meshes)
	k = 1.1
	r = max(rmin, k * max(scale, n * scale / (2 * pi)))

	for i, mesh in enumerate(meshes):
		mesh_move_by(mesh, subtract_vectors(add_vectors(centre, circle_evaluate(2 * pi * float(i) / float(n), r)), mesh.centroid()))


def arrange_in_spiral(meshes, centre = None):

	if centre is None:
		centre = centroid_points([mesh.vertex_coordinates(vkey) for mesh in meshes for vkey in mesh.vertices()])

	# get object bounding box diagonal length
	diagonals = []
	for mesh in meshes:
		box = mesh_bounding_box(mesh)
		dx = distance_point_point(box[0], box[1])
		dy = distance_point_point(box[0], box[3])
		diagonals.append((dx ** 2 + dy ** 2) ** .5)
	
	# set scale based on maximum guid size
	scale = max(diagonals)

	# spiral parameters
	# default start angle
	a = 0
	# radius (2 * pi * b) larger than scale to avoid object overlaps
	k = 1.1
	b = k * scale / (2 * pi)


	# space meshes along spiral knowing L(t) = b / 2 * t ** 2
	t0 = pi * b
	ts = [t0]
	for i in range(len(meshes)):
		ts.append((2 * scale / b + ts[-1] ** 2) ** .5)

	for mesh, t in zip(meshes, ts):
		mesh_move_by(mesh, subtract_vectors(add_vectors(centre, archimedean_spiral_evaluate(t, a, b, 0)), mesh.centroid()))


def arrange_in_map(primary_topologies, secondary_topologies):

	# WIP
	
	diagonals = []
	for mesh in primary_topologies.keys():
		box = mesh_bounding_box(mesh)
		dx = distance_point_point(box[0], box[1])
		dy = distance_point_point(box[0], box[3])
		diagonals.append((dx ** 2 + dy ** 2) ** .5)
	scale = max(diagonals)

	n = len(primary_topologies.keys() + secondary_topologies.keys())
	rmin = n * scale
	arrange_in_circle(primary_topologies.keys(), rmin = rmin)
	centre = centroid_points([mesh.vertex_coordinates(vkey) for mesh in primary_topologies.keys() for vkey in mesh.vertices()])

	all_rules = [rule for rules in primary_topologies.values() for rule in rules]
	rules_without_duplicates = []
	for rule in all_rules:
		if rule not in rules_without_duplicates:
			rules_without_duplicates.append(rule)

	n = len(all_rules)
	points = [mesh.centroid() for mesh in primary_topologies.keys()]

	for mesh, rules in secondary_topologies.items():
		distances = [len(rules) + len(rules_0) - len(common_items(rules, rules_0)) for mesh_0, rules_0 in primary_topologies.items()]
		weights = [1.0 / float(d) if d != 0 else 10^(-n) for d in distances]
		mesh_move_by(mesh, subtract_vectors(weighted_centroid_points(points, weights), mesh.centroid()))


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	import compas
