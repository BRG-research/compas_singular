from compas_pattern.datastructures.network import Network

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2018, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'

__all__ = [
	'is_network_two_colourable'
]


def is_network_two_colourable(network):
	"""Try to colour a network with two colours only.

	Parameters
	----------
	network : Network
		A network.

	Returns
	-------
	key_to_colour : dict, None
		A dictionary with vertex keys pointing to colours, if two-colourable.
		None if not two-colourable.

	References
	----------
	.. [1] GeeksforGeeks. *Bipartite graph*.
		   Available at: https://www.geeksforgeeks.org/bipartite-graph/.

	"""

	# store colour status of network vertices (-1 means no colour)
	key_to_colour = {vkey: -1 for vkey in network.vertices()}
	
	# start from any vertex and colour it
	key_0 = network.get_any_vertex()
	sources = [key_0]
	key_to_colour[key_0] = 0

	count = network.number_of_vertices()

	# propagate until all vertices are coloured or two adjacent vertices have the same colour
	while count > 0 and sources:
		count -= 1
		key = sources.pop()

		for nbr in network.vertex_neighbors(key):
			# if already colored and with the same colour as the neighbour, return False
			if key_to_colour[nbr] != -1 and key_to_colour[key] == key_to_colour[nbr]:
				return None
			# if not coloured, colour the opposite colour of the neighbour and add to sources for propagation
			elif key_to_colour[nbr] == -1:
				key_to_colour[nbr] = 1 - key_to_colour[key]
				sources.append(nbr)

	# if completed, return True
	return key_to_colour

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	import compas
