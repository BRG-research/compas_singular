from math import pi
from math import cos
from math import sin
from math import tan

import compas

try:
	import rhinoscriptsyntax as rs

except ImportError:
	compas.raise_if_ironpython()

import compas_rhino as rhino

from compas.datastructures import mesh_weld

from compas.geometry import bounding_box
from compas.geometry import distance_point_point


__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2017, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'


__all__ = [
	'draw_mesh',
	'draw_graph'
]


def draw_mesh(mesh, group = True):
	"""Draw a graph in Rhino 5 as a mesh or grouped lines if at least face has 5 edges or more.

	Parameters
	----------
	mesh : Mesh
		A mesh.
	group : bool
		Group edges if polygonal mesh. Default is True.

	Returns
	-------
	mesh, edges : guid, list
		The guid of the mesh or the guids of the lines.

	"""

	if mesh.number_of_vertices() == 0:
		return None

	for fkey in mesh.faces():
		
		if len(mesh.face_vertices(fkey)) > 4:
			edges =  [rs.AddLine(mesh.vertex_coordinates(u), mesh.vertex_coordinates(v)) for u, v in mesh.edges() if mesh.vertex_coordinates(u) != mesh.vertex_coordinates(v)]
			if group:
				rs.AddObjectsToGroup(edges, rs.AddGroup())
			return edges
	
	vertices, faces = mesh.to_vertices_and_faces(keep_keys=False)
	mesh = rhino.utilities.drawing.draw_mesh(vertices, faces, None, None)
	
	return mesh


def draw_graph(graph, key_to_colour = {}):
	"""Draw a graph in Rhino as grouped points and lines with optional node colouring.

	Parameters
	----------
	graph : Network
		A graph.
	key_to_colour : dict
		An optional dictonary with vertex keys pointing to RGB colours.

	Returns
	-------
	group
		The name of the drawn group.

	"""

	# scale for the size of the vertices
	box = bounding_box([graph.vertex_coordinates(vkey) for vkey in graph.vertices()])
	scale = distance_point_point(box[0], box[6])

	# all black if not color specified
	key_to_colour.update({key: [0, 0, 0] for key in graph.vertices() if key not in key_to_colour})
	
	spheres = []
	for key in graph.vertices():
		sphere = rs.AddSphere(graph.vertex_coordinates(key), .005 * scale)
		rs.ObjectColor(sphere, key_to_colour[key])
		spheres.append(sphere)

	lines = [rs.AddLine(graph.vertex_coordinates(u), graph.vertex_coordinates(v)) for u, v in graph.edges()]
	
	# group
	group = rs.AddGroup()
	rs.AddObjectsToGroup(spheres + lines, group)

	return group


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	import compas
