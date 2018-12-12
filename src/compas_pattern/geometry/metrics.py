from math import degrees
from math import acos
from math import pi

from compas.datastructures.mesh import Mesh

from compas.geometry import length_vector
from compas.geometry import dot_vectors
from compas.geometry import cross_vectors
from compas.geometry import subtract_vectors
from compas.geometry import distance_line_line
from compas.geometry import distance_point_point
from compas.geometry import angle_points
from compas.geometry import normalize_vector

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2018, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'

__all__ = [
	'minimum',
	'maximum',
	'mean',
	'standard_deviation',
	'edge_lengths',
	'face_areas',
	'face_aspect_ratios',
	'face_skewnesses',
	'face_curvatures',
	'vertex_curvatures',
	'polyedge_curvatures',
	'polyline_curvatures',
]

def minimum(list):
	"""Minimum in a list.

	Parameters
	----------
	list : list
		List of values.

	Returns
	-------
	minimum_value: float
		The minimum value.

	Raises
	------
	-

	"""

	return min(list)

def maximum(list):
	"""Maximum in a list.

	Parameters
	----------
	list : list
		List of values.

	Returns
	-------
	maximum_value: float
		The maximum value.

	Raises
	------
	-

	"""

	return max(list)

def mean(list):
	"""Mean of a list.

	Parameters
	----------
	list : list
		List of values.

	Returns
	-------
	mean_value: float
		The mean value.

	Raises
	------
	-

	"""

	return sum(list) / float(len(list))

def standard_deviation(list):
	"""Standard deviation of a list.

	Parameters
	----------
	list : list
		List of values.

	Returns
	-------
	standard_deviation_value: float
		The standard deviation value.

	Raises
	------
	-

	"""

	m = mean(list)

	return (sum([(i - m) ** 2 for i in list]) / float(len(list))) ** .5


def edge_lengths(mesh):
	"""Lengths of the mesh edges as dict edge: edge length.

	Parameters
	----------
	mesh : Mesh
		A mesh.

	Returns
	-------
	edge_length_dict: dict
		Dictionary of lengths per edge {edge: edge length}.

	Raises
	------
	-

	"""

	return {(u, v): mesh.edge_length(u, v) for u, v  in mesh.edges()}

def face_areas(mesh):
	"""Areas of the mesh faces as dict face: face area.

	Parameters
	----------
	mesh : Mesh
		A mesh.

	Returns
	-------
	face_area_dict: dict
		Dictionary of areas per face {face: face area}.

	Raises
	------
	-

	"""

	return {fkey: mesh.face_area(fkey) for fkey in mesh.faces()}

def face_aspect_ratios(mesh):
	"""Aspect ratios of the mesh faces as dict face: face aspect ratio.
	Aspect ratio of a face = longuest edge / shortest edge.

	https://en.wikipedia.org/wiki/Types_of_mesh

	Parameters
	----------
	mesh : Mesh
		A mesh.

	Returns
	-------
	face_aspect_ratio_dict: dict
		Dictionary of aspect ratios per face {face: face adpect ratio}.

	Raises
	------
	-

	"""

	face_aspect_ratio_dict = {}
	for fkey in mesh.faces():
		face_edge_lengths = [mesh.edge_length(u, v) for u, v in mesh.face_halfedges(fkey)]
		face_aspect_ratio_dict[fkey] = maximum(face_edge_lengths) / minimum(face_edge_lengths)

	return face_aspect_ratio_dict


def face_skewnesses(mesh):
	"""Skewnesses of the mesh faces as dict face: face skewness.

	https://en.wikipedia.org/wiki/Types_of_mesh

	Parameters
	----------
	mesh : Mesh
		A mesh.

	Returns
	-------
	face_aspect_ratio_dict: dict
		Dictionary of aspect ratios per face {face: face aspect ratio}.

	Raises
	------
	-

	"""

	face_skewness_dict = {}
	for fkey in mesh.faces():
		equi_angle = 180 * (1 - 2 / float(len(mesh.face_vertices(fkey))))
		angles = []
		face_vertices = mesh.face_vertices(fkey)
		for i in range(len(face_vertices)):
			u = mesh.vertex_coordinates(face_vertices[i - 2])
			v = mesh.vertex_coordinates(face_vertices[i - 1])
			w = mesh.vertex_coordinates(face_vertices[i])
			uv = subtract_vectors(v, u)
			vw = subtract_vectors(w, v)
			dot = dot_vectors(uv, vw) / (length_vector(uv) * length_vector(vw))
			cross = dot_vectors(mesh.face_normal(fkey), cross_vectors(uv, vw))
			sign = 1
			if sign < 0:
				sign = -1
			angle = sign  * degrees(acos(dot))
			angles.append(angle)
		max_angle = maximum(angles)
		min_angle = minimum(angles)
		
		face_skewness_dict[fkey] = max((max_angle - equi_angle) / (180 - equi_angle), (equi_angle - min_angle) / equi_angle)

	return face_skewness_dict

def face_curvatures(mesh):
	"""Curvatures of the mesh quad faces as dict face: face curvature.
	Curvature of a face = distance between diagonals / mean diagonal length.

	Parameters
	----------
	mesh : Mesh
		A mesh.

	Returns
	-------
	face_curvature_dict: dict
		Dictionary of curvatures per face {face: face curvature}. None if vertex is not a quad.

	Raises
	------
	-

	"""

	face_curvature_dict = {}
	for fkey in mesh.faces():
		if len(mesh.face_vertices(fkey)) == 4:
			u, v, w, x = [mesh.vertex_coordinates(vkey) for vkey in mesh.face_vertices(fkey)]
			face_curvature_dict[fkey] = distance_line_line((u, w), (v, x)) / (distance_point_point(u, w) + distance_point_point(v, x)) * 2
		elif len(mesh.face_vertices(fkey)) == 3:
			face_curvature_dict[fkey] = 0
		else:
			face_curvature_dict[fkey] = None

	return face_curvature_dict

def vertex_curvatures(mesh):
	"""Curvatures of the non-boundary mesh vertices as dict vertex: vertex curvature.
	Curvature of a vertex = 2 * pi - sum angles between adajcent edges.

	Parameters
	----------
	mesh : Mesh
		A mesh.

	Returns
	-------
	vertex_curvature_dict: dict
		Dictionary of curvatures per vertex {vertex: vertex curvature}. None if vertex is on the boundary.

	Raises
	------
	-

	"""

	vertex_curvature_dict = {}
	for vkey in mesh.vertices():
		if not mesh.is_vertex_on_boundary(vkey):
			sum_angles = 0
			neighbours = mesh.vertex_neighbours(vkey)
			for i in range(len(neighbours)):
				nbr_1 = neighbours[i - 1]
				nbr_2 = neighbours[i]
				sum_angles += angle_points(mesh.vertex_coordinates(vkey), mesh.vertex_coordinates(nbr_1), mesh.vertex_coordinates(nbr_2))
			vertex_curvature_dict[vkey] = 2 * pi - sum_angles
		else:
			vertex_curvature_dict[vkey] = None

	return vertex_curvature_dict

def polyedge_curvatures(mesh, polyedges):
	"""Curvatures of the mesh vertices along polyedges as dict (vertices): (curvatures).


	Parameters
	----------
	mesh: Mesh
		A mesh
	polyedges: list
		List of polyedges as sequences of vertices.

	Returns
	-------
	polyedge_curvature_dict: dict
		Dictionary of curvatures per vertex per polyedge {(vertices): (curvature)}.

	Raises
	------
	-

	"""

	polyedge_curvature_dict = {}
	for polyedge in polyedges:
		curvatures = []
		for i in range(len(polyedge)):
			if i == 0 or i == len(polyedge) - 1:
				curvatures.append(0)
			else:
				a, b, c = polyedge[i - 1], polyedge[i], polyedge[i + 1]
				ab = subtract_vectors(mesh.vertex_coordinates(b), mesh.vertex_coordinates(a))
				bc = subtract_vectors(mesh.vertex_coordinates(c), mesh.vertex_coordinates(b))
				ac = subtract_vectors(mesh.vertex_coordinates(c), mesh.vertex_coordinates(a))
				if cross_vectors(ab, bc) == 0:
					curvatures.append(0)
				else:
					radius = length_vector(ac) / (2 * length_vector(cross_vectors(ab, bc))) * (length_vector(ab) * length_vector(bc))
					curvatures.append(1 / radius)
		polyedge_curvature_dict[tuple(polyedge)] = curvatures

	return polyedge_curvature_dict

def polyline_curvatures(polyline):
	"""Curvatures of the polyline.


	Parameters
	----------
	polyline: list
		A list of points

	Returns
	-------
	polyline_curvatures_list: list
		List of curvatures per vertex per polyline []curvature].

	Raises
	------
	-

	"""

	polyline_curvatures_list = []
	for i in range(len(polyline)):
		if i == 0 or i == len(polyline) - 1:
			polyline_curvatures_list.append(0)
		else:
			a, b, c = polyline[i - 1], polyline[i], polyline[i + 1]
			ab = subtract_vectors(b, a)
			bc = subtract_vectors(c, b)
			ac = subtract_vectors(c, a)
			if cross_vectors(ab, bc) == 0:
				polyline_curvatures_list.append(0)
			else:
				radius = length_vector(ac) / (2 * length_vector(cross_vectors(ab, bc))) * (length_vector(ab) * length_vector(bc))
				polyline_curvatures_list.append(1 / radius)

	return polyline_curvatures_list

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	import compas

	vertices = [[0,0,0],[1,0,0],[1,1,5],[0,2,0],[2,1.5,0],[1,1,0]]
	faces = [[0,1,2,3],[1,4,2],[2,4,5,3]]

	mesh = Mesh.from_vertices_and_faces(vertices, faces)

	print face_skewnesses(mesh)
	#print standard_deviation(face_skewnesses(mesh).values())
