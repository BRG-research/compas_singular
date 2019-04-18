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

	"""

	# store color status of network vertices (-1 means no color)
	key_to_color = {vkey: -1 for vkey in network.vertices()}
	
	# start from any vertex, color it and propagate to neighbors
	key_0 = network.get_any_vertex()
	sources = [key_0]

	count = network.number_of_vertices()

	# propagate until all vertices are colored or two adjacent vertices have the same color
	while count > 0 and sources:
		count -= 1
		key = sources.pop()
		nbr_colors = tuple([key_to_color[nbr] for nbr in network.vertex_neighbors(key)])

		# if two colors already exist in the neighbors, the network is not two-colourable
		if 0 in nbr_colors and 1 in nbr_colors:
			return None
		# otherwise, color with an available color
		else:
			if 0 not in nbr_colors:
				key_to_color[key] = 0
			elif 1 not in nbr_colors:
				key_to_color[key] = 1
			# add uncolored neighbors to sources
			sources += [nbr for nbr in network.vertex_neighbors(key) if key_to_color[nbr] == -1 and nbr not in sources]

	return key_to_color


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	import time
	import compas
	from compas_pattern.datastructures.network.network import Network
	from compas_pattern.datastructures.mesh_quad_coarse.mesh_quad_coarse import CoarseQuadMesh
	from compas.plotters import NetworkPlotter

	# vertices = [
	# 	[0, 0, 0],
	# 	[1, 0, 0],
	# 	[2, 0, 0],
	# 	[2, 1, 0],
	# 	[1, 1, 0],
	# 	[0, 1, 0],
	# ]

	# edges = [
	# 	(0, 1),
	# 	(1, 2),
	# 	(2, 3),
	# 	(3, 4),
	# 	(4, 5),
	# 	(5, 0),
	# 	(0, 3),
	# 	(2, 5)
	# ]

	# network = Network.from_vertices_and_edges(vertices, edges)
	# print is_network_two_colorable(network)

	vertices = [
		[0, 0, 0],
		[1, 0, 0],
		[1, 1, 0],
		[0, 1, 0]
	]

	faces = [
		[0, 1, 2, 3]
	]



	mesh = CoarseQuadMesh.from_vertices_and_faces(vertices, faces)
	mesh.init_strip_density()
	mesh.set_strips_density(60)
	mesh.densification()
	mesh = mesh.quad_mesh
	vertices = [mesh.vertex_coordinates(vkey) for vkey in mesh.vertices()]
	edges = list(mesh.edges())
	network = Network.from_vertices_and_edges(vertices, edges)
	#print network.vertex_neighbors(0), network.vertex_neighbors(8), network.vertex_neighbors(17), network.vertex_neighbors(33)
	t0 = time.time()
	is_network_two_colorable(network)
	t1 = time.time()
	print t1 - t0, network.number_of_vertices(), network.number_of_vertices() / (t1 - t0)
	plotter = NetworkPlotter(network)
	plotter.draw_vertices(text='key', radius=.01)
	plotter.draw_edges()
	#plotter.show()

