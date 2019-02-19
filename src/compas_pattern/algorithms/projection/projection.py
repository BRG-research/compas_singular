import itertools

from compas_pattern.datastructures.mesh_quad.mesh_quad import QuadMesh

from compas_pattern.datastructures.mesh_quad.grammar import delete_strips_safe

from compas_pattern.datastructures.network.coloring import is_network_two_colorable

from compas_pattern.utilities.lists import are_items_in_list

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2018, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'

__all__ = [
	'two_colourable_projection',
]


def two_colourable_projection(mesh, kmax = 1):
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
	.. [1] Oval et al., *Topology Finding of Two-Colourable Patterns*. In progress.

	"""

	# result for input mesh
	strip_network = mesh.strip_connectivity()
	results = {(): is_network_two_colorable(strip_network)}

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
					if results[previous_combination] == 'invalid topology':
						results[combination] = 'already invalid topology'
						break
					elif type(results[previous_combination]) == tuple:
						results[combination] = 'already two-colourable'
						break
			if combination in results:
				continue
			
			# delete strips in mesh and check validity
			copy_mesh = mesh.copy()
			copy_mesh.collect_strips()
			delete_strips_safe(copy_mesh, combination)
			topological_validity = copy_mesh.is_manifold() and copy_mesh.euler() == mesh.euler()
			if not topological_validity:
				results[combination] = 'invalid topology'

			# delete strip vertices in network and check colourability
			else:
				copy_network = strip_network.copy()
				for vkey in combination:
					copy_network.delete_vertex(vkey)
				two_colourability = is_network_two_colorable(copy_network)
				if not two_colourability:
					results[combination] = 'not two-colourable'
				else:
					results[combination] = (copy_mesh, copy_network, two_colourability)

	return results


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	import compas

	vertices = [[1.909000039100647, 11.21607494354248, 0.0], [9.717498779296875, 9.024598121643066, 0.0], [4.361410140991211, 4.71211576461792, 0.0], [3.813263177871704, 13.209049224853516, 0.0], [1.909000039100647, 13.209049224853516, 0.0], [4.765394687652588, 2.2476935386657715, 0.0], [5.792667865753174, 9.437114715576172, 0.0], [9.160603523254395, 6.404611587524414, 0.0], [14.286709785461426, 5.237154006958008, 0.0], [14.286709785461426, 2.2476935386657715, 0.0], [14.286709785461426, 13.209049224853516, 0.0], [1.909000039100647, 2.2476935386657715, 0.0], [4.150432109832764, 10.980650901794434, 0.0], [11.537713050842285, 5.0044331550598145, 0.0], [11.430315971374512, 2.2476935386657715, 0.0], [5.792667865753174, 6.758595943450928, 0.0], [14.286709785461426, 10.219588279724121, 0.0], [1.909000039100647, 4.240667343139648, 0.0], [11.430315971374512, 13.209049224853516, 0.0], [11.735541343688965, 10.641332626342773, 0.0]]
	faces = [[7, 15, 2, 13], [15, 6, 12, 2], [6, 1, 19, 12], [1, 7, 13, 19], [8, 16, 19, 13], [16, 10, 18, 19], [18, 3, 12, 19], [3, 4, 0, 12], [0, 17, 2, 12], [17, 11, 5, 2], [5, 14, 13, 2], [14, 9, 8, 13]]
	
	vertices_1 = [[-332.0, -22.0, 0.0], [-332.0, -19.0, 0.0], [-332.0, -5.0, 0.0], [-332.0, -2.0, 0.0], [-329.0, -22.0, 0.0], [-329.0, -19.0, 0.0], [-329.0, -5.0, 0.0], [-329.0, -2.0, 0.0], [-324.0, -15.0, 0.0], [-324.0, -9.0, 0.0], [-318.0, -15.0, 0.0], [-318.0, -9.0, 0.0], [-312.0, -22.0, 0.0], [-312.0, -19.0, 0.0], [-312.0, -5.0, 0.0], [-312.0, -2.0, 0.0], [-305.0, -15.0, 0.0], [-305.0, -9.0, 0.0], [-299.0, -15.0, 0.0], [-299.0, -9.0, 0.0], [-295.0, -22.0, 0.0], [-295.0, -19.0, 0.0], [-295.0, -5.0, 0.0], [-295.0, -2.0, 0.0], [-292.0, -22.0, 0.0], [-292.0, -19.0, 0.0], [-292.0, -5.0, 0.0], [-292.0, -2.0, 0.0]]
	faces_1 = [[16, 17, 14, 13], [14, 17, 19, 22], [21, 22, 19, 18], [21, 18, 16, 13], [8, 9, 6, 5], [6, 9, 11, 14], [13, 14, 11, 10], [13, 10, 8, 5], [4, 5, 1, 0], [5, 6, 2, 1], [6, 7, 3, 2], [14, 15, 7, 6], [22, 23, 15, 14], [12, 13, 5, 4], [20, 21, 13, 12], [26, 27, 23, 22], [25, 26, 22, 21], [24, 25, 21, 20]]


	mesh = QuadMesh.from_vertices_and_faces(vertices, faces)
	
	mesh.collect_strips()
	print two_colourable_projection(mesh, kmax = 2)


