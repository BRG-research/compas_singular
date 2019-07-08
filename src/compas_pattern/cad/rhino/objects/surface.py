import compas

try:
	import rhinoscriptsyntax as rs

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


### TO BE PUSHED TO COMPAS ###


class RhinoSurface(RhinoSurface):

	def __init__(self, guid):
		super(RhinoSurface, self).__init__(guid) 

	def mesh_uv_to_xyz(self, mesh):
		"""Remap a mesh with UV coordinates to a surface based on its UV-parameterisation.
		The third coordinate of the mesh vertices is discarded.

		Parameters
		----------
		mesh : Mesh
			A mesh.
		"""

		for vkey in mesh.vertices():
			x, y, z = self.point_uv_to_xyz(mesh.vertex_coordinates(vkey)[:2])
			mesh.vertex[vkey]['x'] = x
			mesh.vertex[vkey]['y'] = y
			mesh.vertex[vkey]['z'] = z


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	import compas
