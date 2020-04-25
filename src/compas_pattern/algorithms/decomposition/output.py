from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

from compas_pattern.rhino.objects.surface import RhinoSurface

from compas.utilities import geometric_key

from compas_pattern.algorithms.decomposition.decomposition import SkeletonDecomposition

__all__ = [
	'DecompositionRemap'
]

class DecompositionRemap(SkeletonDecomposition):
	srf_guid = None

	def __init__(self, srf_guid):
		self.srf_guid = srf_guid
		super(SkeletonDecomposition, self).__init__()

	def decomposition_delaunay(self):
		"""Output the remapped Delaunay triangulation.

		Returns
		-------
		Decomposition
			The remapped Delaunay triangulation.

		"""

		return RhinoSurface.from_guid(self.srf_guid).mesh_uv_to_xyz(self)


	def decomposition_skeleton(self):
		"""Output the remapped skeleton branches.

		Returns
		-------
		list
			The remapped skeleton branches.

		"""

		return [RhinoSurface.from_guid(self.srf_guid).polyline_uv_to_xyz([xyz[:2] for xyz in polyline]) for polyline in self.branches()]


	def decomposition_curves(self):
		"""Output the remapped decomposition curves.

		Returns
		-------
		list
			The remapped decomposition curves.

		"""

		return [RhinoSurface.from_guid(self.srf_guid).polyline_uv_to_xyz([xyz[:2] for xyz in polyline]) for polyline in self.decomposition_polylines()]


	def decomposition_mesh(self, point_features):
		"""Output the remapped decomposition mesh.

		Parameters
		----------
		point_features : list
			The point features for pole locations.

		Returns
		-------
		list
			The remapped decomposition mesh.

		"""

		mesh = self.decomposition_mesh(point_features)
		RhinoSurface.from_guid(self.srf_guid).mesh_uv_to_xyz(mesh)
		return mesh


	def decomposition_polysurface(self, point_features):
		"""Output the remapped decomposition polysurface.

		Parameters
		----------
		point_features : list
			The point features for pole locations.

		Returns
		-------
		A Rhino surface guid.
			The remapped decomposition polysurface.

		"""

		mesh = self.decomposition_mesh()
		nurbs_curves = {(geometric_key(polyline[i]), geometric_key(polyline[-i -1])): rs.AddInterpCrvOnSrfUV(self.srf_guid, [pt[:2] for pt in polyline]) for polyline in self.decomposition_polylines() for i in [0, -1]}
		polysurface = rs.JoinSurfaces([rs.AddEdgeSrf([nurbs_curves[(geometric_key(mesh.vertex_coordinates(u)), geometric_key(mesh.vertex_coordinates(v)))] for u, v in mesh.face_halfedges(fkey)]) for fkey in mesh.faces()], delete_input=True)
		rs.DeleteObjects(list(nurbs_curves.values()))
		return polysurface


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	import compas
	from compas_pattern.datastructures.mesh.mesh import Mesh
	#from compas_pattern.algorithms.decomposition.decomposition import Decomposition

	outer_boundary = [[1.0, 0.125, 0.0], [1.0, 0.25, 0.0], [1.0, 0.375, 0.0], [1.0, 0.5, 0.0], [1.0, 0.625, 0.0], [1.0, 0.75, 0.0], [1.0, 0.875, 0.0], [1.0, 1.0, 0.0], [0.875, 1.0, 0.0], [0.75, 1.0, 0.0], [0.625, 1.0, 0.0], [0.5, 1.0, 0.0], [0.375, 1.0, 0.0], [0.25, 1.0, 0.0], [0.125, 1.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.875, 0.0], [0.0, 0.75, 0.0], [0.0, 0.625, 0.0], [0.0, 0.5, 0.0], [0.0, 0.375, 0.0], [0.0, 0.25, 0.0], [0.0, 0.125, 0.0], [0.0, 0.0, 0.0], [0.125, 0.0, 0.0], [0.25, 0.0, 0.0], [0.375, 0.0, 0.0], [0.5, 0.0, 0.0], [0.625, 0.0, 0.0], [0.75, 0.0, 0.0], [0.875, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 0.125, 0.0]]
	point_features = [[0.29999999999999999, 0.59999999999999998, 0.0]]

	#decomposition = boundary_triangulation(outer_boundary, inner_boundaries=[], polyline_features=[], point_features=point_features, cls=Decomposition)
