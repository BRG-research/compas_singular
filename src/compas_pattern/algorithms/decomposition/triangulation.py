from compas.geometry import delaunay_from_points
#from compas.geometry.triangulation.triangulation_numpy import delaunay_from_points_numpy

from compas_pattern.datastructures.mesh.mesh import Mesh
from compas_pattern.algorithms.decomposition.decomposition import Decomposition

from compas.utilities import XFunc

from compas.rpc import Proxy

from compas.geometry import is_point_in_polygon_xy
from compas.geometry import length_vector
from compas.geometry import subtract_vectors
from compas.geometry import cross_vectors

from compas.datastructures import trimesh_face_circle

from compas.datastructures import mesh_unweld_edges

from compas.utilities import pairwise
from compas.utilities import geometric_key

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2018, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'

__all__ = [
	'delaunay_numpy_rpc',
	'boundary_triangulation'
]

def delaunay_numpy_rpc(vertices):
	"""RPC for Delaunay function from numpy.

	Parameters
	----------
	vertices : list
		List of vertex coordinates.

	Returns
	-------
	list
		List of face vertices.

	"""

	geometry = Proxy('compas.geometry.triangulation.triangulation_numpy')
	return geometry.delaunay_from_points_numpy(vertices)


def boundary_triangulation(outer_boundary, inner_boundaries, polyline_features = [], point_features = [], cls=None):
	"""Generate Delaunay triangulation between a planar outer boundary and planar inner boundaries. All vertices lie the boundaries.

	Parameters
	----------
	outer_boundary : list
		Planar outer boundary as list of vertex coordinates.
	inner_boundaries : list
		List of planar inner boundaries as lists of vertex coordinates.
	polyline_features : list
		List of planar polyline_features as lists of vertex coordinates.
	point_features : list
		List of planar point_features as lists of vertex coordinates.
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
	vertices = [pt for boundary in [outer_boundary] + inner_boundaries + polyline_features for pt in boundary] + point_features
	delaunay_mesh = Decomposition.from_vertices_and_faces(vertices, delaunay_numpy_rpc(vertices))
	
	# delete false faces with aligned vertices
	for fkey in list(delaunay_mesh.faces()):
		a, b, c = [delaunay_mesh.vertex_coordinates(vkey) for vkey in delaunay_mesh.face_vertices(fkey)]
		ab = subtract_vectors(b, a)
		ac = subtract_vectors(c, a)
		if length_vector(cross_vectors(ab, ac)) == 0:
			delaunay_mesh.delete_face(fkey)

	# delete faces outisde the borders
	for fkey in list(delaunay_mesh.faces()):
		centre = trimesh_face_circle(delaunay_mesh, fkey)[0]
		if not is_point_in_polygon_xy(centre, outer_boundary) or any([is_point_in_polygon_xy(centre, inner_boundary) for inner_boundary in inner_boundaries]):
			delaunay_mesh.delete_face(fkey)

	# topological cut along the feature polylines through unwelding
	vertex_map = {geometric_key(delaunay_mesh.vertex_coordinates(vkey)): vkey for vkey in delaunay_mesh.vertices()}
	edges = [edge for polyline in polyline_features for edge in pairwise([vertex_map[geometric_key(point)] for point in polyline])]
	mesh_unweld_edges(delaunay_mesh, edges)

	return delaunay_mesh


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	import compas
