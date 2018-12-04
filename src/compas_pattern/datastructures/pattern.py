import compas

try:
	import rhinoscriptsyntax as rs

except ImportError:
	compas.raise_if_ironpython()

from compas_pattern.datastructures.mesh import Mesh
from compas_pattern.datastructures.mesh_quad import QuadMesh
from compas_pattern.datastructures.mesh_quad_coarse import CoarseQuadMesh
from compas_pattern.datastructures.mesh_quad_pseudo import PseudoQuadMesh
from compas_pattern.datastructures.mesh_quad_pseudo_coarse import CoarsePseudoQuadMesh

from compas_pattern.cad.rhino.utilities import draw_mesh

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2018, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'

__all__ = [

]

class Pattern:
	"""Definition of a pattern.

	"""

	def __init__(self, settings = None):
		if settings is not None:
			self.settings = settings
		else:
			self.settings = {}
		self.coarse_quad_mesh = CoarseQuadMesh()
		self.mesh = Mesh()

	# --------------------------------------------------------------------------
	# constructors
	# --------------------------------------------------------------------------

	@classmethod
	def from_quad_mesh(cls, quad_mesh):

		pattern = cls()

		pattern.coarse_quad_mesh = CoarseQuadMesh.from_quad_mesh(quad_mesh)
		pattern.mesh = pattern.coarse_quad_mesh.quadmesh

		return pattern

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	import compas
