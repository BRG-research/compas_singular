from compas.geometry import distance_point_point
from compas.geometry import add_vectors
from compas.geometry import subtract_vectors
from compas.geometry import scale_vector

from compas.utilities import pairwise

from compas.geometry import Line
from compas.geometry import Polyline


__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2018, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'

__all__ = [
	'weighted_centroid_points',
	'line_point',
	'polyline_point'
]

def weighted_centroid_points(points, weights):
	"""Compute the weighted centroid of a set of points.

	Parameters
	----------
	points : list
		A list of point coordinates.
	weights : list
		A list of weight floats.

	Returns
	-------
	list
		The coordinates of the weighted centroid.
	"""
 
	return scale_vector( 1. / sum(weights), add_vectors([scale_vector(weight, point) for weight, point in zip(weights, points)]))


def line_point(line, t = .5):
	"""Point on a lyline at a normalised parameter.

	Parameters
	----------
	line: tuple
		The XYZ coordinates of the extremities of the line.
	t: float 
		The normalised parameter of the point on the polyline between 0 and 1.

	Returns
	-------
	xyz: list, None
		The point coordinates.
		None if the parameter is not in [0,1]
	"""

	if t < 0 or t > 1:
		return None

	u, v = line
	uv = subtract_vectors(v, u)
	return add_vectors(u, scale_vector(uv, t))

def polyline_point(polyline, t = .5, snap = False):
	"""Point on a polyline at a normalised parameter. If asked, the found position is snapped to the closest polyline node.

	Parameters
	----------
	polyline: list
		The XYZ coordinates of the nodes of the polyline. The polyline can be closed.
	t: float 
		The normalised parameter of the point on the polyline between 0 and 1.
	snap_to_point: bool
		If true, the closest node on the polyline is returned, if false, a point on a line.

	Returns
	-------
	xyz: list, None
		The point coordinates.
		None if the parameter is not in [0,1]

	Raises
	------
	-

	"""

	polyline = Polyline(polyline)

	if t < 0 or t > 1:
		return None

	points = polyline.points
	polyline_length = polyline.length

	x = 0
	i = 0

	while x <= t:

		line = Line(points[i], points[i + 1])
		line_length = line.length

		dx = line_length / polyline_length

		if x + dx >= t:

			if snap:
				if t - x < x + dx - t:
					return line.start
				else:
					return line.end

			return line.start + line.direction * ((t - x) * polyline_length / line_length * line.length)
		
		x += dx
		i += 1

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	import compas

	polyline = [[0.,0.,0.], [1.,0.,0.], [2.,0.,0.], [10.,0.,0.], [12.,0.,0.], [20.,0.,0.], [21.,0.,0.], [21.,4.,0.]]

	print polyline_point(polyline, t = .66, snap = True)
