from compas_pattern.datastructures.mesh import Mesh
from compas_pattern.datastructures.network import Network
from compas.geometry import convex_hull

from compas.geometry import subtract_vectors
from compas.geometry import normalize_vector
from compas.geometry import dot_vectors
from compas.geometry import cross_vectors
from compas.geometry import midpoint_line
from compas.geometry import scale_vector
from compas.geometry import add_vectors
from compas.geometry import distance_point_point
from compas.geometry import centroid_points

from compas.datastructures import meshes_join_and_weld
from compas.datastructures import mesh_weld

from compas.topology import trimesh_subdivide_loop

from compas.topology import conway_ambo

from compas.topology import vertex_coloring

from compas.utilities import pairwise

class Weaving(Mesh):

	def __init__(self):
		super(Weaving, self).__init__()
		self.dense_mesh = None
		self.kagome = None

	@classmethod
	def from_mesh(cls, mesh):

		return cls.from_vertices_and_faces(*mesh.to_vertices_and_faces())

	@classmethod
	def from_lines(cls, lines):


		radius = .2

		network = Network.from_lines(lines)

		tube_extremities = {}

		nodes = []
		for vkey in network.vertices():
			if len(network.vertex_neighbors(vkey)) > 1:
				
				points = [network.edge_point(vkey, nbr, t = float(radius) / network.edge_length(vkey, nbr)) for nbr in network.vertex_neighbors(vkey)]
				faces = convex_hull(points)
				mesh = cls.from_vertices_and_faces(points, faces)
				
				meshes = []
				
				for fkey in mesh.faces():
					vertices = [mesh.edge_midpoint(u, v) for u, v in mesh.face_halfedges(fkey)]
					faces = [[0,1,2]]
					meshes.append(cls.from_vertices_and_faces(vertices, faces))
				
				for vkey_2 in mesh.vertices():
					tops = []
					bottoms = []
					n = normalize_vector(subtract_vectors(mesh.vertex_coordinates(vkey_2), network.vertex_coordinates(vkey)))
					for i in range(len(mesh.vertex_neighbors(vkey_2))):
						pt_0 = mesh.edge_midpoint(vkey_2, mesh.vertex_neighbors(vkey_2, ordered = True)[i - 1])
						bottoms.append(pt_0)
						pt_1 = mesh.edge_midpoint(vkey_2, mesh.vertex_neighbors(vkey_2, ordered = True)[i])
						pt_2 = midpoint_line([pt_0, pt_1])
						pt_2 = add_vectors(scale_vector(n, distance_point_point(pt_0, pt_1)), pt_2)
						tops.append(pt_2)
						vertices = [pt_0, pt_2, pt_1]
						faces = [[0,1,2]]
						meshes.append(cls.from_vertices_and_faces(vertices, faces))
					for i in range(len(tops)):
						vertices = [tops[i - 1], tops[i], bottoms[i]]
						faces = [[0,1,2]]
						meshes.append(cls.from_vertices_and_faces(vertices, faces))
					#print network.vertex_neighbors(vkey), network.vertex_neighbors(vkey)[vkey_2]
					tube_extremities[(vkey, network.vertex_neighbors(vkey)[vkey_2])] = tops
						
				mesh = meshes_join_and_weld(meshes)
				
				#dense_mesh = trimesh_subdivide_loop(mesh, k = 3)
				
				nodes.append(mesh)

		return nodes[0]

		meshes_2 = []
		for u, v in network.edges():
			if len(network.vertex_neighbors(u)) > 1 and len(network.vertex_neighbors(v)) > 1:
				#print len(tube_extremities[(u, v)])
				#print len(tube_extremities[(v, u)])
				if len(tube_extremities[(u, v)]) == len(tube_extremities[(v, u)]):
					n = len(tube_extremities[(u, v)])
					l = network.edge_length(u, v) - 2 * radius
					m = math.floor(l / radius) + 1
					print n, m
					pt_uv = tube_extremities[(u, v)]
					pt_vu = list(reversed(tube_extremities[(v, u)]))
					dmin = -1
					imin = None
					for i in range(n):
						distance = sum([distance_point_point(pt_uv[j], pt_vu[i + j - len(pt_vu)]) for j in range(n)])
						if dmin < 0 or distance < dmin:
							dmin = distance
							imin = i
					pt_vu = [pt_vu[imin + j - len(pt_vu)] for j in range(n)]
					array = [pt_uv]
					for i in range(int(m)):
						polygon = []
						for j in range(int(n)):
							u = pt_uv[j]
							v = pt_vu[j]
							polygon.append(add_vectors(scale_vector(u, (float(m) - 1 - float(i))/float(m - 1)), scale_vector(v, float(i)/float(m - 1))))
						array.append(polygon)
					array.append(pt_vu)
					#print len(array), len(array[0]), len(array[1]), len(array[2]), len(array[3])
					for i in range(int(n)):
						for j in range(int(m)):
							vertices = [array[i - 1][j - 1], array[i - 1][j], array[i][j]]
							faces = [[0, 1, 2]]
							meshes_2.append(Mesh.from_vertices_and_faces(vertices, faces))

		vertices, faces = join_and_weld_meshes(meshes_2)
		print len(vertices), len(faces)
		#meshes_2 = rs.AddMesh(vertices, faces)

		meshes = []
		for node in nodes:
			vertices, faces = node.to_vertices_and_faces()
			meshes.append(rs.AddMesh(vertices, faces))

	def singularities(self):

		return [vkey for vkey in self.vertices() if (self.is_vertex_on_boundary(vkey) and self.vertex_valency(vkey) != 4) or (not self.is_vertex_on_boundary(vkey) and self.vertex_valency(vkey) != 6)]

	def singularity_points(self):

		return [self.vertex_coordinates(vkey) for vkey in self.singularities()]

	def densification(self, k = 1):

		self.dense_mesh = Weaving.from_mesh(trimesh_subdivide_loop(self, k, fixed = None))
	
	def patterning(self):

		self.kagome = conway_ambo(self.dense_mesh)

	def kagome_negative_singularities(self):

		return [fkey for fkey in self.kagome.faces() if all([len(self.kagome.face_vertices(nbr)) == 3 for nbr in self.kagome.face_neighbors(fkey)]) and len(self.kagome.face_vertices(fkey)) > 6]

	def kagome_negative_polygons(self):

		return [[self.kagome.vertex_coordinates(vkey) for vkey in self.kagome.face_vertices(fkey)] for fkey in self.kagome_negative_singularities()]

	def kagome_vertex_opposite_vertex(self, u, v):

		if self.kagome.is_vertex_on_boundary(v):
			
			if not self.kagome.is_vertex_on_boundary(u):
				return None
			
			else:
				return [nbr for nbr in self.kagome.vertex_neighbors(v) if nbr != u and self.kagome.is_vertex_on_boundary(nbr)][0]
		
		else:
			nbrs = self.kagome.vertex_neighbors(v, ordered = True)
			return nbrs[nbrs.index(u) - 2]

	def kagome_polyedge(self, u0, v0):

		polyedge = [u0, v0]

		while len(polyedge) <= self.kagome.number_of_vertices():

			# end if closed loop
			if polyedge[0] == polyedge[-1]:
				break

			# get next vertex accros four-valent vertex
			w = self.kagome_vertex_opposite_vertex(*polyedge[-2 :])

			# flip if end of first extremity
			if w is None:
				polyedge = list(reversed(polyedge))
				# stop if end of second extremity
				w = self.kagome_vertex_opposite_vertex(*polyedge[-2 :])
				if w is None:
					break

			# add next vertex
			polyedge.append(w)

		return polyedge

	def kagome_polyedges(self):

		polyedges = []

		edges = list(self.kagome.edges())

		while len(edges) > 0:

			# collect new polyedge
			u0, v0 = edges.pop()
			polyedges.append(self.kagome_polyedge(u0, v0))

			# remove collected edges
			for u, v in pairwise(polyedges[-1]):
				if (u, v) in edges:
					edges.remove((u, v))
				elif (v, u) in edges:
					edges.remove((v, u))

		return polyedges

	def kagome_polyline(self, u, v):

		return [self.kagome.vertex_coordinates(vkey) for vkey in self.kagome_polyedge(u0, v0)]

	def kagome_polylines(self):

		return [[self.kagome.vertex_coordinates(vkey) for vkey in polyedge] for polyedge in self.kagome_polyedges()]

	def kagome_polyedge_colouring(self):

		polyedges = self.kagome_polyedges()

		edge_to_polyedge_index = {vkey: {} for vkey in self.kagome.vertices()}
		for i, polyedge in enumerate(polyedges):
			for u, v in pairwise(polyedge):
				edge_to_polyedge_index[u][v] = i
				edge_to_polyedge_index[v][u] = i

		vertices = [centroid_points([self.kagome.vertex_coordinates(vkey) for vkey in polyedge]) for polyedge in polyedges]

		edges = []
		for idx, polyedge in enumerate(polyedges):
			for vkey in polyedge:
				for vkey_2 in self.kagome.vertex_neighbors(vkey):
					idx_2 = edge_to_polyedge_index[vkey][vkey_2]
					if idx_2 != idx and idx < idx_2 and (idx, idx_2) not in edges:
						edges.append((idx, idx_2))

		polyedge_network = Network.from_vertices_and_edges(vertices, edges)

		key_to_colour = vertex_coloring(polyedge_network.adjacency)

		return {tuple(polyedge): key_to_colour[i] for i, polyedge in enumerate(polyedges)}

	def kagome_polyline_colouring(self):

		return {tuple([tuple(self.kagome.vertex_coordinates(vkey)) for vkey in polyedge]): colour for polyedge, colour in self.kagome_polyedge_colouring().items()}

	# def kagome_polyedge_colouring(self):

	# 	polyedges = self.kagome_polyedges()

	# 	edge_to_polyedge = {u: {} for self.kagome.vertices()}

	# 	for i, polyedge in enumerate(polyedges):
	# 		for u, v in pairwise(polyedge):
	# 			edge_to_polyedge[u][v] = i
	# 			edge_to_polyedge[v][u] = i

	# 	edge_to_polyedge = {u: {} for self.kagome.vertices()}

	# 	tri_faces = [fkey for fkey in self.kagome.faces() if len(self.kagome.face_vertices(fkey)) == 3]

	# 	polyedge_to_colour = {i: -1 for i in range(len(polyedges))}

	# 	to_visit = polyedges[:]
	# 	count = len(to_visit) * 2
	# 	while to_visit and count:
	# 		count -= 1
	# 		polyedge = to_visit.pop()
	# 		polyedge_to_colour[]



# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	import compas


	lines = [
		([0., 0., 0.],[1., 0., -1.]),
		([0., 0., 0.],[-1., 0., -1.]),
		([0., 0., 0.],[0., 1., -1.]),
		([0., 0., 0.],[0., -1., -1.]),
		([0., 0., 0.],[0., 0., 1.]),
		]

	weaving = Weaving.from_lines(lines)
	weaving.densification(2)
	weaving.patterning()

	weaving.kagome_negative_singularities()
	#print weaving.kagome_mesh
	weaving.kagome_polyedges()

	weaving.kagome_polyline_colouring()


