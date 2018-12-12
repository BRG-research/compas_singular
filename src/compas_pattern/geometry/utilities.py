from compas.geometry import distance_point_point
from compas.geometry import add_vectors
from compas.geometry import subtract_vectors
from compas.geometry import scale_vector


__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2018, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'

__all__ = [
	'line_point',
	'polyline_point'
]

def line_point(line, t = .5):
	"""Point on a lyline at a normalised parameter.

	Parameters
	----------
	polyline: list
	    The XYZ coordinates of the extremities of the line.
	t: float 
	    The normalised parameter of the point on the polyline between 0 and 1.

	Returns
	-------
	xyz: list, None
		The point coordinates.
		None if the parameter is not in [0,1]

	Raises
	------
	-

	"""

	u, v = line
	uv = subtract_vectors(v, u)
	return add_vectors(u, scale_vector(uv, t))

def polyline_point(polyline, t = .5, snap_to_point = False):
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

	if t < 0 or t > 1:
		return None

	length = sum([distance_point_point(polyline[i], polyline[i + 1]) for i in range(len(polyline) - 1)])
	target_length = t * length

	current_length = 0
	for i in range(len(polyline) - 1):
		current_point = polyline[i]
		next_point = polyline[i + 1]
		next_length = current_length + distance_point_point(current_point, next_point)
		if target_length >= current_length and target_length <= next_length:
			rest_length = target_length - current_length
			rest_t = rest_length / distance_point_point(current_point, next_point)
			xyz = add_vectors(current_point, scale_vector(subtract_vectors(next_point, current_point), rest_t))
			if snap_to_point:
				if distance_point_point(xyz, current_point) < distance_point_point(xyz, next_point):
					return current_point
				else:
					return next_point
			else:
				return xyz
		else:
			current_length = next_length

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas

    polyline = [[0.,0.,0.], [1.,0.,0.], [2.,0.,0.], [10.,0.,0.], [12.,0.,0.], [20.,0.,0.], [21.,0.,0.], [21.,5.,0.]]

    print polyline_point(polyline, t = .5, snap_to_point = False)
