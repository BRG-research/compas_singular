from compas_pattern.datastructures.mesh.mesh import Mesh
from compas_pattern.datastructures.network.network import Network
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

from compas.datastructures import trimesh_subdivide_loop

from compas.topology import conway_ambo

from compas.topology import vertex_coloring

from compas.utilities import pairwise
from compas.utilities import window

class Kagome(Mesh):

	def __init__(self):
		super(Kagome, self).__init__()
		self.dense_mesh = None
		self.kagome = None
		self.kagome_polyedge_data = None

	@classmethod
	def from_mesh(cls, mesh):

		return cls.from_vertices_and_faces(*mesh.to_vertices_and_faces())

	@classmethod
	def from_skeleton(cls, lines, radius=1):

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

		#meshes_2 = rs.AddMesh(vertices, faces)

		meshes = []
		for node in nodes:
			vertices, faces = node.to_vertices_and_faces()
			meshes.append(rs.AddMesh(vertices, faces))

	def singularities(self):

		return [vkey for vkey in self.vertices() if (self.is_vertex_on_boundary(vkey) and self.vertex_degree(vkey) != 4) or (not self.is_vertex_on_boundary(vkey) and self.vertex_degree(vkey) != 6)]

	def singularity_points(self):

		return [self.vertex_coordinates(vkey) for vkey in self.singularities()]

	def densification(self, k = 1, fixed_boundary = True):

		if fixed_boundary:
			fixed = self.vertices_on_boundary()
		else:
			fixed = None

		self.dense_mesh = Kagome.from_mesh(trimesh_subdivide_loop(self, k, fixed))
	
	def patterning(self):

		self.kagome = conway_ambo(self.dense_mesh)

	def store_kagome_polyedge_data(self):

		self.kagome_polyedge_data = self.kagome_polyedges()

	def kagome_singularities(self):

		singular_faces = []
		for fkey in self.kagome.faces():
			singular_hex = all([len(self.kagome.face_vertices(nbr)) == 3 for nbr in self.kagome.face_neighbors(fkey)]) and len(self.kagome.face_vertices(fkey)) != 6
			singular_tri = all([len(self.kagome.face_vertices(nbr)) == 6 for nbr in self.kagome.face_neighbors(fkey)]) and len(self.kagome.face_vertices(fkey)) != 3
			if singular_hex or singular_tri:
				singular_faces.append([self.kagome.vertex_coordinates(vkey) for vkey in self.kagome.face_vertices(fkey) + self.kagome.face_vertices(fkey)[: 1]])
		return singular_faces

	def kagome_negative_singularities(self):

		return [fkey for fkey in self.kagome.faces() if all([len(self.kagome.face_vertices(nbr)) == 3 for nbr in self.kagome.face_neighbors(fkey)]) and len(self.kagome.face_vertices(fkey)) > 6]

	def kagome_negative_polygons(self):

		return [[self.kagome.vertex_coordinates(vkey) for vkey in self.kagome.face_vertices(fkey)] for fkey in self.kagome_negative_singularities()]

	def kagome_vertex_opposite_vertex(self, u, v):

		if self.kagome.is_edge_on_boundary(u, v):
			
			if self.kagome.vertex_degree(v) == 2:
				return None
			
			else:
				return [nbr for nbr in self.kagome.vertex_neighbors(v, ordered = True) if nbr != u and self.kagome.is_edge_on_boundary(v, nbr)][0]
		
		elif self.kagome.is_vertex_on_boundary(v):
			return None

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

	def kagome_polyedges_0(self):

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

	def kagome_polyedges(self):

		polyedges = []

		edge_visited = {(u, v): False for u, v in self.kagome.edges()}

		for edge in self.kagome.edges():
			if edge_visited[edge]:
				continue
			u0, v0 = edge
			# collect new polyedge
			polyedges.append(self.kagome_polyedge(u0, v0))

			# remove collected edges
			for u, v in pairwise(polyedges[-1]):
				#if (u, v) in edge_visited:
				edge_visited[(u, v)] = True
				#elif (v, u) in edge_visited:
				edge_visited[(v, u)] = True
		#for edge, visited in edges.items():
		#	if not visited:
		#		print edge 
		#print len(polyedges)
		return polyedges

	def kagome_polyline(self, u, v):

		return [self.kagome.vertex_coordinates(vkey) for vkey in self.kagome_polyedge(u0, v0)]

	def kagome_polylines(self):

		return [[self.kagome.vertex_coordinates(vkey) for vkey in polyedge] for polyedge in self.kagome_polyedge_data]

	def kagome_polyline_frames(self):
		polylines_frames = []
		for polyedge in self.kagome_polyedge_data:
			polyline_frames = []
			for i, u in enumerate(polyedge):
				#if end
				if i == len(polyedge) - 1:
					# if closed
					if polyedge[0] == polyedge[-1]:
						v = polyedge[1]
					else:
						v = polyedge[i - 1]
				else:
					v = polyedge[i + 1]
				x = self.kagome.vertex_normal(u)
				y = normalize_vector(subtract_vectors(self.kagome.vertex_coordinates(v), self.kagome.vertex_coordinates(u)))
				if i == len(polyedge) - 1 and polyedge[0] != polyedge[-1]:
					y = scale_vector(y, -1)
				z = cross_vectors(x, y)
				polyline_frames.append([x, y, z])
			polylines_frames.append(polyline_frames)
		return polylines_frames

	def kagome_polyedge_colouring(self):

		polyedges = self.kagome_polyedge_data

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

	def kagome_polyedge_colouring_2(self):

		polyedges = self.kagome_polyedge_data

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

		return [key_to_colour[key] for key in sorted(key_to_colour.keys())]

	def kagome_polyline_colouring(self):

		return {tuple([tuple(self.kagome.vertex_coordinates(vkey)) for vkey in polyedge]): colour for polyedge, colour in self.kagome_polyedge_colouring().items()}

	def kagome_polyedge_weaving(self):

		mesh = self.kagome

		edge_to_polyedge_index = {}
		for i, polyedge in enumerate(self.kagome_polyedge_data):
			for u, v in pairwise(polyedge):
				edge_to_polyedge_index[(u, v)] = i
				edge_to_polyedge_index[(v, u)] = i

		vertex_to_polyege_offset = {vkey: {} for vkey in mesh.vertices()}
		for fkey in mesh.faces():
			if len(mesh.face_vertices(fkey)) == 3:
				for u, v, w in window(mesh.face_vertices(fkey) + mesh.face_vertices(fkey)[:2], n = 3):
					vertex_to_polyege_offset[v].update({edge_to_polyedge_index[(u, v)]: +1, edge_to_polyedge_index[(v, w)]: -1})
			else:
				for u, v, w in window(mesh.face_vertices(fkey) + mesh.face_vertices(fkey)[:2], n = 3):
					vertex_to_polyege_offset[v].update({edge_to_polyedge_index[(u, v)]: -1, edge_to_polyedge_index[(v, w)]: +1})

		polyedge_weave = []
		for i, polyedge in enumerate(self.kagome_polyedge_data):
			polyedge_weave.append([vertex_to_polyege_offset[vkey][i] for vkey in polyedge])

		return polyedge_weave


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	import compas
	from compas.plotters import MeshPlotter

	vertices = [
		[0., 0., 0.],
		[1., 0., 0.],
		[1., 1., 0.],
		[0., 1., 0.],
		[0.5, 0.5, 0.],	
	]

	faces = [
		[0, 1, 4],
		[1, 2, 4],
		[2, 3, 4],
		[3, 0, 4],
	]

	lines = [
		([0., 0., 0.],[1., 0., -1.]),
		([0., 0., 0.],[-1., 0., -1.]),
		([0., 0., 0.],[0., 1., -1.]),
		([0., 0., 0.],[0., -1., -1.]),
		([0., 0., 0.],[0., 0., 1.]),
		]

	#kagome = Kagome.from_skeleton(lines)
	kagome = Kagome.from_vertices_and_faces(vertices, faces)
	kagome.densification(3)
	kagome.patterning()
	kagome.store_kagome_polyedge_data()

	plotter = MeshPlotter(kagome.kagome)
	plotter.draw_vertices(radius=.005)
	plotter.draw_edges()
	plotter.draw_faces()
	plotter.show()

	#print kagome.kagome_negative_singularities()
	#print kagome.kagome_singularities()
	#print kagome.kagome_polyline_frames()
	#kagome.kagome_polyedges()
	#kagome.kagome_polyline_colouring()
	kagome.kagome_polyedge_weaving()

