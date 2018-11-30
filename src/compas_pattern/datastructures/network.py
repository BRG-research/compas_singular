from compas.datastructures.network import Network

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2017, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'

__all__ = [

]

class Network(Network):

	def __init__(self):
		super(Network, self).__init__()

	def vertex_valency(self, vkey):
		"""Valency of a vertex, i.e. number of adjacent vertices.

		Parameters
		----------
		vkey : hashable
			The vertex key.

		Returns
		-------
		int
			The valency.
		"""

		return len(self.vertex_neighbors(vkey))

	@classmethod
	def from_vertices_and_edges(cls, vertices, edges):
		"""Construct a network from vertices and edges.

		Parameters
		----------
		vertices : list of list of float or dictionary of keys pointing to list of floats
			A list of vertex coordinates or a dictionary of keys pointing to vertex coordinates to specify keys.
		edges : list of tuple of int

		Returns
		-------
		Network
			A network object.

		Examples
		--------
		.. code-block:: python

			pass

		"""
		network = cls()
		if type(vertices) == list:
			for x, y, z in vertices:
				network.add_vertex(x=x, y=y, z=z)
		if type(vertices) == dict:
			for key, xyz in vertices.items():
				network.add_vertex(key = key, attr_dict = {i: j for i, j in zip(['x', 'y', 'z'], xyz)})
		for u, v in edges:
			network.add_edge(u, v)
		return network

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	import compas
