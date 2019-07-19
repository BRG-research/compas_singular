import itertools

from compas.utilities import pairwise

__all__ = [
	'enumerate_deletion_rules',
	'enumerate_addition_rules',
	'open_boundary_polyedges_no_duplicates_length_k',
	'open_boundary_polyedges_no_duplicates',
	'closed_boundary_polyedges_no_duplicates_length_k',
	'closed_polyedges_no_duplicates'
]


def enumerate_deletion_rules(self):
	
	self.collect_strips()
	return [[skey] for skey in self.strips()]


def enumerate_addition_rules(coarse_quad_mesh, ks):

	return open_boundary_polyedges_no_duplicates(coarse_quad_mesh, ks)
	#return closed_boundary_polyedges_no_duplicates(coarse_quad_mesh, ks)

def open_boundary_polyedges_no_duplicates_length_k(mesh, k):
	"""All open polyedges with length k from a boundary vertex to another one, without duplicate vertices.

	Parameters
	----------
	mesh : Mesh
		A mesh.
	k : int
		The length of the polyedge as the number of edges.

	Returns
	-------
	polyedges : list
		List of polyedges as tuples of vertices

	"""

	polyedges = []

	for permutation in itertools.permutations(mesh.vertices(), k):
		if mesh.is_vertex_on_boundary(permutation[0]) and mesh.is_vertex_on_boundary(permutation[-1]):
			if all([v in mesh.halfedge[u] for u, v in pairwise(permutation)]):
				# avoid reversed polyedges
				if permutation[::-1] not in polyedges:
					polyedges.append(permutation)

	return polyedges


def open_boundary_polyedges_no_duplicates(mesh, ks):
	"""All open polyedges with different lengths k from a boundary vertex to another one, without duplicate vertices.

	Parameters
	----------
	mesh : Mesh
		A mesh.
	ks: list
		The lengths of the polyedge as the number of edges.

	Returns
	-------
	polyedges : list
		List of polyedges as tuples of vertices, sorted by length.

	"""

	return [polyedge for k in sorted(ks) for polyedge in open_boundary_polyedges_no_duplicates_length_k(mesh, k)]


def closed_boundary_polyedges_no_duplicates_length_k(mesh, k):
	"""All closed polyedges with length k from a boundary vertex to another one, without duplicate vertices.

	Parameters
	----------
	mesh : Mesh
		A mesh.
	k : int
		The length of the polyedge as the number of edges.

	Returns
	-------
	polyedges : list
		List of polyedges as tuples of vertices

	"""

	polyedges = []

	for permutation in itertools.permutations(mesh.vertices(), k):
		if all([v in mesh.halfedge[u] for u, v in pairwise(permutation + permutation[: 1])]):
			# avoid redundant polyedges
			for i in range(k):
				offset_permutation = permutation[i :] + permutation[: i]
				if offset_permutation in polyedges or offset_permutation[::-1] in polyedges:
					break
				if i == k -1:
					polyedges.append(permutation)

	return [list(polyedge + polyedge[: 1]) for polyedge in polyedges]


def closed_boundary_polyedges_no_duplicates(mesh, ks):
	"""All closed polyedges with different lengths k from a boundary vertex to another one, without duplicate vertices.

	Parameters
	----------
	mesh : Mesh
		A mesh.
	ks: list
		The lengths of the polyedge as the number of edges.

	Returns
	-------
	polyedges : list
		List of polyedges as tuples of vertices, sorted by length.

	"""

	return [polyedge for k in sorted(ks) for polyedge in closed_boundary_polyedges_no_duplicates_length_k(mesh, k)]


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	import compas
	