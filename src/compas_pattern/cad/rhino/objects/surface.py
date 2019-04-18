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

	def mesh_uv_to_xyz(self, mesh, cls=None):
		"""Return the mesh from the inverse mapping of a UV mesh based on the UV parameterisation of the surface.

		Parameters
		----------
		mesh : Mesh
			A mesh.

		Returns
		-------
		Mesh, cls
			The inverse-mapped mesh.

		"""
		if cls is None:
			cls = type(mesh)

		vertices, faces = mesh.to_vertices_and_faces()
		vertices = {vkey: self.point_uv_to_xyz(uv0[:2]) for vkey, uv0 in vertices.items()}
		return cls.from_vertices_and_faces(vertices, faces)

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	import compas
