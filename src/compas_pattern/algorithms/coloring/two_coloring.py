import itertools

from compas_pattern.datastructures.mesh_quad.mesh_quad import QuadMesh

from compas_pattern.datastructures.mesh_quad.grammar_pattern import delete_strips

from compas.topology import adjacency_from_edges
from compas_pattern.topology.coloring import is_adjacency_two_colorable

from compas_pattern.utilities.lists import are_items_in_list


__all__ = [
	'two_colourable_projection',
]


class TwoColourableProjection:

	def __init__(self, quad_mesh):
		self.quad_mesh = quad_mesh
		self.results = None


	def projection(self, kmax = 1):
		"""Projection of a coarse quad mesh to the closest two-colourable sub-spaces.

		Parameters
		----------
		mesh : CoarseQuadMesh
			A coarse quad mesh.

		Returns
		-------
		results : dict
			The combination pointing to the its result. If the combination is valid, the result is a tuple of the the two-colourable mesh, the two-colourable network, and the network vertex colors.

		References
		----------
		.. [1] Oval et al., *Topology Finding of Two-Colourable Quad-Mesh Patterns in Structural Design*. Submitted.

		"""

		mesh = self.quad_mesh

		# result for input mesh
		vertices, edges = mesh.strip_graph()
		if is_adjacency_two_colorable(adjacency_from_edges(edges)) is not None:
			self.results = True
			return True

		results = {}

		# guarantee valid kmax
		n = mesh.number_of_strips()
		if kmax < 1 or kmax > n:
			kmax = n
		
		# start iteration
		k = 0
		while k < kmax:
			k += 1

			# test all combinations of (n k) strips
			for combination in itertools.combinations(mesh.strips(), k):

				# check results from potential previous sub-combinations
				for previous_combination in results:
					if are_items_in_list(previous_combination, combination):
						# if a sub-combination yielded an invalid topology do not pursue
						if results[previous_combination] == 'invalid shape topology':
							results[combination] = 'already invalid shape topology'
							break
						elif type(results[previous_combination]) == tuple:
							results[combination] = 'already two-colourable'
							break
				if combination in results:
					continue
				
				# delete strips in mesh and check validity
				copy_mesh = mesh.copy()
				copy_mesh.collect_strips()
				delete_strips(copy_mesh, combination, preserve_boundaries=True)
				topological_validity = copy_mesh.is_manifold() and copy_mesh.euler() == mesh.euler()
				if not topological_validity:
					results[combination] = 'invalid shape topology'

				# delete strip vertices in network and check colourability
				else:
					vertices, edges = copy_mesh.strip_graph()
					two_colourability = is_adjacency_two_colorable(adjacency_from_edges(edges))
					if not two_colourability:
						results[combination] = 'not two-colourable'
					else:
						results[combination] = (copy_mesh, (vertices, edges), two_colourability)

		self.results = results

	# --------------------------------------------------------------------------
	# results
	# --------------------------------------------------------------------------

	def get_results(self):
		return self.results

	def strip_deletions_yielding_two_colourability(self):
		out = []
		for combination, result in self.get_results().items():
			if type(result) == tuple:
				out.append(combination)
		return out


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	import compas

	vertices = [[1.9, 11.2, 0.0], [9.7, 9.0, 0.0], [4.3, 4.7, 0.0], [3.8, 13.2, 0.0], [1.9, 13.2, 0.0], [4.7, 2.2, 0.0], [5.7, 9.4, 0.0], [9.1, 6.4, 0.0], [14.2, 5.2, 0.0], [14.2, 2.2, 0.0], [14.2, 13.2, 0.0], [1.9, 2.2, 0.0], [4.1, 10.9, 0.0], [11.5, 5.0, 0.0], [11.4, 2.2, 0.0], [5.7, 6.7, 0.0], [14.2, 10.2, 0.0], [1.9, 4.2, 0.0], [11.4, 13.2, 0.0], [11.7, 10.6, 0.0]]
	faces = [[7, 15, 2, 13], [15, 6, 12, 2], [6, 1, 19, 12], [1, 7, 13, 19], [8, 16, 19, 13], [16, 10, 18, 19], [18, 3, 12, 19], [3, 4, 0, 12], [0, 17, 2, 12], [17, 11, 5, 2], [5, 14, 13, 2], [14, 9, 8, 13]]
	
	vertices_1 = [[-332.0, -22.0, 0.0], [-332.0, -19.0, 0.0], [-332.0, -5.0, 0.0], [-332.0, -2.0, 0.0], [-329.0, -22.0, 0.0], [-329.0, -19.0, 0.0], [-329.0, -5.0, 0.0], [-329.0, -2.0, 0.0], [-324.0, -15.0, 0.0], [-324.0, -9.0, 0.0], [-318.0, -15.0, 0.0], [-318.0, -9.0, 0.0], [-312.0, -22.0, 0.0], [-312.0, -19.0, 0.0], [-312.0, -5.0, 0.0], [-312.0, -2.0, 0.0], [-305.0, -15.0, 0.0], [-305.0, -9.0, 0.0], [-299.0, -15.0, 0.0], [-299.0, -9.0, 0.0], [-295.0, -22.0, 0.0], [-295.0, -19.0, 0.0], [-295.0, -5.0, 0.0], [-295.0, -2.0, 0.0], [-292.0, -22.0, 0.0], [-292.0, -19.0, 0.0], [-292.0, -5.0, 0.0], [-292.0, -2.0, 0.0]]
	faces_1 = [[16, 17, 14, 13], [14, 17, 19, 22], [21, 22, 19, 18], [21, 18, 16, 13], [8, 9, 6, 5], [6, 9, 11, 14], [13, 14, 11, 10], [13, 10, 8, 5], [4, 5, 1, 0], [5, 6, 2, 1], [6, 7, 3, 2], [14, 15, 7, 6], [22, 23, 15, 14], [12, 13, 5, 4], [20, 21, 13, 12], [26, 27, 23, 22], [25, 26, 22, 21], [24, 25, 21, 20]]

	mesh = QuadMesh.from_vertices_and_faces(vertices, faces)
	mesh.collect_strips()
	projection = TwoColourableProjection(mesh)
	projection.projection(kmax=2)
	print(projection.strip_deletions_yielding_two_colourability())
