try:
	import networkx as nx
except:
	pass

__all__ = [
	'strip_graph',
	'are_strip_graphs_isomorphic',
	'are_strips_isomorphic',
	'mesh_graph',
	'are_mesh_graphs_isomorphic',
	'are_meshes_isomorphic',
	'matches_between_ismorphic_meshes',
	'remove_isomorphism_in_polyedge'
]


# --------------------------------------------------------------------------
# strip isomorphism
# --------------------------------------------------------------------------


def strip_graph(mesh, close_strip_data=False):
	# graph of quad mesh strips: one graph vertex <-> one mesh strip and one graph <-> edge one mesh face
	# graph vertices have an attribute whether the corresponding strip is closed or not

	if mesh.data['attributes']['strips'] is None or mesh.data['attributes']['strips'] == {}:
		mesh.collect_strips()

	graph = nx.MultiGraph([tuple(mesh.face_strips(fkey)) for fkey in mesh.faces()])
	if close_strip_data:
		nx.set_node_attributes(graph, {skey : {'closed': mesh.is_strip_closed(skey)} for skey in mesh.strips()})
	return graph


def are_strip_graphs_isomorphic(strip_graph_i, strip_graph_j):
	# check if two strip graphs are isomorphic, including closeness data
	return nx.is_isomorphic(strip_graph_i, strip_graph_j, node_match=nx.isomorphism.categorical_node_match('closed', None))


def are_strips_isomorphic(mesh_i, mesh_j, close_strip_data=False):
	strip_graph_i = strip_graph(mesh_i, close_strip_data=close_strip_data)
	strip_graph_j = strip_graph(mesh_j, close_strip_data=close_strip_data)
	return are_strip_graphs_isomorphic(strip_graph_i, strip_graph_j)


# --------------------------------------------------------------------------
# mesh isomorphism
# --------------------------------------------------------------------------


def mesh_graph(mesh, boundary_edge_data=False):
	# graph of meshes with edges only
	# edges have an attribute whether they are on the boundary or not (vertex attributes would not be sufficient)
	graph = nx.MultiGraph(mesh.edges())
	if boundary_edge_data:
		 nx.set_edge_attributes(graph, {(*edge, i): {'boundary': mesh.is_edge_on_boundary(*edge)} for i, edge in enumerate(mesh.edges())})
	return graph


def are_mesh_graphs_isomorphic(mesh_graph_i, mesh_graph_j):
	# check if two mesh graphs are isomorphic, including boundary data
	return nx.is_isomorphic(mesh_graph_i, mesh_graph_j, edge_match=nx.isomorphism.categorical_edge_match('boundary', None))


def are_meshes_isomorphic(mesh_i, mesh_j, boundary_edge_data=False):
	mesh_graph_i = mesh_graph(mesh_i, boundary_edge_data=boundary_edge_data)
	mesh_graph_j = mesh_graph(mesh_j, boundary_edge_data=boundary_edge_data)
	return are_mesh_graphs_isomorphic(mesh_graph_i, mesh_graph_j)


def matches_between_ismorphic_meshes(mesh_i, mesh_j, boundary_edge_data=False):
	mesh_graph_i = mesh_graph(mesh_i, boundary_edge_data=boundary_edge_data)
	mesh_graph_j = mesh_graph(mesh_j, boundary_edge_data=boundary_edge_data)
	matcher = nx.isomorphism.GraphMatcher(mesh_graph_i, mesh_graph_j)
	return matcher.match()

# --------------------------------------------------------------------------
# polyedge isomorphism
# --------------------------------------------------------------------------


def remove_isomorphism_in_polyedge(polyedge):
	# remove isomorphisms in polyedges (open or closed)

	# if closed: min value first, and its minimum neighbour value second
	if polyedge[0] == polyedge[-1]:
		polyedge = polyedge[:-1]
		candidates = []

		start = min(polyedge)
		for i, key in enumerate(polyedge):
			# collect all candidates, there may be multiple minimum values and multiple minimum neighbours
			if key == start:        
				candidate = polyedge[i:] + polyedge[:i] + [polyedge[i]]
				candidates.append(candidate)
				candidates.append(list(reversed(candidate)))
		for k in range(1, len(polyedge) + 1):
			n = len(candidates)
			if n == 1:
				break
			# get minimum-sum sub-polyedge
			min_x = None
			for candidate in candidates:
				x = sum(candidate[:k])
				if min_x is None or x < min_x:
					min_x = x
			# compare to minimum-sum sub-polyedge
			for i, candidate in enumerate(reversed(candidates)):
				if sum(candidate[:k]) > min_x:
					del candidates[n - i - 1]
		# potentially multiple canidates left due to symmetry in polyedge, but no isomorphism left
		polyedge = candidates[0]

	# if open: minimum value extremmity at the start
	else:
		if polyedge[0] > polyedge[-1]:
			polyedge = list(reversed(polyedge))

	return polyedge


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	pass

