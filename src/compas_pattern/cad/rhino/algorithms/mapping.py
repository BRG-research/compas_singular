from compas_pattern.cad.rhino.objects.surface import RhinoSurface
from compas_pattern.cad.rhino.objects.curve import RhinoCurve

from compas.datastructures import Network
from compas.datastructures.network.operations import network_polylines

from compas.utilities import pairwise

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2018, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'

__all__ = [
	'surface_to_planar_boundaries',
	'mesh_to_surface',
	'line_to_surface',
	'polyline_to_surface'
]

def surface_to_planar_boundaries(srf_guid, precision):
	"""Map the boundaries of a Rhino NURBS surface to planar poylines dicretised within some precision using the surface UV parameterisation.

	Parameters
	----------
	srf_guid : guid
		A surface guid.
	precision : float
		The discretisation precision of the surface boundaries

	Returns
	-------
	list
		List of closed planar polyline boundaries. The first one is the outer boundary.

	"""

	# a boundary may be made of multiple boundary components and therefore checking for closeness and joining are necessary
	srf = RhinoSurface(srf_guid)

	mapped_borders = []

	for i in [1, 2]:
		mapped_border = []

		for border in srf.borders(type = i):
			border = RhinoCurve(border)
			points = [srf.map_uv0(pt) for pt in border.divide(int(border.length() / precision) + 1)]
			
			if border.is_closed():
				points.append(points[0])
			
			mapped_border.append(points)
			border.delete()
		mapped_borders.append(mapped_border)

	outer_boundaries, inner_boundaries = [network_polylines(Network.from_lines([(u, v) for border in mapped_borders[i] for u, v in pairwise(border)])) for i in [0, 1]]
	return outer_boundaries[: 1] + inner_boundaries

def mesh_to_surface(srf_guid, mesh):
	"""Map a mesh on a surface based on its UV parameterisation.

	Parameters
	----------
	srf_guid : guid
		A surface guid.
	mesh : Mesh
		A mesh

	Returns
	-------
	Mesh
		The mapped mesh.

	"""

	return RhinoSurface(srf_guid).remap_xyz_mesh(mesh)

def line_to_surface(srf_guid, line):
	"""Map a line on a surface based on its UV parameterisation.

	Parameters
	----------
	srf_guid : guid
		A surface guid.
	line : tuple
		A line

	Returns
	-------
	tuple
		The mapped line.

	"""
	
	return RhinoSurface(srf_guid).remap_xyz_line(line)

def polyline_to_surface(srf_guid, polyline):
	"""Map a polyline on a surface based on its UV parameterisation.

	Parameters
	----------
	srf_guid : guid
		A surface guid.
	polyline : tuple
		A polyline

	Returns
	-------
	tuple
		The mapped polyline.

	"""
	
	return RhinoSurface(srf_guid).remap_xyz_polyline(polyline)

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	import compas
