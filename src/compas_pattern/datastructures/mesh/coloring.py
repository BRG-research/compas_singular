from compas_pattern.datastructures.network import Network

from compas.topology import vertex_coloring

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2018, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'

__all__ = [
	'mesh_vertex_2_coloring',
	'mesh_vertex_n_coloring',
	'mesh_face_2_coloring',
	'mesh_face_n_coloring'
]


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


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	import compas
