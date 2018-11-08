import compas

try:
	import rhinoscriptsyntax as rs
	import scriptcontext as sc

	from Rhino.Geometry import Point3d

	find_object = sc.doc.Objects.Find

except ImportError:
	compas.raise_if_ironpython()

from compas_pattern.geometry.skeleton import Skeleton
from compas_pattern.geometry.skeleton_mesh import SkeletonMesh

from compas_pattern.cad.rhino.algorithms.mapping import surface_to_planar_boundaries
from compas_pattern.topology.triangulation import planar_boundaries_to_delaunay
from compas_pattern.cad.rhino.algorithms.mapping import mesh_to_surface
from compas_pattern.cad.rhino.algorithms.mapping import line_to_surface
from compas_pattern.cad.rhino.algorithms.mapping import polyline_to_surface

from compas.utilities import geometric_key

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2018, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'

__all__ = [
	'surface_skeleton',
	'surface_skeleton_decomposition_mesh',
	'surface_skeleton_decomposition_nurbs'
]

def surface_skeleton(srf_guid, precision):
	"""Generate the topological skeleton/medial axis of a surface based on a Delaunay triangulation, after mapping and before remapping.

	Parameters
	----------
	srf_guid : guid
		A Rhino surface guid.
	precision : float
		A discretisation precision.

	Returns
	-------
	list
		The list of the polylines of the skeleton branches as list of vertices.

	References
	----------
	.. [1] Harry Blum. 1967. *A transformation for extracting new descriptors of shape*.
		   Models for Perception of Speech and Visual Forms, pages 362--380.
		   Available at http://pageperso.lif.univ-mrs.fr/~edouard.thiel/rech/1967-blum.pdf.
	.. [2] Punam K. Saha, Gunilla Borgefors, and Gabriella Sanniti di Baja. 2016. *A survey on skeletonization algorithms and their applications*.
		   Pattern Recognition Letters, volume 76, pages 3--12.
		   Available at https://www.sciencedirect.com/science/article/abs/pii/S0167865515001233.
	"""

	# mapping NURBS surface to planar polyline borders
	boundaries = surface_to_planar_boundaries(srf_guid, precision)

	# Delaunay triangulation of the palnar polyline borders
	skeleton = planar_boundaries_to_delaunay(boundaries[0], boundaries[1 :], cls = Skeleton)

	# generation and remapping of the topological skeleton from the Delaunay mesh of/on the surface
	return [polyline_to_surface(srf_guid, polyline) for polyline in skeleton.branches()]
	
def surface_skeleton_decomposition_mesh(srf_guid, precision):
	"""Generate a coarse quad mesh of a surface using its topological skeleton an its singularities.

	Parameters
	----------
	srf_guid : guid
		A Rhino surface guid.
	precision : float
		A discretisation precision.

	Returns
	-------
	CoarseQuadMesh
		The coarse quad mesh.

	References
	----------
	.. [1] Oval et al. 2018. *Topology finding of patterns for shell structures*.
		   Submitted for publication in Automation in Construction.

	"""

	# mapping NURBS surface to planar polyline borders
	boundaries = surface_to_planar_boundaries(srf_guid, precision)

	# Delaunay triangulation of the palnar polyline borders
	skeleton = planar_boundaries_to_delaunay(boundaries[0], boundaries[1 :], cls = SkeletonMesh)

	# generation and remapping of the skeleton-based mesh from the Delaunay mesh of/on the surface
	return mesh_to_surface(srf_guid, skeleton.decomposition_mesh()), [polyline_to_surface(srf_guid, polyline) for polyline in skeleton.polylines]

def surface_skeleton_decomposition_nurbs(srf_guid, precision):
	"""Generate an untrimmed polysurface on a surface using its topological skeleton an its singularities.

	Parameters
	----------
	srf_guid : guid
		A Rhino surface guid.
	precision : float
		A discretisation precision.

	Returns
	-------
	CoarseQuadMesh
		The coarse quad mesh.

	References
	----------
	.. [1] Oval et al. 2018. *Topology finding of patterns for shell structures*.
		   Submitted for publication in Automation in Construction.

	"""

	# mapping NURBS surface to planar polyline borders
	boundaries = surface_to_planar_boundaries(srf_guid, precision)

	# Delaunay triangulation of the palnar polyline borders
	skeleton = planar_boundaries_to_delaunay(boundaries[0], boundaries[1 :], cls = SkeletonMesh)

	# generation and remapping of the skeleton-based NURBS polysurface from the Delaunay mesh of/on the surface
	mesh = skeleton.decomposition_mesh()
	nurbs_curves = {(geometric_key(polyline[i]), geometric_key(polyline[-i -1])): rs.AddInterpCrvOnSrfUV(srf_guid, [pt[:2] for pt in polyline]) for polyline in skeleton.decomposition_polylines() for i in [0, -1]}
	polysurface = rs.JoinSurfaces([rs.AddEdgeSrf([nurbs_curves[(geometric_key(mesh.vertex_coordinates(u)), geometric_key(mesh.vertex_coordinates(v)))] for u, v in mesh.face_halfedges(fkey)]) for fkey in mesh.faces()], delete_input = True)
	rs.DeleteObjects(list(nurbs_curves.values()))

	return polysurface

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	import compas