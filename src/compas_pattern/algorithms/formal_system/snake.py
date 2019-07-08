from math import floor
from collections import deque

from compas_pattern.datastructures.mesh_quad.mesh_quad import QuadMesh
from compas_pattern.datastructures.mesh_quad.grammar_pattern import add_strip
from compas_pattern.datastructures.mesh_quad.grammar_pattern import delete_strip

from compas.utilities import window

__all__ = [
	'Snake'
]

class Snake:

	def __init__(self, mesh):
		self.mesh = mesh
		self.polyedge = []

	def initiate_polyedge_0(self):
		# initate from the first vertex and its first neighbor
		self.polyedge = self.mesh.vertices_on_boundary()[:1]
		self.polyedge.append(self.mesh.vertex_neighbors(self.polyedge[-1], ordered = True)[0])

	def initiate_polyedge(self, k0, k1):
		# normalised parameters k0 and k1 between 0 and 1 to select a vertex and a neighbour
		n0 = self.mesh.number_of_vertices()
		u0 = list(self.mesh.vertices())[floor(k0 * n0)]
		n1 = len(self.mesh.vertex_neighbors(u0))
		u1 = self.mesh.vertex_neighbors(u0)[floor(k1 * n1)]
		self.polyedge = [u0, u1]

	def norm_value_interval(self, norm_value, nb_int):
		# the number of the sub-interval a value in [0, 1[ belongs to 
		return floor(norm_value * nb_int) + 1

	def value_interval(self, value, max_value, nb_int):
		# the number of the sub-interval a value in [0, max_value[ belongs to
		return self.norm_value_interval(value / max_value, nb_int)

	def format_value_to_rules(self, value, length):
		# convert a float 0.783629... in rules [78, 36, 29, ...] of a given length
		value = str(value)[2:]
		#print('value: ', value)
		return [int(value[i : i + length]) for i in range(0, floor(len(value) / length))]

	def interpret(self, values):
		values = deque(values)
		while values:
			value = values.popleft()
			self.apply_rules(self.format_value_to_rules(value, 2))

	def apply_rules(self, rules):
		rules = deque(rules)
		for i in range(2):
			r0 = rules.popleft()
			r1 = rules.popleft()
			self.initiate_polyedge(r0 / 10.0 ** 2, r1 / 10.0 ** 2)
		#print(rules)
		while rules:
			rule = rules.popleft()
			added = self.apply_rule(rule)
			if added:
				break

	def apply_rule(self, rule):
		v = self.polyedge[-1]
		#print(self.polyedge)
		n = len(self.mesh.vertex_neighbors(v))
		k = self.value_interval(rule, 10 ** 2, n + 1)
		#print('k: ', k)
		if k == n + 1:
			#print('polyedge: ', self.polyedge)
			self.addition()
			return True
		else:
			self.add_next_vertex_n(k)
		return False

	def addition(self):
		if self.is_polyedge_valid_for_strip_addition():
			if all([self.polyedge.count(vkey) == 1 for vkey in self.polyedge[1:-1]]) and not(self.polyedge[0] == self.polyedge[-1] and len(self.polyedge) <= 3):
				skey, left_polyedge, right_polyedge = add_strip(self.mesh, self.polyedge)
				return True
		return False

	def is_polyedge_valid_for_strip_addition(self):
		# the polyedge must be at leat one edge long, and closed or have extremities on the boundary
		if len(self.polyedge) > 1:
			if self.polyedge[0] == self.polyedge [-1] or (self.mesh.is_vertex_on_boundary(self.polyedge[0]) and self.mesh.is_vertex_on_boundary(self.polyedge[-1])):
				return True
		return False

	def get_next_vertex_n(self, u, v, n):
		# get the next vertex w that is the vertex number n after vertex u among the adjacent vertices to vertex v
		neighbors = self.mesh.vertex_neighbors(v, ordered = True)
		i = neighbors.index(u)
		w = neighbors[i + n - len(neighbors)]
		return w

	def add_next_vertex_n(self, n):
		# add vertex to polyedge
		u, v = self.polyedge[-2:]
		w = self.get_next_vertex_n(u, v, n)
		self.polyedge.append(w)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	import random
	from math import pi
	from math import floor
	from compas_pattern.datastructures.mesh_quad_coarse.mesh_quad_coarse import CoarseQuadMesh
	from compas_pattern.algorithms.formal_system.snake import Snake
	from compas.geometry.analytical import circle_evaluate
	from compas_pattern.datastructures.mesh.operations import mesh_move_vertex_to
	from compas_pattern.datastructures.mesh.operations import mesh_move_by
	from compas.numerical import fd_numpy
	from compas.numerical import ga
	from compas.datastructures import meshes_join
	from compas_plotters.meshplotter import MeshPlotter
	from compas_plotters.gaplotter import visualize_evolution

	def define_density(mesh, nb_faces):
		mesh.set_strips_density(1)
		mesh.set_mesh_density_face_target(nb_faces)
		mesh.densification()

	def fix_boundaries(mesh):
		n = len(mesh.vertices_on_boundary())
		for i, vkey in enumerate(mesh.boundaries()[0]):
			xyz = circle_evaluate(2.0 * pi * i / n, 10)
			mesh_move_vertex_to(mesh, xyz, vkey)

	def find_form(mesh):
	    vertices = [mesh.vertex_coordinates(vkey) for vkey in mesh.vertices()]
	    edges = list(mesh.edges())
	    fixed = mesh.vertices_on_boundary()
	    q = [1.0] * len(edges)
	    loads = [[0.0, 0.0, 50.0 / len(vertices)]] * len(vertices)
	    xyz, q, f, l, r = fd_numpy(vertices, edges, fixed, q, loads)
	    for vkey, coordinates in zip(mesh.vertices(), xyz):
	        mesh.vertex[vkey]['x'] = coordinates[0]
	        mesh.vertex[vkey]['y'] = coordinates[1]
	        mesh.vertex[vkey]['z'] = coordinates[2]

	def compute_load_path(mesh):
		return sum([mesh.edge_length(*edge) ** 2 for edge in mesh.edges()])

	def fit_function(code, **fkwargs):

		mesh = fkwargs['mesh']
		
		mesh_2 = mesh.copy()
		snake = Snake(mesh_2)
		snake.interpret(code)
		fix_boundaries(mesh_2)
		define_density(mesh_2, 500)
		fix_boundaries(mesh_2.get_quad_mesh())
		find_form(mesh_2.get_quad_mesh())

		return mesh_2, mesh_2.number_of_strips() #, compute_load_path(mesh_2.get_quad_mesh())

	vertices = [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 1.0, 0.0], [0.0, 1.0, 0.0]]
	faces = [[0, 1, 2, 3]]

	mesh = CoarseQuadMesh.from_vertices_and_faces(vertices, faces)
	mesh.collect_strips()

	meshes = []
	m = 12
	u = floor(m ** 0.5)
	for k in range(m):

		n = 10
		vector = [random.random() for i in range(n)]
		
		print('vector: ', vector)
		mesh_2, fit_value = fit_function(vector, **{'mesh': mesh})
		print()
		mesh_move_by(mesh_2.get_quad_mesh(), [25.0 * (k - k % u) / u, -25.0 * (k % u), 0.0])
		# for vkey in mesh_2.get_quad_mesh().vertices():
		# 	attr = mesh_2.get_quad_mesh().vertex[vkey]
		# 	attr['x'], attr['z'], attr['y'] = attr['x'], attr['y'], attr['z']
		#print(fit_value)
		meshes.append(mesh_2.get_quad_mesh())

	super_mesh = meshes_join(meshes)

	plotter = MeshPlotter(super_mesh, figsize = (5, 5))
	plotter.draw_vertices(radius = 0.01)
	plotter.draw_edges()
	plotter.draw_faces()
	plotter.show()

