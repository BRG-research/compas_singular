from compas.datastructures.mesh import Mesh

from compas.utilities import geometric_key

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2018, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'

__all__ = [

]

class QuadMesh(Mesh):

	def __init__(self):
		super(QuadMesh, self).__init__()
		self.default_edge_attributes.update({
			'strip': None
			})

	def not_none_edges(self):
		"""Returns the edges oriented inwards.

		Parameters
		----------

		Returns
		-------
		(w, x) : tuple
			The opposite edge.

		"""

		return [(u, v) if v in self.halfedge[u] and self.halfedge[u][v] is not None else (v, u) for u, v in self.edges()]


	def face_edge_opposite(self, u, v):
		"""Returns the opposite edge in the quad face.

		Parameters
		----------
		u : int
			The identifier of the edge start.
		v : int
			The identifier of the edge end.

		Returns
		-------
		(w, x) : tuple
			The opposite edge.

		"""

		fkey = self.halfedge[u][v]
		w = self.face_vertex_descendant(fkey, v)
		x = self.face_vertex_descendant(fkey, w)

		return (w, x)

	# --------------------------------------------------------------------------
	# strip topology
	# --------------------------------------------------------------------------

	def edge_strip(self, u0, v0):
		"""Returns all the edges in the strip of the input edge.

		Parameters
		----------
		u : int
			The identifier of the edge start.
		v : int
			The identifier of the edge end.

		Returns
		-------
		strip : list
			The list of the edges in strip.

		"""

		edges = [(u0, v0)]

		count = self.number_of_edges()
		while count > 0:
			count -= 1

			u, v = edges[-1]
			w, x = self.face_edge_opposite(u, v)
			
			if (x, w) == edges[0]:
				break
			
			edges.append((x, w))

			if w not in self.halfedge[x] or self.halfedge[x][w] is None:	
				edges = [(v, u) for u, v in reversed(edges)]
				u, v = edges[-1]
				if v not in self.halfedge[u] or self.halfedge[u][v] is None:
					break

		return edges

	def collect_strip_edge_attribute(self):
		"""Store the strip edge attributes in the quad mesh.

		Parameters
		----------

		Returns
		-------
		n : int
			The number of strips.

		"""

		edges = list(self.not_none_edges())

		strip = -1
		while len(edges) > 0:
			strip += 1

			u0, v0 = edges.pop()

			edge_strip = self.edge_strip(u0, v0)

			self.set_edges_attribute('strip', strip, edge_strip)
			
			for u, v in edge_strip:
				if (u, v) in edges:
					edges.remove((u, v))
				elif (v, u) in edges:
					edges.remove((v, u))

	def edges_to_strips_dict(mesh):
		"""Output a dictionary of edges pointing to strip.

		Parameters
		----------

		Returns
		-------
		dict
			A dictionary {edge: strip}.
		"""

		return {edge: self.get_edge_attribute(edge, 'strip') for edge in self.edges()}

	def strips_to_edges_dict(self):
		"""Output a dictionary of strips pointing to edges.

		Parameters
		----------

		Returns
		-------
		strips_to_edges : dict
			A dictionary {strip: edges}.

		"""

		strips_to_edges = {}

		for edge in self.edges():
			strip = self.get_edge_attribute(edge, 'strip')

			if strip in strips_to_edges:
				strips_to_edges[strip].append(edge)
			
			else:
				strips_to_edges[strip] = [edge]
		
		return strips_to_edges
		
# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	import compas

	vertices = [[12.97441577911377, 24.33094596862793, 0.0], [18.310085296630859, 8.467333793640137, 0.0], [30.052173614501953, 18.846050262451172, 0.0], [17.135400772094727, 16.750551223754883, 0.0], [16.661802291870117, 22.973459243774414, 0.0], [14.180665969848633, 26.949295043945313, 0.0], [36.052761077880859, 26.372636795043945, 0.0], [26.180931091308594, 21.778648376464844, 0.0], [19.647378921508789, 12.288106918334961, 0.0], [9.355668067932129, 16.475896835327148, 0.0], [18.929227828979492, 16.271940231323242, 0.0], [7.34525203704834, 12.111981391906738, 0.0], [13.31309986114502, 14.699410438537598, 0.0], [18.699434280395508, 19.613750457763672, 0.0], [11.913931846618652, 10.593378067016602, 0.0], [17.163223266601563, 26.870658874511719, 0.0], [26.110898971557617, 26.634754180908203, 0.0], [22.851469039916992, 9.81414794921875, 0.0], [21.051292419433594, 7.556171894073486, 0.0], [22.1370792388916, 19.089054107666016, 0.0]]
	faces = [[15, 5, 0, 4], [0, 9, 12, 4], [9, 11, 14, 12], [14, 1, 8, 12], [1, 18, 17, 8], [17, 2, 7, 8], [2, 6, 16, 7], [16, 15, 4, 7], [13, 19, 7, 4], [19, 10, 8, 7], [10, 3, 12, 8], [3, 13, 4, 12]]

	mesh = QuadMesh.from_vertices_and_faces(vertices, faces)

	mesh.collect_strip_edge_attribute()

	for edge in mesh.edges():
		print mesh.get_edge_attribute(edge, 'strip')
