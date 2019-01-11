from compas.topology import delaunay_from_points
from compas.topology.triangulation import delaunay_from_points_numpy
from compas.utilities import XFunc

from compas.geometry import is_point_in_polygon_xy
from compas.geometry import length_vector
from compas.geometry import subtract_vectors
from compas.geometry import cross_vectors

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2018, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'

__all__ = [
	'delaunay_from_points_numpy_xfunc',
	'delaunay',
	'planar_boundaries_to_delaunay'
]

def delaunay_from_points_numpy_xfunc(vertices):
	"""Xfunc for Delaunay function from numpy.

	Parameters
	----------
	vertices : list
		List of vertex coordinates.

	Returns
	-------
	list
		List of face vertices.

	"""

	return delaunay_from_points_numpy(vertices)

def delaunay(vertices, src = 'compas', cls=None):
	"""Group the Delaunay functions from compas, numpy.

	Parameters
	----------
	vertices : list
		List of vertex coordinates.
	src : string
		Specify Delaunay algorithm to use: compas or numpy.
	cls
		Mesh class.

	Returns
	-------
	cls
		The Delaunay mesh.

	"""

	if cls is None:
		cls = Mesh

	if src == 'compas':
		faces = delaunay_from_points(vertices)
	
	elif src == 'numpy':
		faces = XFunc('compas_pattern.topology.triangulation.delaunay_from_points_numpy_xfunc')(vertices)
	
	else:
		return None

	return cls.from_vertices_and_faces(vertices, faces)

def planar_boundaries_to_delaunay(outer_boundary, inner_boundaries, src = 'numpy', cls=None):
	"""Generate Delaunay triangulation between a planar outer boundary and planar inner boundaries. All vertices lie the boundaries.

	Parameters
	----------
	outer_boundary : list
		Planar outer boundary as list of vertex coordinates.
	inner_boundaries : list
		List of planar inner boundaries as lists of vertex coordinates.
	src : string
		Specify Delaunay algorithm to use: compas or numpy.
	cls
		Mesh class.

	Returns
	-------
	delaunay_mesh : cls
		The Delaunay mesh.

	"""

	if cls is None:
		cls = Mesh

	# generate planar Delaunay triangulation
	vertices = [pt for boundary in [outer_boundary] + inner_boundaries for pt in boundary]
	delaunay_mesh = delaunay(vertices, src = src, cls = cls)
	
	# delete false faces with aligned vertices
	for fkey in list(delaunay_mesh.faces()):
		a, b, c = [delaunay_mesh.vertex_coordinates(vkey) for vkey in delaunay_mesh.face_vertices(fkey)]
		ab = subtract_vectors(b, a)
		ac = subtract_vectors(c, a)
		if length_vector(cross_vectors(ab, ac)) == 0:
			delaunay_mesh.delete_face(fkey)

	# delete faces outisde the borders
	for fkey in list(delaunay_mesh.faces()):
		centre = delaunay_mesh.face_circle(fkey)[0]
		if not is_point_in_polygon_xy(centre, outer_boundary) or any([is_point_in_polygon_xy(centre, inner_boundary) for inner_boundary in inner_boundaries]):
			delaunay_mesh.delete_face(fkey)

	return delaunay_mesh

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	import compas