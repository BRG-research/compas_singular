from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

from compas.datastructures import Network
from compas.datastructures import network_polylines

from compas_pattern.rhino import RhinoSurface
from compas_pattern.rhino import RhinoCurve

from compas.utilities import pairwise

try:
	import rhinoscriptsyntax as rs

except ImportError:
	import compas
	compas.raise_if_ironpython()


__all__ = [
	'DecompositionMap'
]

class DecompositionMap(RhinoSurface):

	curve_features = None
	point_features = None

	mapped_outer_boundary = None
	mapped_inner_boundaries = None
	mapped_polyline_features = None
	mapped_point_features = None

	def __init__(self):
		super(RhinoSurface, self).__init__()

def surface_discrete_mapping(self, discretisation, minimum_discretisation = 5, crv_guids = [], pt_guids = []):
	"""Map the boundaries of a Rhino NURBS surface to planar poylines dicretised within some discretisation using the surface UV parameterisation.
	Curve and point feautres on the surface can be included.

	Parameters
	----------
	srf_guid : guid
		A surface guid.
	crv_guids : list
		List of guids of curves on the surface.
	pt_guids : list
		List of guids of points on the surface.
	discretisation : float
		The discretisation of the surface boundaries.
	minimum_discretisation : int
		The minimum discretisation of the surface boundaries.

	Returns
	-------
	tuple
		Tuple of the mapped objects: outer boundary, inner boundaries, polyline_features, point_features.

	"""

	self.curve_features = [RhinoCurve.from_guid(crv_guid) for crv_guid in crv_guids]
	self.point_features = [rs.PointCoordinates(pt_guid) for pt_guid in pt_guids]

	# a boundary may be made of multiple boundary components and therefore checking for closeness and joining are necessary
	mapped_borders = []

	for i in [1, 2]:
		mapped_border = []

		for border in self.borders(type = i):
			border = RhinoCurve.from_guid(border)
			points = [list(self.point_xyz_to_uv(pt)) + [0.0] for pt in border.divide(max(int(border.length() / discretisation) + 1, minimum_discretisation))]
			
			if border.is_closed():
				points.append(points[0])
			
			mapped_border.append(points)
			rs.DeleteObject(border.guid)
		mapped_borders.append(mapped_border)

	outer_boundaries, inner_boundaries = [network_polylines(Network.from_lines([(u, v) for border in mapped_borders[i] for u, v in pairwise(border)])) for i in [0, 1]]
	
	# mapping of the curve features on the surface
	mapped_curves = []

	for curve in self.curve_features:

		points = [list(self.point_xyz_to_uv(pt)) + [0.0] for pt in curve.divide(max(int(curve.length() / discretisation) + 1, minimum_discretisation))]
		
		if curve.is_closed():
			points.append(points[0])
		
		mapped_curves.append(points)

	polyline_features = network_polylines(Network.from_lines([(u, v) for curve in mapped_curves for u, v in pairwise(curve)]))

	# mapping of the point features onthe surface
	point_features = [list(self.point_xyz_to_uv(point)) + [0.0] for point in self.point_features]

	self.mapped_outer_boundary = outer_boundaries[0]
	self.mapped_inner_boundaries = inner_boundaries
	self.mapped_polyline_features = polyline_features
	self.mapped_point_features = point_features


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	import compas
