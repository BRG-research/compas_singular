import compas

try:
	import rhinoscriptsyntax as rs

except ImportError:
	compas.raise_if_ironpython()

from compas.geometry import distance_point_point
from compas.geometry import angle_vectors

from compas_pattern.cad.rhino.objects.curve import RhinoCurve
from compas_rhino.geometry.surface import RhinoSurface


__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2018, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'

__all__ = [
	'RhinoSurface'
]


### TO BE PUSHED TO COMPAS ###


class RhinoSurface(RhinoSurface):

	def __init__(self):
		super(RhinoSurface, self).__init__()


	def borders(self, type=0):
		"""Duplicate the borders of the surface.

		Parameters
		----------
		type : {0, 1, 2}
			The type of border.

			* 0: All borders
			* 1: The exterior borders.
			* 2: The interior borders.

		Returns
		-------
		list
			The GUIDs of the extracted border curves.

		"""
		border = rs.DuplicateSurfaceBorder(self.guid, type=type)
		curves = rs.ExplodeCurves(border, delete_input=True)
		return curves

	def kinks(self, threshold=1e-3):
		"""Return the XYZ coordinates of kinks, i.e. tangency discontinuities, along the surface's boundaries.

		Returns
		-------
		list
			The list of XYZ coordinates of surface boundary kinks.

		"""
		kinks = []
		borders = self.borders(type=0)

		for border in borders:
			border = RhinoCurve.from_guid(border)
			extremities = map(lambda x: rs.EvaluateCurve(border.guid, rs.CurveParameter(border.guid, x)), [0., 1.])

			if border.is_closed():
				start_tgt, end_tgt = border.tangents(extremities)
				if angle_vectors(start_tgt, end_tgt) > threshold:
					kinks += extremities

			else:
				kinks += extremities

		rs.DeleteObjects(borders)
		return list(set(kinks))

	def closest_point_on_boundaries(self, xyz):
		"""Return the XYZ coordinates of the closest point on the boundaries of the surface from input XYZ-coordinates.

		Parameters
		----------
		xyz : list
			XYZ coordinates.

		Returns
		-------
		list
			The XYZ coordinates of the closest point on the boundaries of the surface.

		"""
		borders = self.borders(type=0)
		proj_dist = {tuple(proj_xyz): distance_point_point(xyz, proj_xyz) for proj_xyz in [RhinoCurve(border).closest_point(xyz) for border in borders]}
		delete_objects(borders)
		return min(proj_dist, key=proj_dist.get)

	def closest_points_on_boundaries(self, points):
		return [self.closest_point_on_boundaries(point) for point in points]

	# --------------------------------------------------------------------------
	# mapping
	# --------------------------------------------------------------------------

	def point_xyz_to_uv(self, xyz):
		"""Return the UV point from the mapping of a XYZ point based on the UV parameterisation of the surface.

		Parameters
		----------
		xyz : list
			(x, y, z) coordinates.

		Returns
		-------
		list
			The (u, v) coordinates of the mapped point.

		"""
		return rs.SurfaceClosestPoint(self.guid, xyz)

	def point_uv_to_xyz(self, uv):
		"""Return the XYZ point from the inverse mapping of a UV point based on the UV parameterisation of the surface.

		Parameters
		----------
		uv : list
			(u, v) coordinates.

		Returns
		-------
		list
			The (x, y, z) coordinates of the inverse-mapped point.

		"""
		u, v = uv
		return tuple(rs.EvaluateSurface(self.guid, *uv))

	def line_uv_to_xyz(self, line):
		"""Return the XYZ points from the inverse mapping of a UV line based on the UV parameterisation of the surface.

		Parameters
		----------
		uv : list
			List of (u, v) coordinates.

		Returns
		-------
		list
			The list of XYZ coordinates of the inverse-mapped line.

		"""
		return (self.point_uv_to_xyz(line[0]), self.point_uv_to_xyz(line[1]))

	def polyline_uv_to_xyz(self, polyline):
		"""Return the XYZ points from the inverse mapping of a UV polyline based on the UV parameterisation of the surface.

		Parameters
		----------
		uv : list
			List of (u, v) coordinates.

		Returns
		-------
		list
			The list of (x, y, z) coordinates of the inverse-mapped polyline.

		"""
		return [self.point_uv_to_xyz(vertex) for vertex in polyline]

	def mesh_uv_to_xyz(self, mesh):
		"""Return the mesh from the inverse mapping of a UV mesh based on the UV parameterisation of the surface.
		The third coordinate of the mesh vertices is discarded.

		Parameters
		----------
		mesh : Mesh
			A mesh.

		Returns
		-------
		mesh : Mesh
			The mesh once mapped back to the surface.

		"""

		for vkey in mesh.vertices():
			x, y, z = self.point_uv_to_xyz(mesh.vertex_coordinates(vkey)[:2])
			mesh.vertex[vkey]['x'] = x
			mesh.vertex[vkey]['y'] = y
			mesh.vertex[vkey]['z'] = z
		return mesh
	

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	import compas
