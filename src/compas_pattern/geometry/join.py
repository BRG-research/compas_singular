from compas.datastructures.network import Network

from compas.utilities import pairwise

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2018, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'

__all__ = [
	'join_lines_to_polylines',
]

def join_lines_to_polylines(lines):
	"""Join polylines from lines. The polylines stop at points connectng more than two lines.

	Parameters
	----------
	lines : list
		List of lines as tuples of their extremity coordinates.

	Returns
	-------
	polylines: list
		The polylines. If the polyline is closed, the two extremities are the same.

	"""
	# create graph from polyline extremities
	network = Network.from_lines([(line[0], line[-1]) for line in lines])

	polylines = []
	edges_to_visit = set(network.edges())

	while len(edges_to_visit) > 0:

		# initiate from an edge
		polyline = list(edges_to_visit.pop())

		# loop around the cycle
		while polyline[0] != polyline[-1]:

			if len(network.vertex_neighbors(polyline[-1])) != 2:
				polyline = list(reversed(polyline))
				if len(network.vertex_neighbors(polyline[-1])) != 2:
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
