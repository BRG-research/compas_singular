import compas

try:
	import rhinoscriptsyntax as rs

except ImportError:
	compas.raise_if_ironpython()

from compas_rhino.geometry.curve import RhinoCurve


__all__ = [
	'RhinoCurve'
]


### TO BE PUSHED TO COMPAS ###


class RhinoCurve(RhinoCurve):

	def __init__(self, guid):
		super(RhinoCurve, self).__init__(guid) 


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	import compas
