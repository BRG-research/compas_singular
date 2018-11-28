import compas

try:
	import rhinoscriptsyntax as rs
	import scriptcontext as sc

	from Rhino.Geometry import Point3d

	find_object = sc.doc.Objects.Find

except ImportError:
	compas.raise_if_ironpython()

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
	# mapping XYZ <--> UV
	# --------------------------------------------------------------------------
	
	def project_point(self, xyz):
		return rs.EvaluateSurface(self.guid, *rs.SurfaceClosestPoint(self.guid, xyz))
	
	def map_uv0(self, xyz):
		return rs.SurfaceClosestPoint(self.guid, xyz) + (0.,)

	def remap_xyz_point(self, uv):
		return tuple(rs.EvaluateSurface(self.guid, *uv))

	def remap_xyz_line(self, line):
		return (self.remap_xyz_point(line[0][:2]), self.remap_xyz_point(line[1][:2]))

	def remap_xyz_polyline(self, polyline):
		return [self.remap_xyz_point(vertex[:2]) for vertex in polyline]

	def remap_xyz_mesh(self, mesh, cls=None):

		if cls is None:
			cls = type(mesh)

		vertices, faces = mesh.to_vertices_and_faces()
		vertices = [self.remap_xyz_point(uv0[:2]) for uv0 in vertices]
		return cls.from_vertices_and_faces(vertices, faces)

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	import compas
