from compas_pattern.datastructures.network.network import Network

from compas.topology import vertex_coloring

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2018, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'

__all__ = [
	'is_network_two_colorable'
]


def is_network_two_colorable(network):
	"""Try to color a network with two colors only.

	Parameters
	----------
	network : Network
		A network.

	Returns
	-------
	key_to_color : dict, None
		A dictionary with vertex keys pointing to colors, if two-colorable.
		None if not two-colorable.

	References
	----------
	.. [1] GeeksforGeeks. *Bipartite graph*.
		   Available at: https://www.geeksforgeeks.org/bipartite-graph/.

	"""

	# store color status of network vertices (-1 means no color)
	key_to_color = {vkey: -1 for vkey in network.vertices()}
	
	# start from any vertex and color it
	key_0 = network.get_any_vertex()
	sources = [key_0]
	key_to_color[key_0] = 0

	count = network.number_of_vertices()

	# propagate until all vertices are colored or two adjacent vertices have the same color
	while count > 0 and sources:
		count -= 1
		key = sources.pop()

		for nbr in network.vertex_neighbors(key):
			# if already colored and with the same color as the neighbour, return False
			# FALSE!!!!!!!!!!!!!!!
			if key_to_color[nbr] != -1 and key_to_color[key] == key_to_color[nbr]:
				return None
			# if not colored, color the opposite color of the neighbour and add to sources for propagation
			elif key_to_color[nbr] == -1:
				key_to_color[nbr] = 1 - key_to_color[key]
				sources.append(nbr)

	# if completed, return True
	return key_to_color


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	import compas
