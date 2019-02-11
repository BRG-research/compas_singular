from compas_pattern.datastructures.network import Network

from compas.topology import vertex_coloring

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2018, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'

__all__ = [
	'is_network_two_colorable',
	'mesh_vertex_2_coloring',
	'mesh_vertex_n_coloring',
	'mesh_face_2_coloring',
	'mesh_face_n_coloring',
	'mesh_strip_2_coloring',
	'mesh_strip_n_coloring',
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
			if key_to_color[nbr] != -1 and key_to_color[key] == key_to_color[nbr]:
				return None
			# if not colored, color the opposite color of the neighbour and add to sources for propagation
			elif key_to_color[nbr] == -1:
				key_to_color[nbr] = 1 - key_to_color[key]
				sources.append(nbr)

	# if completed, return True
	return key_to_color

def mesh_vertex_2_coloring(mesh):
	"""Try to color the vertices of a mesh with two colors only without adjacent vertices with the same color.

	Parameters
	----------
	mesh : Mesh
		A mesh.

	Returns
	-------
	dict, None
		A dictionary with vertex keys pointing to colors, if two-colorable.
		None if not two-colorable.

	"""

	network = Network.from_vertices_and_edges({vkey: mesh.vertex_coordinates(vkey) for vkey in mesh.vertices()}, list(mesh.edges()))
	return is_network_two_colorable(network)

def mesh_vertex_n_coloring(mesh):
	"""Color the vertices of a mesh with a minimum number of colors without adjacent vertices with the same color.

	Parameters
	----------
	mesh : Mesh
		A mesh.

	Returns
	-------
	dict
		A dictionary with vertex keys pointing to colors.
		
	"""

	return vertex_coloring(mesh.adjacency)

def mesh_face_2_coloring(mesh):
	"""Try to color the faces of a mesh with two colors only without adjacent faces with the same color.

	Parameters
	----------
	mesh : Mesh
		A mesh.

	Returns
	-------
	dict, None
		A dictionary with face keys pointing to colors, if two-colorable.
		None if not two-colorable.

	"""

	vertices = {fkey: mesh.face_centroid(fkey) for fkey in mesh.faces()}
	edges = [(mesh.halfedge[u][v], mesh.halfedge[v][u]) for u, v in mesh.edges() if not mesh.is_edge_boundary(u, v)]
	network = Network.from_vertices_and_edges(vertices, edges)

	return is_network_two_colorable(network)

def mesh_face_n_coloring(mesh):
	"""Color the faces of a mesh with a minimum number of colors without adjacent faces with the same color.

	Parameters
	----------
	mesh : Mesh
		A mesh.

	Returns
	-------
	dict
		A dictionary with face keys pointing to colors.
		
	"""

	vertices = {fkey: mesh.face_centroid(fkey) for fkey in mesh.faces()}
	edges = [(mesh.halfedge[u][v], mesh.halfedge[v][u]) for u, v in mesh.edges() if not mesh.is_edge_on_boundary(u, v)]
	network = Network.from_vertices_and_edges(vertices, edges)

	return vertex_coloring(network.adjacency)

def mesh_strip_2_coloring(quad_mesh):
	"""Try to color the strips of a quad mesh with two colors only without overlapping strips with the same color.

	Parameters
	----------
	quad_mesh : QuadMesh
		A quad mesh.

	Returns
	-------
	dict, None
		A dictionary with strip keys pointing to colors, if two-colorable.
		None if not two-colorable.

	"""

	quad_mesh.collect_strips()
	return is_network_two_colorable(quad_mesh.strip_connectivity())

def mesh_strip_n_coloring(quad_mesh):
	"""Color the strips of a quad mesh with a minimum number of colors without overlapping strips with the same color.

	Parameters
	----------
	quad_mesh : QuadMesh
		A quad mesh.

	Returns
	-------
	dict
		A dictionary with strip keys pointing to colors.
		
	"""

	quad_mesh.collect_strips()
	return vertex_coloring(quad_mesh.strip_connectivity().adjacency)

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	import compas
