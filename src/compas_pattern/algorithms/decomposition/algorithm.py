import compas

from compas_pattern.algorithms.decomposition.mapping import surface_discrete_mapping
from compas_pattern.algorithms.decomposition.triangulation import boundary_triangulation

from compas_pattern.algorithms.decomposition.skeletonisation import Skeleton
from compas_pattern.algorithms.decomposition.decomposition import Decomposition

from compas_pattern.cad.rhino.objects.surface import RhinoSurface

from compas.utilities import geometric_key

__all__ = [
	'surface_decomposition'
]


def surface_decomposition(srf_guid, precision, output_delaunay = False, output_skeleton = True, output_mesh = True, output_polysurface = False):
	"""Generate the topological skeleton/medial axis of a surface based on a Delaunay triangulation, after mapping and before remapping.

	Parameters
	----------
	srf_guid : guid
		A Rhino surface guid.
	precision : float
		A discretisation precision.
	output_delaunay : bool
		Output the Delaunay or not.
		Default is False.
	output_skeleton : bool
		Output the skeleton or not.
		Default is True.
	output_mesh : bool
		Output the coarse quad mesh or not.
		Default is True.
	output_polysurface : bool
		Output the polysurface or not.
		Default is False.

	Returns
	-------
	list
		The requested outputs.

	References
	----------
	.. [1] Harry Blum. 1967. *A transformation for extracting new descriptors of shape*.
		   Models for Perception of Speech and Visual Forms, pages 362--380.
		   Available at http://pageperso.lif.univ-mrs.fr/~edouard.thiel/rech/1967-blum.pdf.
	.. [2] Punam K. Saha, Gunilla Borgefors, and Gabriella Sanniti di Baja. 2016. *A survey on skeletonization algorithms and their applications*.
		   Pattern Recognition Letters, volume 76, pages 3--12.
		   Available at https://www.sciencedirect.com/science/article/abs/pii/S0167865515001233.
	.. [3] Oval et al. 2019. *Feature-based topology finding of patterns for shell structures*.
		   Accepted in Automation in Construction.

	"""

	# mapping NURBS surface to planar polyline borders
	outer_boundary, inner_boundaries, polyline_features, point_features = surface_discrete_mapping(srf_guid, precision)

	# Delaunay triangulation of the palnar polyline borders
	skeleton = boundary_triangulation(outer_boundary, inner_boundaries, polyline_features, point_features, cls = Decomposition)

	outputs = []

	# output remapped Delaunay mesh
	if output_delaunay:
		outputs.append(RhinoSurface(srf_guid).remap_xyz_mesh(skeleton))

	# output remapped topological skeleton/medial axis
	if output_skeleton:
		outputs.append([RhinoSurface(srf_guid).remap_xyz_polyline(polyline) for polyline in skeleton.branches()])

	# output decomposition coarse quad mesh
	if output_mesh:
		outputs.append(RhinoSurface(srf_guid).remap_xyz_mesh(skeleton.decomposition_mesh()))

	# output decomposition surface
	if output_polysurface:
		mesh = skeleton.decomposition_mesh()
		nurbs_curves = {(geometric_key(polyline[i]), geometric_key(polyline[-i -1])): rs.AddInterpCrvOnSrfUV(srf_guid, [pt[:2] for pt in polyline]) for polyline in skeleton.decomposition_polylines() for i in [0, -1]}
		outputs.append(rs.JoinSurfaces([rs.AddEdgeSrf([nurbs_curves[(geometric_key(mesh.vertex_coordinates(u)), geometric_key(mesh.vertex_coordinates(v)))] for u, v in mesh.face_halfedges(fkey)]) for fkey in mesh.faces()], delete_input = True))
		rs.DeleteObjects(list(nurbs_curves.values()))

	return outputs


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	import compas