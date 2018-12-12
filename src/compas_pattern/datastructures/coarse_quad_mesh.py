import math

from compas.datastructures.mesh import Mesh
from compas_pattern.datastructures.quad_mesh import QuadMesh

from compas.utilities import geometric_key

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2018, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'

__all__ = [

]

class CoarseQuadMesh(QuadMesh):

	def __init__(self):
		super(CoarseQuadMesh, self).__init__()
		self.collect_strip_edge_attribute()
		self.default_edge_attributes.update({
			'density_parameter': None
			})


	def density_global_parameter(self, density_parameter):
		"""Set the same density parameter to all edges.

		Parameters
		----------
		density_parameter : int
			A global density parameter.

		Returns
		-------

		"""

		self.set_edges_attribute('density_parameter', density_parameter, list(self.edges()))

	def density_target_length(self, target_length):
		"""Set the density parameters based on a target length and the average length of the strip edges.

		Parameters
		----------
		target_length : float
			A target length.

		Returns
		-------

		"""

		for strip, edges in self.strips_to_edges_dict().items():
			average_length = sum([self.edge_length(u, v) for u, v in edges]) / len(edges)
			density_parameter = int(math.ceil(average_length / target_length))

			self.set_edges_attribute('density_parameter', density_parameter, list(self.edges()))

	def change_density_parameter(self, strip, new_density_parameter):
		"""Change the density parameter in a strip.

		Parameters
		----------
		strip : int
			The key of the strip.
		new_density_parameter : int
			The new density parameter.

		Returns
		-------

		"""

		edges = self.strips_to_edges_dict()[strip]

		self.set_edges_attribute('density_parameter', new_density_parameter, edges)


	
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
