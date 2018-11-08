from compas.datastructures.network import Network

from compas.utilities import pairwise
from compas.utilities import geometric_key

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2018, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'

__all__ = [
	'join_polylines',
]

def join_polylines(polylines, stops = []):
	"""Join polylines. The polylines stop at points connectng more than two lines and to optional additional points.

	Parameters
	----------
	polylines : list
		List of polylines as tuples of vertex coordinates.
	stops : list
		List of point coordinates for additional splits.

	Returns
	-------
	polylines: list
		The joined polylines. If the polyline is closed, the two extremities are the same.

	"""

	# explode in lines
	lines = [(u, v) for polyline in polylines for u, v in pairwise(polyline)]

	# geometric keys of split points
	stop_geom_keys = set([geometric_key(xyz) for xyz in stops])
	
	# create graph from polyline extremities
	network = Network.from_lines([(line[0], line[-1]) for line in lines])

	polylines = []
	edges_to_visit = set(network.edges())

	while len(edges_to_visit) > 0:

		# initiate from an edge
		polyline = list(edges_to_visit.pop())

		# loop around the cycle
		while polyline[0] != polyline[-1]:

			if len(network.vertex_neighbors(polyline[-1])) != 2 or geometric_key(network.vertex_coordinates(polyline[-1])) in stop_geom_keys:
				polyline = list(reversed(polyline))
				if len(network.vertex_neighbors(polyline[-1])) != 2 or geometric_key(network.vertex_coordinates(polyline[-1])) in stop_geom_keys:
					break

			polyline.append([nbr for nbr in network.vertex_neighbors(polyline[-1]) if nbr != polyline[-2]][0])

		for u, v in pairwise(polyline):
			if (u, v) in edges_to_visit:
				edges_to_visit.remove((u, v))
			elif (v, u) in edges_to_visit:
				edges_to_visit.remove((v, u))

		polylines.append(polyline)

	return [[network.vertex_coordinates(vkey) for vkey in polyline]for polyline in polylines]

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	import compas

	polylines=[[(0.,0.,0.), (1.,0.,0.), (1.,1.,0.), (1.,2.,0.), (0.,2.,0.), (0.,1.,0.), (0.,0.,0.)],[(0.,1.,0.), (1.,1.,0.)]]


	for i in join_polylines(polylines):
		print i
