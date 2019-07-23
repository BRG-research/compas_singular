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


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	import compas
