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
	'graph_colourability',
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
			for vkey in graph.vertex_neighbors(next_neighbours.pop()):
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

