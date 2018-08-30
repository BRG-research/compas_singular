try:
	import rhinoscriptsyntax as rs

except ImportError:
	import platform
	if platform.python_implementation() == 'IronPython':
		raise

from compas.datastructures.mesh import Mesh
from compas.datastructures.network import Network

from compas_pattern.topology.polyline_extraction import dual_edge_polylines

from compas.geometry import bounding_box
from compas.geometry import distance_point_point
from compas.geometry import centroid_points
from compas.geometry import subtract_vectors
from compas.geometry import normalize_vector

from compas.topology import vertex_coloring
from collections import deque

import copy
import itertools

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2018, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'

__all__ = [
	'graph_disjointed_parts',
	'draw_graph',
	'complement_graph',
	'strip_overlap_graph_from_quad_mesh',
	'graph_colourability',
	'is_graph_two_colourable',
	'two_colourable_subgraphs',
]

def graph_disjointed_parts(graph):
	"""Group the graph vertices in sub-lists of disjointed parts.

	Parameters
	----------
	graph : Network
		A graph.

	Returns
	-------
	disjointed_parts : list
		The list of sublists of disjointed parts of graph vertices.

	"""

    vertices = list(graph.vertices())

    disjointed_parts = []

    count = len(vertices)
    while len(vertices) > 0 and count > 0:
        count -= 1
        part = [vertices.pop()]
        next_neighbours = [part[-1]]
        count_2  = count
        while len(next_neighbours) > 0 and count_2 > 0:
            count_2 -= 1
            for vkey in graph.vertex_neighbours(next_neighbours.pop()):
                if vkey not in part:
                    part.append(vkey)
                    vertices.remove(vkey)
                    if vkey not in next_neighbours:
                        next_neighbours.append(vkey)
        disjointed_parts.append(part)

    return disjointed_parts

def draw_graph(graph, group = None, key_to_colour = None):
	"""Draw a graph in Rhino as grouped points and lines with optional node colouring.

	Parameters
	----------
	graph : Network
		A graph.
	group : string
		Optional name of the group.
	key_to_colour : dict
		An optional dictonary point node keys no RGB colours.

	Returns
	-------
	group
		The name of the drawn group.

	"""

	box = bounding_box([graph.vertex_coordinates(vkey) for vkey in graph.vertices()])

	scale = distance_point_point(box[0], box[6])

	colours = [[255,0,0], [0,0,255], [0,255,0], [255,255,0], [0,255,255], [255,0,255],[0,0,0]]

	if key_to_colour is None:
		key_to_colour = {key: -1 for key in graph.vertices()}
	circles = []
	for key in graph.vertices():
		circle = rs.AddCircle(graph.vertex_coordinates(key), .01 * scale)
		circles.append(circle)
		colour = colours[key_to_colour[key]]
		rs.ObjectColor(circle, colour)

	lines = [rs.AddLine(graph.vertex_coordinates(u), graph.vertex_coordinates(v)) for u, v in graph.edges()]
	group = rs.AddGroup(group)
	rs.AddObjectsToGroup(circles + lines, group)

	return group

def complement_graph(graph):
	"""Generate the complement graph of a graph [1].

	Parameters
	----------
	graph : Network
		A graph.

	Returns
	-------
	complement_graph : graph
		The complement graph.

	References
	----------
	.. [1] Wolfram MathWorld. *Graph complement*.
		   Available at: http://mathworld.wolfram.com/GraphComplement.html.
	"""

	complement_graph = graph.copy()

	edges = list(graph.edges())

	for u, v in edges:
		complement_graph.delete_edge(u, v)

	for u in complement_graph.vertices():
		for v in complement_graph.vertices():
			if u < v and (u, v) not in edges and (v, u) not in edges:
				complement_graph.add_edge(u, v)

	return complement_graph

def strip_overlap_graph_from_quad_mesh(mesh):
	"""Create the strip overlap graph of a (coarse) quad mesh.
	A graph node is a quad face strip and a graph edge is a face crossed by two quad face strips.

	Parameters
	----------
	mesh : Mesh
		A quad mesh.

	Returns
	-------
	graph : graph, None
		The strip overlap graph.
		None if the mesh is not a quad mesh.

	"""

	# check if is quad mesh
	if not mesh.is_quadmesh():
		return None

	# compute strips as dual edge groups
	edge_groups, max_group = dual_edge_polylines(mesh)

	# collect groups info in dict as group: [index, list of faces]
	groups = {}
	index = 0
	for edge, group in edge_groups.items():
		u, v = edge
		if group not in groups:
			groups[group] = [index, []]
			index += 1
		fkey_1 = mesh.halfedge[u][v]
		if fkey_1 is not None and fkey_1 not in groups[group][1]:
			groups[group][1].append(fkey_1)
		fkey_2 = mesh.halfedge[v][u]
		if fkey_2 is not None and fkey_2 not in groups[group][1]:
			groups[group][1].append(fkey_2)

	n = len(groups.keys())

	# place nodes at the centroid of the strip
	vertices = [0] * n
	for group, attributes in groups.items():
		index, faces = attributes
		# possible improvement: add area weights
		centroids = [mesh.face_centroid(fkey) for fkey in faces]
		xyz = centroid_points(centroids)
		vertices[index] = xyz

	# connect one edge per face between its two strips (if self-crossing strip?)
	edges = []
	for fkey in mesh.faces():
		a, b, c, d = mesh.face_vertices(fkey)
		group_0 = edge_groups[(a, b)]
		group_1 = edge_groups[(b, c)]
		idx_0 = groups[group_0][0]
		idx_1 = groups[group_1][0]
		edges.append([idx_0, idx_1])

	# create graph
	graph = Network.from_vertices_and_edges(vertices, edges)

	# box = bounding_box([graph.vertex_coordinates(vkey) for vkey in graph.vertices()])
	# dx = distance_point_point(box[0], box[1])
	# dy = distance_point_point(box[0], box[3])
	# dz = distance_point_point(box[0], box[4])
	# scale = (dx ** 2 + dy ** 2 + dz ** 2) ** .5
	# area = dx * dy * dz
	# n = len(list(graph.vertices()))
	# factor = .5
	# criteria = factor * (area / n) ** (1/3)
	# # move superimposed vertices
	# k = graph.number_of_vertices()
	# while k  > 0:
	# 	k -= 1
	# 	vertex_map = {}
	# 	for vkey_1 in graph.vertices():
	# 		xyz_1 = graph.vertex_coordinates(vkey_1)
	# 		for vkey_2 in graph.vertices():
	# 			xyz_2 = graph.vertex_coordinates(vkey_2)
	# 			dist = distance_point_point(xyz_1, xyz_2)
	# 			if vkey_1 < vkey_2 and dist < criteria:
	# 				# possible improvement: find equilibrium towards centroid of neighbours
	# 				for eps, vkey in zip([+1, -1], [vkey_1, vkey_2]):
	# 					attr = graph.vertex[vkey]
	# 					attr['x'] += eps * .5 / scale * factor * dx
	# 					attr['y'] += eps * .5 / scale * factor * dy
	# 					attr['z'] += eps * .5 / scale * factor * dz

	return graph, groups

def graph_colourability(graph):
	"""Compute vertex colourability of a graph.

	Parameters
	----------
	graph : Network
		A graph.

	Returns
	-------
	int
		Colourability.

	"""

	return max(list(vertex_coloring(graph.adjacency).values())) + 1

def try_colour_graph_with_two_colours(graph):
	"""Try to colour a graph with two colours only.

	Parameters
	----------
	graph : Network
		A graph.

	Returns
	-------
	key_to_colour : dict, None
		A dictionary with vertex keys pointing to colours.
		None if the graph is not two-colourable.

	"""

	two_colourable = True

	# store colour per vertex key and vertex keys per rank of propagation
	key_to_colour = {}
	rank_to_keys = {}
	current_colour = 0
	current_rank = 0
	unvisited = [key for key in graph.vertices() if len(graph.vertex_neighbours(key)) > 0]
	# case of isolated vertices
	isolated_vertices = [key for key in graph.vertices() if len(graph.vertex_neighbours(key)) == 0]
	key_to_colour.update({key: 1 - current_colour for key in isolated_vertices})
	rank_to_keys[-1] = isolated_vertices

	# start from one of the vertices with the highest valency
	key_to_degree = {key: len(graph.vertex_neighbours(key)) for key in unvisited}
	univisted = sorted(unvisited, key=lambda key: key_to_degree[key])
	key_0 = unvisited.pop()
	key_to_colour[key_0] = current_colour
	rank_to_keys[current_rank] = [key_0]

	# loop until all vertices are visited
	count = len(unvisited)
	while len(unvisited) > 0 and count > 0:
		count -= 1
		# next rank and switch colour
		current_rank += 1
		current_colour = 1 - current_colour
		current_keys = []
		# collect valid neighbours of previous rank to form next rank
		for key in rank_to_keys[current_rank - 1]:
			for nbr in graph.vertex_neighbours(key):
				if nbr in unvisited and nbr not in current_keys:
					current_keys.append(nbr)
		#if no current keys (if graph has disconnected parts) start from a new one
		if len(current_keys) == 0:
			current_keys = [unvisited[-1]]
		# check that vertices of the next rank are not neighbours
		for key in current_keys:
			for key_2 in current_keys:
				if key < key_2:
					if key_2 in graph.vertex_neighbours(key):
								two_colourable = False
		# return None if not two colourable
		if not two_colourable:
			return None
		# store information before continuing
		else:
			for key in current_keys:
				key_to_colour[key] = current_colour
				unvisited.remove(key)
			rank_to_keys[current_rank] = current_keys

	return key_to_colour


def two_colourable_subgraphs(graph, k):

	vertices = list(graph.vertices())

	combinations = list(itertools.combinations(vertices, k))
	#print combinations
	two_col_combinations = []

	for combination in combinations:
		modified_graph = graph.copy()
		for vkey in combination:
			modified_graph.delete_vertex(vkey)
		key_to_colour = try_colour_graph_with_two_colours(modified_graph)
		if key_to_colour is not None:
			key_to_colour.update({vkey: 2 for vkey in combination})
			two_col_combinations.append(key_to_colour)

	return two_col_combinations

def binom_coeff(n, k):
	k = min(k, n - k)
	x = 1
	y = 1
	i = n - k + 1
	while i <= n:
		x = (x * i) // y
		y += 1
		i += 1
	return x

def is_subset_in_set(small_set, big_set):
	for i in small_set:
		is_in = False
		for j in big_set:
			if i == j:
				is_in = True
				break
		if not is_in:
			return False
	return True

def all_closest_two_colourable_subgraphs(graph, kmax = -1):

	vertices = list(graph.vertices())

	n = len(vertices)
	results = {}

	all_valid_two_col = []
	all_redundant_two_col = []
	all_invalid_two_col = []
	all_non_two_col = []

	if kmax < 0:
		kmax = n
	for k in range(1, kmax + 1):
		valid_two_col = []
		redundant_two_col = []
		invalid_two_col = []
		non_two_col = []

		#two_colourable_subgraphs(graph, k)
		combinations = list(itertools.combinations(vertices, k))
		two_col_combinations = []

		for combination in combinations:
			# is combination redundant
			redundant = False
			for two_col_combination in [item for sublist in all_valid_two_col for item in sublist]:
				if is_subset_in_set(two_col_combination, combination):
					redundant = True
					break
			if redundant:
				redundant_two_col.append(tuple(sorted(combination)))
				continue


			modified_graph = graph.copy()
			for vkey in combination:
				modified_graph.delete_vertex(vkey)
			key_to_colour = try_colour_graph_with_two_colours(modified_graph)
			if key_to_colour is not None:
				key_to_colour.update({vkey: 2 for vkey in combination})
				two_col_combinations.append(key_to_colour)



		for combination in two_col_combinations:
			isolated_non_third_node = False
			for vkey in graph.vertices():
				if combination[vkey] != 2:
					all_third = True
					for nbr in graph.vertex_neighbours(vkey):
						if combination[nbr] != 2:
							all_third = False
							break
					if all_third:
						isolated_non_third_node = True
						break
			if isolated_non_third_node:
				invalid_two_col.append(tuple(sorted([key for key, colour in combination.items() if colour == 2])))
			else:
				valid_two_col.append(tuple(sorted([key for key, colour in combination.items() if colour == 2])))

		all_combinations = list(itertools.combinations(vertices, k))
		for combination in all_combinations:
			combination = tuple(sorted(combination))
			if combination not in valid_two_col + redundant_two_col + invalid_two_col:
				non_two_col.append(combination)
				

		total = binom_coeff(n, k)
		nb_valid_two_col = len(valid_two_col)
		nb_redundant_two_col = len(redundant_two_col)
		nb_invalid_two_col = len(invalid_two_col)
		nb_non_two_col = len(non_two_col)
		print total, nb_valid_two_col, nb_redundant_two_col, nb_invalid_two_col, nb_non_two_col

		all_valid_two_col.append(valid_two_col)
		all_redundant_two_col.append(redundant_two_col)
		all_invalid_two_col.append(invalid_two_col)
		all_non_two_col.append(non_two_col)

		# termination criteria when no more directions are possible
		if total == nb_redundant_two_col:
			break

	return all_valid_two_col, all_redundant_two_col, all_invalid_two_col, all_non_two_col

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	import compas
	from compas.plotters import NetworkPlotter
	from compas.plotters import MeshPlotter

	from compas_pattern.topology.face_strip_operations import face_strip_collapse

	from compas.geometry import scale_points

	#print binom_coeff(44, 37)

	vertices_0 = [[2,0,0],
				[-1,0,0],
				[0,1,0],
				[1,0,0],
				[-2,0,0],
				[0,-1,0],
				[0,0,0],
				]
	edges_0 = [
			[6,3],
			[3,0],
			[0,5],
			[5,4],
			[4,1],
			[1,6],
			[6,2],
			]

	# graph = Network.from_vertices_and_edges(vertices_0, edges_0)
	# key_color = try_colour_graph_with_two_colours(graph)
	# if key_color is not None:
	# 	colors = ['#ff0000', '#0000ff', '#00ff00']
	# 	plotter = NetworkPlotter(graph, figsize=(10, 7))
	# 	plotter.draw_vertices(facecolor={key: colors[key_color[key]] for key in graph.vertices()})
	# 	plotter.draw_edges()
	# 	plotter.show()
	import time
	graph = Network()
	for i in range(7):
		graph.add_vertex(attr_dict = {'x': i, 'y':0, 'z':0})
	graph.add_edge(0,1)
	graph.add_edge(2,1)
	graph.add_edge(3,4)
	t0 = time.time()
	print graph_disjointed_parts(graph)
	t1 = time.time()
	print t1 - t0

