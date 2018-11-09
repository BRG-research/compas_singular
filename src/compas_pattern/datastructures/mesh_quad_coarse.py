import math

from compas_pattern.datastructures.mesh import Mesh
from compas_pattern.datastructures.mesh_quad import QuadMesh

from compas.utilities import geometric_key

from compas.datastructures.mesh.operations.weld import meshes_join_and_weld

from compas.geometry.algorithms.interpolation import discrete_coons_patch

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2018, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'

__all__ = [
	'CoarseQuadMesh'
]

class CoarseQuadMesh(QuadMesh):

	def __init__(self):
		super(CoarseQuadMesh, self).__init__()
		self.stripdata = {}
		self.quadmesh = QuadMesh()

	# --------------------------------------------------------------------------
	# density getters
	# --------------------------------------------------------------------------

	def get_strip_density(self, skey):
		"""Get the density of a strip.

		Parameters
		----------
		skey : hashable
			A strip key.

		Returns
		----------
		int
			The strip density.

		"""
		return self.stripdata['density'][skey]

	def get_strip_densities(self):
		"""Get the density of a strip.

		Returns
		----------
		dict
			The dictionary of the strip densities.

		"""
		return self.stripdata['density']

	# --------------------------------------------------------------------------
	# density setters
	# --------------------------------------------------------------------------

	def init_strip_density(self):
		"""Initiate data for strips and their densities.

		Parameters
		----------
		skey : hashable
			A srip key.
		d : int
			A density parameter.

		"""

		self.collect_strips()
		self.stripdata.update({'density': {skey: 1 for skey in self.strips()}})

	def set_strip_density(self, skey, d):
		"""Set the densty of one strip.

		Parameters
		----------
		skey : hashable
			A srip key.
		d : int
			A density parameter.

		"""

		self.stripdata['density'][skey] = d

	def set_strips_density(self, d):
		"""Set the same density to all strips.

		Parameters
		----------
		d : int
			A density parameter.
		
		"""

		for skey in self.strips():
			self.set_strip_density(skey, d)

	def set_strip_density_target(self, t):
		"""Set the strip densities based on a target length and the average length of the strip edges.

		Parameters
		----------
		t : float
			A target length.

		Returns
		-------

		"""

		for skey in self.strips():
			self.set_strip_density(skey, int(math.ceil(sum([self.edge_length(u, v) for u, v in self.strip_edges(skey)]) / len(list(self.strip_edges(skey))) / t)))

	# --------------------------------------------------------------------------
	# densification
	# --------------------------------------------------------------------------

	def densification(self):
		"""Generate a denser quad mesh from the coarse quad mesh and its strip densities.

		Returns
		-------
		QuadMesh
			A denser quad mesh.

		"""
		meshes = []

		for fkey in self.faces():
			ab, bc, cd, da = [[self.edge_point(u, v, float(i) / float(self.get_strip_density(self.edge_strip((u, v))))) for i in range(0, self.get_strip_density(self.edge_strip((u, v))) + 1)] for u, v in self.face_halfedges(fkey)]
			vertices, faces = discrete_coons_patch(ab, bc, list(reversed(cd)), list(reversed(da)))
			meshes.append(QuadMesh.from_vertices_and_faces(vertices, faces))


		self.quadmesh = meshes_join_and_weld(meshes)

		return self.quadmesh
# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	import compas

	vertices = [[12.97441577911377, 24.33094596862793, 0.0], [18.310085296630859, 8.467333793640137, 0.0], [30.052173614501953, 18.846050262451172, 0.0], [17.135400772094727, 16.750551223754883, 0.0], [16.661802291870117, 22.973459243774414, 0.0], [14.180665969848633, 26.949295043945313, 0.0], [36.052761077880859, 26.372636795043945, 0.0], [26.180931091308594, 21.778648376464844, 0.0], [19.647378921508789, 12.288106918334961, 0.0], [9.355668067932129, 16.475896835327148, 0.0], [18.929227828979492, 16.271940231323242, 0.0], [7.34525203704834, 12.111981391906738, 0.0], [13.31309986114502, 14.699410438537598, 0.0], [18.699434280395508, 19.613750457763672, 0.0], [11.913931846618652, 10.593378067016602, 0.0], [17.163223266601563, 26.870658874511719, 0.0], [26.110898971557617, 26.634754180908203, 0.0], [22.851469039916992, 9.81414794921875, 0.0], [21.051292419433594, 7.556171894073486, 0.0], [22.1370792388916, 19.089054107666016, 0.0]]
	faces = [[15, 5, 0, 4], [0, 9, 12, 4], [9, 11, 14, 12], [14, 1, 8, 12], [1, 18, 17, 8], [17, 2, 7, 8], [2, 6, 16, 7], [16, 15, 4, 7], [13, 19, 7, 4], [19, 10, 8, 7], [10, 3, 12, 8], [3, 13, 4, 12]]

	mesh = CoarseQuadMesh.from_vertices_and_faces(vertices, faces)
	
	mesh.init_strip_density()
	print mesh.number_of_strips()
	
	mesh.set_strip_density_target(1)

	mesh.get_strip_densities()
	for edge in mesh.edges():
		pass
		#print mesh.get_strip_density(mesh.edge_strip(edge))
	mesh.densification()
	quadmesh = mesh.quadmesh
	print quadmesh.number_of_faces()
