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

	def __init__(self):
		super(RhinoCurve, self).__init__() 

	def divide(self, number_of_segments, over_space=False):
		points = []
		rs.EnableRedraw(False)
		if over_space:
			space = self.space(number_of_segments + 1)
			if space:
				points = [list(rs.EvaluateCurve(self.guid, param)) for param in space]
		else:
			points = rs.DivideCurve(self.guid, number_of_segments, create_points=False, return_points=True)
			points[:] = map(list, points)
		rs.EnableRedraw(True)
		return points

	def length(self):
		"""Return the length of the curve.

		Returns
		-------
		float
			The curve's length.
		"""
		return rs.CurveLength(self.guid)
		
	def tangents(self, points):
		tangents = []
		if rs.IsPolyCurve(self.guid):
			pass
		elif rs.IsCurve(self.guid):
			for point in points:
				param = rs.CurveClosestPoint(self.guid, point)
				vector = list(rs.CurveTangent(self.guid, param))
				tangents.append(vector)
		else:
			raise Exception('Object is not a curve.')
		return tangents
	

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	import compas
