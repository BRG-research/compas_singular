import compas

try:
	import rhinoscriptsyntax as rs
	import scriptcontext as sc

	from Rhino.Geometry import Point3d

	find_object = sc.doc.Objects.Find

except ImportError:
	compas.raise_if_ironpython()

from compas_rhino.geometry.curve import RhinoCurve


__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2018, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'

__all__ = [
	'RhinoCurve'
]

class RhinoCurve(RhinoCurve):

	def __init__(self, guid):
		super(RhinoCurve, self).__init__(guid) 

	def length(self):
		return rs.CurveLength(self.guid)

	def delete(self):
		rs.DeleteObject(self.guid)

	def is_closed(self):
		return rs.IsCurveClosed(self.guid)

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	import compas
