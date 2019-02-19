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

from compas.geometry import bounding_box
from compas.geometry import distance_point_point
from compas.geometry import subtract_vectors
from compas.geometry import centroid_points

from compas_rhino.modifiers import VertexModifier

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2017, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'


__all__ = [
	'draw_mesh',
	'draw_graph',
	'arrange_in_circle',
	'arrange_in_spiral'
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
	
	vertices, faces = mesh.to_vertices_and_faces()
	mesh = rhino.utilities.drawing.xdraw_mesh(vertices, faces, None, None)

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


def arrange_in_circle(guids, centre = None, radius = None):
	"""Arrange Rhino objects along a circle.

	Parameters
	----------
	guids : list
		The list of Rhino objects to arrange.
	centre : list
		The XYZ-coordinates of the centre of the circle. If None, the centroid of the Rhino objects.
	radius : float
		The radius of the circle. If None, a radius is computed based on the max bounding box of the Rhino objects.

	Returns
	-------
	guid_xyz : dict
		A dictionary of object guids pointing to new location centre.

	"""

	n = len(guids)

	guid_boxes = {guid: rs.BoundingBox(guid) for guid in guids}
	guid_xyz0 = {guid: centroid_points([point for point in guid_boxes[guid]]) for guid in guids}
	if centre is None:
		centre = centroid_points(guid_xyz0.values())


	if radius is None:
		scales = []
		for guid in guids:
			box = guid_boxes[guid]
			dx = distance_point_point(box[0], box[1])
			dy = distance_point_point(box[0], box[3])
			scales.append((dx**2 + dy**2)**.5)
		scale = max(scales)
		radius = n * scale / (2 * pi)

	guid_xyz = {}

	for i, guid in enumerate(guids):
		xyz0 = guid_xyz0[guid]
		xyz = [centre[0] + radius * cos(2 * pi * float(i) / n), centre[1] + radius * sin(2 * pi * float(i) / n), centre[2]]
		rs.MoveObject(guid, subtract_vectors(xyz, xyz0))
		guid_xyz[guid] = xyz

	return guid_xyz


def arrange_in_spiral(guids, centre = None):
	"""Arrange Rhino objects along a spiral.

	Parameters
	----------
	guids : list
		The list of Rhino objects to arrange.
	centre : list
		The XYZ-coordinates of the centre of the circle. If None, the centroid of the Rhino objects.

	Returns
	-------
	guid_xyz : dict
		A dictionary of object guids pointing to new location centre.

	"""

	n = len(guids)

	guid_boxes = {guid: rs.BoundingBox(guid) for guid in guids}
	guid_xyz0 = {guid: centroid_points([point for point in guid_boxes[guid]]) for guid in guids}
	if centre is None:
		centre = centroid_points(guid_xyz0.values())

	scales = []
	for guid in guids:
		box = guid_boxes[guid]
		dx = distance_point_point(box[0], box[1])
		dy = distance_point_point(box[0], box[3])
		scales.append((dx**2 + dy**2)**.5)
	D = max(scales)


	a = 0
	b = 1.1 * D / (2 * pi)

	t_start = 0
	t_end = (2 * n * D / b + t_start ** 2) ** .5
	ts = [float(t) / (n - 1) * (t_end - tstart) for t in range(n)]
	points_xy = [archimedean_spiral_evaluate(t, a, b) for t in ts]

	guid_xyz = {}

	for i, guid in enumerate(guids):
		xyz0 = guid_xyz0[guid]
		xyz = [centre[0] + radius * cos(2 * pi * float(i) / n), centre[1] + radius * sin(2 * pi * float(i) / n), centre[2]]
		rs.MoveObject(guid, subtract_vectors(xyz, xyz0))
		guid_xyz[guid] = xyz

	return guid_xyz


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	import compas
