import compas

try:
	import rhinoscriptsyntax as rs
	import scriptcontext as sc

	from Rhino.Geometry import Point3d

	find_object = sc.doc.Objects.Find

except ImportError:
	compas.raise_if_ironpython()

from compas.geometry import distance_point_point
from compas.geometry import angle_vectors

from compas_rhino.geometry.curve import RhinoCurve
from compas_rhino.geometry.surface import RhinoSurface


__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2018, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'

__all__ = [
	'RhinoSurface'
]

class RhinoSurface(RhinoSurface):

	def __init__(self, guid):
		super(RhinoSurface, self).__init__(guid) 

	# --------------------------------------------------------------------------
	# projection
	# --------------------------------------------------------------------------
	
	def closest_point(self, xyz):
		"""Return the XYZ coordinates of the closest point on the surface from input XYZ-coordinates.
	
		Parameters
		----------
		xyz : list
			XYZ coordinates.

		Returns
		-------
		list
			The XYZ coordinates of the closest point on the surface.

		"""

		return rs.EvaluateSurface(self.guid, *rs.SurfaceClosestPoint(self.guid, xyz))

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

		borders = self.borders(type = 0)
		proj_dist = {tuple(proj_xyz): distance_point_point(xyz, proj_xyz) for proj_xyz in [RhinoCurve(border).closest_point(xyz) for border in borders]}
		rs.DeleteObjects(borders)
		return min(proj_dist, key = proj_dist.get)

	# --------------------------------------------------------------------------
	# mapping XYZ <--> UV
	# --------------------------------------------------------------------------

	def map_uv0(self, xyz):
		"""Return the UV(0) point from the mapping of a XYZ point based on the UV parameterisation of the surface.

		Parameters
		----------
		xyz : list
			XYZ coordinates.

		Returns
		-------
		list
			The UV(0) coordinates of the mapped point.

		"""

		return rs.SurfaceClosestPoint(self.guid, xyz) + (0.,)

	def remap_xyz_point(self, uv):
		"""Return the XYZ point from the re-mapping of a UV point based on the UV parameterisation of the surface.

		Parameters
		----------
		uv : list
			UV(0) coordinates.

		Returns
		-------
		list
			The XYZ coordinates of the re-mapped point.

		"""

		return tuple(rs.EvaluateSurface(self.guid, *uv))

	def remap_xyz_line(self, line):
		"""Return the XYZ points from the re-mapping of a UV line based on the UV parameterisation of the surface.

		Parameters
		----------
		uv : list
			List of UV(0) coordinates.

		Returns
		-------
		list
			The list of XYZ coordinates of the re-mapped line.

		"""

		return (self.remap_xyz_point(line[0][:2]), self.remap_xyz_point(line[1][:2]))

	def remap_xyz_polyline(self, polyline):
		"""Return the XYZ points from the re-mapping of a UV polyline based on the UV parameterisation of the surface.

		Parameters
		----------
		uv : list
			List of UV(0) coordinates.

		Returns
		-------
		list
			The list of XYZ coordinates of the re-mapped polyline.

		"""

		return [self.remap_xyz_point(vertex[:2]) for vertex in polyline]

	def remap_xyz_mesh(self, mesh, cls=None):
		"""Return the mesh from the re-mapping of a UV mesh based on the UV parameterisation of the surface.

		Parameters
		----------
		mesh : Mesh
			A mesh.

		Returns
		-------
		Mesh, cls
			The re-mapped mesh.

		"""

		if cls is None:
			cls = type(mesh)

		vertices, faces = mesh.to_vertices_and_faces()
		vertices = [self.remap_xyz_point(uv0[:2]) for uv0 in vertices]
		return cls.from_vertices_and_faces(vertices, faces)

	def kinks(self, threshold=1e-3):
		"""Return the XYZ coordinates of kinks, i.e. tangency discontinuities, along the surface's boundaries.

		Returns
		-------
		list
			The list of XYZ coordinates of surface boundary kinks.

		"""

		kinks = []
		borders = self.borders(type = 0)
		
		for border in borders:
			border = RhinoCurve(border)
			extremities = map(lambda x: rs.EvaluateCurve(border.guid, rs.CurveParameter(border.guid, x)), [0., 1.])
		
			if rs.IsCurveClosed(border.guid):
				start_tgt, end_tgt = border.tangents(extremities)
				if angle_vectors(start_tgt[1], end_tgt[1]) > threshold:
					kinks += extremities 
		
			else:
				kinks += extremities

		return list(set(kinks))

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	import compas
