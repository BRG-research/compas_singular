from compas_pattern.datastructures.mesh import Mesh
from compas_pattern.algorithms.densification import CoarseQuadMesh
from compas_pattern.datastructures.pseudo_quad_mesh import PseudoQuadMesh

from compas_pattern.algorithms.mapping import mapping
from compas_pattern.algorithms.triangulation import triangulation
from compas_pattern.algorithms.extraction import extraction
from compas_pattern.algorithms.decomposition import decomposition
from compas_pattern.algorithms.conforming import conforming
from compas_pattern.algorithms.remapping import remapping

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2018, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'

__all__ = [
	'medial_axis_singularity_mesh_from_surface',
]

def medial_axis_singularity_mesh_from_surface(surface, point_features = [], curve_features = [], discretisation = 1.):
	"""Generate a singularity mesh from a surface input with point and curve features.

	Parameters
	----------
	surface : guid
		A Rhino mesh.
	point_features : list
		A list of Rhino points.
	curve_features : list
		A list of Rhino curves.
	discretisation : float
		The spacing for discretisation of the input

	Returns
	-------
	singularity_mesh : mesh
		A (coarse) quad mesh.
	"""

	uv_boundaries, uv_holes, uv_curve_features, uv_point_features = mapping(discretisation, surface, curve_features, point_features)
	
	delaunay_mesh = triangulation(uv_boundaries, uv_holes, uv_curve_features, uv_point_features)
	medial_branches, boundary_branches = decomposition(delaunay_mesh)
	
	vertices, faces, edges_to_polyline = extraction(boundary_branches, medial_branches)
	patch_decomposition = CoarseQuadMesh.from_vertices_and_faces(vertices, faces)
	
	singularity_mesh = conforming(patch_decomposition, delaunay_mesh, medial_branches, boundary_branches, edges_to_polyline, uv_point_features, uv_curve_features)
	
	remapping(singularity_mesh, surface)

	return singularity_mesh 

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	import compas
