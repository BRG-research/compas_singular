import itertools as it
import random as rd

from compas_pattern.utilities.lists import remove_isomorphism_in_integer_list
from compas_pattern.datastructures.mesh_quad.grammar.add_strip import is_polyedge_valid_for_strip_addition

__all__ = [
	'enumerated_polyedge',
	'random_polyedge',
	'collect_polyedges'
]


def enumerated_polyedge(turtle, tail=None, path_length=5):

	for path in it.product((0, 1), repeat=int(path_length)):
		turtle.reset()
		turtle.start(tail=tail)
		turtle.toggle()
		turtle.interpret_path(path)
		yield turtle.polyedge


def random_polyedge(turtle, max_path_length=10):

	turtle.reset()
	# random start
	vertices = list(turtle.mesh.vertices())
	tail = vertices[rd.randint(0, len(vertices) - 1)]
	turtle.start(tail=tail)
	# random length
	n = rd.randint(1, max_path_length)
	# random path
	path = [rd.randint(0, 1) for i in range(n)]
	turtle.toggle()
	turtle.interpret_path(path)
	return turtle.polyedge


def collect_polyedges(turtle, total=100, part_random=.2, min_path_length=1, max_path_length=10):

	polyedges = set()
	tail = next(turtle.mesh.vertices())
	k = min_path_length
	enumerate_polyedges = enumerated_polyedge(turtle, tail=tail, path_length=k)
	
	count = total * 10
	while len(polyedges) < total * (1 - part_random) and count:
		count -= 1
		try:
			polyedge = next(enumerate_polyedges)
		except:
			k += 1
			enumerate_polyedges = enumerated_polyedge(turtle, tail=tail, path_length=k)
			polyedge = next(enumerate_polyedges)
		polyedge = tuple(remove_isomorphism_in_integer_list(polyedge))
		if polyedge not in polyedges and is_polyedge_valid_for_strip_addition(turtle.mesh, polyedge):
			polyedges.add(polyedge)

	random_polyedges = set()
	count = total * 10
	while len(random_polyedges) < total * part_random and count:
		count -= 1
		polyedge = random_polyedge(turtle, max_path_length=max_path_length)
		polyedge = tuple(remove_isomorphism_in_integer_list(polyedge))
		if polyedge not in polyedges and polyedge not in random_polyedges and is_polyedge_valid_for_strip_addition(turtle.mesh, polyedge):
			random_polyedges.add(polyedge)

	return polyedges, random_polyedges


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	import time
	import compas
	from compas_pattern.algorithms.exploration.turtle import Turtle
	from compas_pattern.datastructures.mesh_quad.mesh_quad import QuadMesh
	import itertools as it

	mesh = QuadMesh.from_obj(compas.get('faces.obj'))
	turtle = Turtle(mesh)

	polyedges = collect_polyedges(turtle, total=20, part_random=.2, max_path_length=10)
	print(polyedges)


