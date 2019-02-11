import itertools

from compas_pattern.topology.grammar import  strips_to_split_to_preserve_boundaries_before_deleting_strips
from compas_pattern.topology.grammar import add_strip
from compas_pattern.topology.grammar import delete_strips
from compas_pattern.topology.grammar import split_strips

from compas.topology import breadth_first_paths

from compas.utilities import pairwise

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2019, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'

__all__ = [
	'adjacent_topologies_delete',
	'adjacent_topologies_add',
]

def adjacent_topologies_delete(quad_mesh, k):
	"""Return the adjacent topologies from a (coarse) quad mesh resulting from all possible combinations to delete k strips.

	Parameters
	----------
	quad_mesh : QuadMesh
		A quad mesh.
	k : int
		The number of strips to delete.

	Returns
	-------
	adjacent_topologies : list
		The list of adjacent topologies with tuples of (coarse) quad meshes and combinations of strips deleted.

	"""

	quad_mesh.collect_strips()

	adjacent_topologies = []
	
	for combination in itertools.combinations(list(quad_mesh.strips()), k):
		copy_mesh = quad_mesh.copy()
		copy_mesh.collect_strips()
		to_split = strips_to_split_to_preserve_boundaries_before_deleting_strips(copy_mesh, combination)
		split_strips(copy_mesh, to_split.keys())
		delete_strips(copy_mesh, combination)
		adjacent_topologies.append((copy_mesh, combination))

	return adjacent_topologies

def adjacent_topologies_add(quad_mesh, kmax):

		return {k: adjacent_topologies_add_k(quad_mesh, k) for k in range(2, kmax)}

def adjacent_topologies_add_k(quad_mesh, k):
	"""Return the adjacent topologies from a (coarse) quad mesh resulting from all possible combinations to add one strip along polyedges of length k.

	Parameters
	----------
	quad_mesh : QuadMesh
		A quad mesh.
	k : int
		The length of the polyedge.

	Returns
	-------
	adjacent_topologies : list
		The list of adjacent topologies with tuples of (coarse) quad meshes and combinations of polyedges added.

	"""

	adjacent_topologies = []

	for polyedge in all_polyedges_boundary_to_boundary_shorter_than_a_value_no_repetitions(quad_mesh, k):
		copy_mesh = quad_mesh.copy()
		copy_mesh.collect_strips()
		add_strip(copy_mesh, polyedge)
		adjacent_topologies.append((copy_mesh, polyedge))

	return adjacent_topologies

def all_polyedges_boundary_to_boundary_shorter_than_a_value_no_repetitions(quad_mesh, k):

	vertices = list(quad_mesh.vertices())
	
	polyedges = []

	for permutation in itertools.permutations(vertices, k):
		# the permutation represents a valid polyedge if...
		# valid only if extremities lie on the boundary
		if not quad_mesh.is_vertex_on_boundary(permutation[0]) or not quad_mesh.is_vertex_on_boundary(permutation[-1]):
			continue
		# polyedge only if vertices are connected
		if not all([v in quad_mesh.halfedge[u] for u, v in pairwise(permutation)]):
			continue
		polyedges.append(permutation)

	return polyedges

def all_polyedges_boundary_to_boundary_no_repetitions(quad_mesh):

	polyedges = []
	adjacency = quad_mesh.adjacency
	# all combinations of extremities on the boundary (identical extremities is excluded)
	for start, end in itertools.combinations(list(quad_mesh.vertices_on_boundary()), 2):
		# all possible paths between extremities (multiple occurences of a vertex is excluded)
		polyedges += breadth_first_paths(adjacency, start, end)

	return polyedges

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	import compas