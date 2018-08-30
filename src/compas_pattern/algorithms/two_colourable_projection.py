import itertools
import copy

from compas.datastructures.mesh import Mesh
from compas_pattern.datastructures.mesh import mesh_euler

from compas.datastructures.network import Network
from compas_pattern.datastructures.network import graph_disjointed_parts

from compas_pattern.topology.polyline_extraction import mesh_boundaries

from compas.geometry import centroid_points

from compas_pattern.topology.face_strip_operations import face_strip_subdivide

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2018, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'

__all__ = [
	'mesh_copy_with_edge_attributes',
	'store_strip_as_edge_attribute',
	'strips_to_edges_dict',
	'strip_to_faces_dict',
	'edges_to_strips_dict',
	'faces_to_strips_dict',
	'graph_from_strip_overlap',
	'is_graph_two_colourable',
	'graph_mutiple_vertex_deletion',
	'mesh_multiple_strip_collapse',
	'have_meshes_same_euler'
	'two_colourable_projection',
]

def mesh_copy_with_edge_attributes(mesh):

	edge_attributes = {(u, v): {attr: mesh.get_edge_attribute((u, v), attr) for attr in mesh.edge[u][v]} for u, v in mesh.edges()}

	copy_mesh = mesh.copy()
	copy_mesh.update_default_edge_attributes()
	for edge in copy_mesh.edges():
		copy_mesh.set_edge_attributes(edge, edge_attributes[edge])

	return copy_mesh


def store_strip_as_edge_attribute(mesh):
	"""Collect the n strips accross a (coarse) quad mesh and store them as edge attribute, from 0 to n-1.

	Parameters
	----------
	mesh : Mesh
		A (coarse) quad mesh.

	Returns
	-------
	strip_to_edges : dict
		The edges in each strip: {strip_index: list of edges as tuples of vertices}.

	"""

	# add strip as edge attribute to store
	mesh.update_default_edge_attributes(attr_dict = {'strip': None})

	# loop over faces to group edges in strips
	strips = 0
	for fkey in mesh.faces():
		a, b, c, d = mesh.face_vertices(fkey)
		for u, v, w, x in [ [a, b, c, d], [b, c, d, a] ]:
 
			# exceptions if pseudo quad mesh with faces like [a, b, c, c]
			if u == v:
				if mesh.get_edge_attribute((w, x), 'strip') is None:
					strips += 1
					mesh.set_edge_attribute((w, x), 'strip', strips)
			elif w == x:
				if mesh.get_edge_attribute((u, v), 'strip') is None:
					strips += 1
					mesh.set_edge_attribute((u, v), 'strip', strips)

			else:
				if mesh.get_edge_attribute((u, v), 'strip') is not None and mesh.get_edge_attribute((w, x), 'strip') is not None:
					# flip one
					new_strip = mesh.get_edge_attribute((u, v), 'strip')
					old_strip = mesh.get_edge_attribute((w, x), 'strip')
					for edge in mesh.edges():
						if mesh.get_edge_attribute(edge, 'strip') == old_strip:
							mesh.set_edge_attribute(edge, 'strip', new_strip)

				elif mesh.get_edge_attribute((u, v), 'strip') is None and mesh.get_edge_attribute((w, x), 'strip') is not None:
					# add the other
					strip = mesh.get_edge_attribute((w, x), 'strip')
					mesh.set_edge_attribute((u, v), 'strip', strip)

				elif mesh.get_edge_attribute((u, v), 'strip') is not None and mesh.get_edge_attribute((w, x), 'strip') is None:
					# add the other
					strip = mesh.get_edge_attribute((u, v), 'strip')
					mesh.set_edge_attribute((w, x), 'strip', strip)

				else:
					# start new strip
					strips += 1
					mesh.set_edge_attribute((u, v), 'strip', strips)
					mesh.set_edge_attribute((w, x), 'strip', strips)

	# reorder strips
	strips = list(set([mesh.get_edge_attribute(edge, 'strip') for edge in mesh.edges()]))
	if None in strips:
		strips.remove(None)
	for edge in mesh.edges():
		old_strip = mesh.get_edge_attribute(edge, 'strip')
		if old_strip is not None:
			new_strip = strips.index(old_strip)
		mesh.set_edge_attribute(edge, 'strip', new_strip)

	return len(strips)

def strips_to_edges_dict(mesh):
	# {strip: [(u,v)]}
	# improvement: optional sorting
	strips_to_edges = {}
	for edge in mesh.edges():
		strip = mesh.get_edge_attribute(edge, 'strip')
		if strip in strips_to_edges:
			strips_to_edges[strip].append(edge)
		else:
			strips_to_edges[strip] = [edge]
	return strips_to_edges

def strip_to_faces_dict(mesh):
	# {strip: [fkey]}
	# improvement: optional sorting

	strip_to_faces = {}
	faces = list(mesh.faces())

	strips_to_edges = strips_to_edges_dict(mesh)

	for strip, edges in strips_to_edges.items():
		strip_to_faces[strip] = []
		for fkey in faces:
			a, b, c, d = mesh.face_vertices(fkey)
			if (a, b) in edges or (b, a) in edges:
				strip_to_faces[strip].append(fkey)
			elif (b, c) in edges or (c, b) in edges:
				strip_to_faces[strip].append(fkey)
			elif (c, d) in edges or (d, c) in edges:
				strip_to_faces[strip].append(fkey)
			elif (d, a) in edges or (a, d) in edges:
				strip_to_faces[strip].append(fkey)

	return strip_to_faces

def edges_to_strips_dict(mesh):
	# {(u,v): strip}
	edges_to_strips = {}
	for edge in mesh.edges():
		edges_to_strips[edge] = mesh.get_edge_attribute(edge, 'strip')

	return edges_to_strips

def faces_to_strips_dict(mesh):
	# {fkey: [strip_1, strip_2]}

	faces_to_strips = {}
	for fkey in mesh.faces():
		a, b, c, d = mesh.face_vertices(fkey)
		if a != b:
			strip_1 = mesh.get_edge_attribute((a, b), 'strip')
		else:
			strip_1 = mesh.get_edge_attribute((c, d), 'strip')
		if b != c:
			strip_2 = mesh.get_edge_attribute((b, c), 'strip')
		else:
			strip_2 = mesh.get_edge_attribute((d, a), 'strip')
		faces_to_strips[fkey] = [strip_1, strip_2]

	return faces_to_strips

def graph_from_strip_overlap(mesh):
	"""Create the strip overlap graph of a (coarse) quad mesh.
	A graph node is a quad face strip and a graph edge is a face crossed by two quad face strips.
	The strip of each edge must be previously stored as an edge attribute.

	Parameters
	----------
	mesh : Mesh
		A (coarse) quad mesh.

	Returns
	-------
	graph : graph
		The strip overlap graph.

	"""

	graph = Network()

	# add vertices
	strips_to_faces = strip_to_faces_dict(mesh)

	for strip, faces in strips_to_faces.items():
		if strip == -1:
			continue
		x, y, z = centroid_points([mesh.face_centroid(fkey) for fkey in faces])
		graph.add_vertex(key = strip, attr_dict = {'x': x, 'y': y, 'z': z})

	# add edges
	edges = []
	faces_to_strips = faces_to_strips_dict(mesh)
	for strip_1, strip_2 in faces_to_strips.values():
		# no duplicates
		if (strip_1, strip_2) not in edges and (strip_2, strip_1) not in edges:
			edges.append((strip_1, strip_2))
	for u, v in edges:
			graph.add_edge(u, v)

	return graph

def is_graph_two_colourable(graph):
	"""Try to colour a graph with two colours only.

	Parameters
	----------
	graph : Network
		A graph.

	Returns
	-------
	key_to_colour : dict, None
		A dictionary with vertex keys pointing to colours.
		None if the graph is not two-colourable.

	"""

	two_colourable = True

	# store colour per vertex key and vertex keys per rank of propagation
	key_to_colour = {}
	rank_to_keys = {}
	current_colour = 0
	current_rank = 0
	unvisited = [key for key in graph.vertices() if len(graph.vertex_neighbours(key)) > 0]
	# case of isolated vertices
	isolated_vertices = [key for key in graph.vertices() if len(graph.vertex_neighbours(key)) == 0]
	key_to_colour.update({key: 1 - current_colour for key in isolated_vertices})
	rank_to_keys[-1] = isolated_vertices

	# start from one of the vertices with the highest valency
	key_to_degree = {key: len(graph.vertex_neighbours(key)) for key in unvisited}
	univisted = sorted(unvisited, key=lambda key: key_to_degree[key])
	key_0 = unvisited.pop()
	key_to_colour[key_0] = current_colour
	rank_to_keys[current_rank] = [key_0]

	# loop until all vertices are visited
	count = len(unvisited)
	while len(unvisited) > 0 and count > 0:
		count -= 1
		# next rank and switch colour
		current_rank += 1
		current_colour = 1 - current_colour
		current_keys = []
		# collect valid neighbours of previous rank to form next rank
		for key in rank_to_keys[current_rank - 1]:
			for nbr in graph.vertex_neighbours(key):
				if nbr in unvisited and nbr not in current_keys:
					current_keys.append(nbr)
		#if no current keys (if graph has disconnected parts) start from a new one
		if len(current_keys) == 0:
			current_keys = [unvisited[-1]]
		# check that vertices of the next rank are not neighbours
		for key in current_keys:
			for key_2 in current_keys:
				if key < key_2:
					if key_2 in graph.vertex_neighbours(key):
								two_colourable = False
		# return None if not two colourable
		if not two_colourable:
			return None
		# store information before continuing
		else:
			for key in current_keys:
				key_to_colour[key] = current_colour
				unvisited.remove(key)
			rank_to_keys[current_rank] = current_keys

	return key_to_colour

def graph_mutiple_vertex_deletion(graph, vertices):
	# delete multiple nodes of a graph at once

	for vkey in vertices:
		graph.delete_vertex(vkey)

	return graph

def mesh_multiple_strip_collapse(cls, mesh, strips_to_collapse):

	boundary_vertices = mesh.vertices_on_boundary()
	boundary_corner_vertices = [vkey for vkey in boundary_vertices if len(mesh.vertex_neighbours(vkey)) == 2]

	edges_to_strips = edges_to_strips_dict(mesh)
	edges_to_collapse = [edge for edge, strip in edges_to_strips.items() if strip in strips_to_collapse]
	faces_to_collapse = [fkey for fkey, strips in faces_to_strips_dict(mesh).items() if strips[0] in strips_to_collapse or strips[1] in strips_to_collapse]

	# get groups of vertices to merge via graph of edges to collapse
	graph = Network()
	for vkey in mesh.vertices():
		x, y, z = mesh.vertex_coordinates(vkey)
		graph.add_vertex(key = vkey, attr_dict = {'x': x, 'y': y, 'z': z})
	for u, v in edges_to_collapse:
		graph.add_edge(u, v)
	parts = graph_disjointed_parts(graph)

	# refine boundaries to avoid collapse
	to_subdivide = []
	for boundary in mesh_boundaries(mesh):
		boundary_edges = [(boundary[i], boundary[i + 1]) for i in range(len(boundary) - 1)]
		boundary_edges_to_collapse = [edge for edge in edges_to_collapse if edge in boundary_edges or edge[::-1] in boundary_edges]
		if len(boundary_edges) - len(boundary_edges_to_collapse) < 3:
			for edge in boundary_edges:
				if edge not in boundary_edges_to_collapse and edge[::-1] not in boundary_edges_to_collapse:
					if edge not in to_subdivide and edge[::-1] not in to_subdivide:
						to_subdivide.append(edge)
	# refine pole points to avoid collapse
	poles = {u: [] for u, v in mesh.edges() if u == v}
	for u, v in edges_to_collapse:
		for pole in poles:
			if pole in mesh.halfedge[u] and pole in mesh.halfedge[v]:
				poles[pole].append((u, v))
	for pole, pole_edges_to_collapse in poles.items():
		vertex_faces = list(set(mesh.vertex_faces(pole)))
		if not mesh.is_vertex_on_boundary(pole):
			if len(vertex_faces) - len(pole_edges_to_collapse) < 3:
				for fkey in vertex_faces:
					face_vertices = copy.copy(mesh.face_vertices(fkey))
					face_vertices.remove(pole)
					face_vertices.remove(pole)
					u, v = face_vertices
					if (u, v) not in pole_edges_to_collapse and (v, u) not in pole_edges_to_collapse:
						if (u, v) not in to_subdivide and (v, u) not in to_subdivide:
							to_subdivide.append((u, v))

	# delete faces
	for fkey in faces_to_collapse:
		mesh.delete_face(fkey)

	for u, v in to_subdivide:
		face_strip_subdivide(cls, mesh, u, v)

	# merge vertices
	vertices_to_change = {}
	for part in parts:
		if len(part) > 1:
			# merge at the location of the unique two-valent boundary vertex ...
			xyz = None
			for vkey in part:
				if vkey in boundary_corner_vertices and xyz is None:
					xyz = mesh.vertex_coordinates(vkey)
				elif vkey in boundary_corner_vertices and xyz is not None:
					xyz = None
					break
			# ... or the unique boundary vertex ...
			if xyz is None:
				for vkey in part:
					if vkey in boundary_vertices and xyz is None:
						xyz = mesh.vertex_coordinates(vkey)
					elif vkey in boundary_vertices and xyz is not None:
						xyz = None
						break
			# ... or at the centroid
			if xyz is None:
				xyz = centroid_points([mesh.vertex_coordinates(vkey) for vkey in part])
			x, y, z = xyz
			new_vkey = mesh.add_vertex(attr_dict = {'x': x, 'y': y, 'z': z})
			vertices_to_change.update({vkey: new_vkey for vkey in part})

	for fkey in list(mesh.faces()):
		face_vertices = [vertices_to_change[vkey] if vkey in vertices_to_change else vkey for vkey in mesh.face_vertices(fkey)]
		mesh.delete_face(fkey)
		mesh.add_face(face_vertices, fkey)

	mesh.cull_vertices()

	return mesh

def have_meshes_same_euler(mesh_1, mesh_2):
	# check if two meshes are manfiold and have the same Euler characteristic

	if mesh_1.is_manifold_corrected() and mesh_2.is_manifold_corrected():
		if mesh_euler(mesh_1) == mesh_euler(mesh_2):

			return True

	return False

def is_subset_in_set(small_set, big_set):
	for i in small_set:
		is_in = False
		for j in big_set:
			if i == j:
				is_in = True
				break
		if not is_in:
			return False
	return True

def two_colourable_projection(cls, mesh, kmax = 1):
	"""Project a (coarse) quad mesh on the closest two-colourable sub-spaces.

	Parameters
	----------
	mesh : Mesh
		A (coarse) quad mesh.

	Returns
	-------
	two_col_meshes : dict
		The closest two-colourable meshes per distance: {k: two_col_meshes_k}.

	"""

	mesh.cull_vertices()

	store_strip_as_edge_attribute(mesh)
	strips = strips_to_edges_dict(mesh).keys()
	strips = [x for x in strips if x is not None]
	
	n = len(strips)

	if kmax < 1 or kmax > n:
		kmax = n

	graph = graph_from_strip_overlap(mesh)

	if is_graph_two_colourable(graph):
		return mesh

	two_colourable_meshes = {}
	kill = []
	results = {}

	k = 0
	while k < kmax:
		k += 1
		two_colourable_meshes[k] = []
		# total, good, neutral, bad
		results[k] = [0,0,0,0]

		for combi in list(itertools.combinations(range(n), k)):

			kill_too = False
			for kill_combi in kill:
				if is_subset_in_set(kill_combi, combi):
					kill_too = True
					break
			if kill_too:
				continue

			results[k][0] += 1
			trimmed_mesh = mesh_copy_with_edge_attributes(mesh)
			mesh_multiple_strip_collapse(cls, trimmed_mesh, list(combi))
			mesh_criteria = have_meshes_same_euler(mesh, trimmed_mesh)

			trimmed_graph = graph.copy()
			graph_mutiple_vertex_deletion(trimmed_graph, list(combi))
			graph_criteria = is_graph_two_colourable(trimmed_graph)

			if mesh_criteria and graph_criteria is not None:
				two_colourable_meshes[k].append([trimmed_mesh, trimmed_graph, graph_criteria])
				kill.append(combi)
				results[k][1] += 1

			elif not mesh_criteria:
				kill.append(combi)
				results[k][3] += 1

			else:
				results[k][2] += 1


		if results[k][2] == 0:
			break


	return two_colourable_meshes, results

def binom_coeff(n, k):
	k = min(k, n - k)
	x = 1
	y = 1
	i = n - k + 1
	while i <= n:
		x = (x * i) // y
		y += 1
		i += 1
	return x

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	import compas

	vertices = [[1.909000039100647, 11.21607494354248, 0.0], [9.717498779296875, 9.024598121643066, 0.0], [4.361410140991211, 4.71211576461792, 0.0], [3.813263177871704, 13.209049224853516, 0.0], [1.909000039100647, 13.209049224853516, 0.0], [4.765394687652588, 2.2476935386657715, 0.0], [5.792667865753174, 9.437114715576172, 0.0], [9.160603523254395, 6.404611587524414, 0.0], [14.286709785461426, 5.237154006958008, 0.0], [14.286709785461426, 2.2476935386657715, 0.0], [14.286709785461426, 13.209049224853516, 0.0], [1.909000039100647, 2.2476935386657715, 0.0], [4.150432109832764, 10.980650901794434, 0.0], [11.537713050842285, 5.0044331550598145, 0.0], [11.430315971374512, 2.2476935386657715, 0.0], [5.792667865753174, 6.758595943450928, 0.0], [14.286709785461426, 10.219588279724121, 0.0], [1.909000039100647, 4.240667343139648, 0.0], [11.430315971374512, 13.209049224853516, 0.0], [11.735541343688965, 10.641332626342773, 0.0]]
	faces = [[7, 15, 2, 13], [15, 6, 12, 2], [6, 1, 19, 12], [1, 7, 13, 19], [8, 16, 19, 13], [16, 10, 18, 19], [18, 3, 12, 19], [3, 4, 0, 12], [0, 17, 2, 12], [17, 11, 5, 2], [5, 14, 13, 2], [14, 9, 8, 13]]
	
	vertices_1 = [[-332.0, -22.0, 0.0], [-332.0, -19.0, 0.0], [-332.0, -5.0, 0.0], [-332.0, -2.0, 0.0], [-329.0, -22.0, 0.0], [-329.0, -19.0, 0.0], [-329.0, -5.0, 0.0], [-329.0, -2.0, 0.0], [-324.0, -15.0, 0.0], [-324.0, -9.0, 0.0], [-318.0, -15.0, 0.0], [-318.0, -9.0, 0.0], [-312.0, -22.0, 0.0], [-312.0, -19.0, 0.0], [-312.0, -5.0, 0.0], [-312.0, -2.0, 0.0], [-305.0, -15.0, 0.0], [-305.0, -9.0, 0.0], [-299.0, -15.0, 0.0], [-299.0, -9.0, 0.0], [-295.0, -22.0, 0.0], [-295.0, -19.0, 0.0], [-295.0, -5.0, 0.0], [-295.0, -2.0, 0.0], [-292.0, -22.0, 0.0], [-292.0, -19.0, 0.0], [-292.0, -5.0, 0.0], [-292.0, -2.0, 0.0]]
	faces_1 = [[16, 17, 14, 13], [14, 17, 19, 22], [21, 22, 19, 18], [21, 18, 16, 13], [8, 9, 6, 5], [6, 9, 11, 14], [13, 14, 11, 10], [13, 10, 8, 5], [4, 5, 1, 0], [5, 6, 2, 1], [6, 7, 3, 2], [14, 15, 7, 6], [22, 23, 15, 14], [12, 13, 5, 4], [20, 21, 13, 12], [26, 27, 23, 22], [25, 26, 22, 21], [24, 25, 21, 20]]


	mesh = Mesh.from_vertices_and_faces(vertices, faces)
	n = store_strip_as_edge_attribute(mesh)
	kmax = 2
	two_colourable_meshes, tested = two_colourable_projection(Mesh, mesh, kmax = kmax)


	for k in range(1, kmax + 1):
		print k, binom_coeff(n, k), len(two_colourable_meshes[k]), tested[k]

