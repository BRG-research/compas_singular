from collections import deque

from compas_pattern.datastructures.mesh_quad.mesh_quad import QuadMesh
from compas_pattern.datastructures.mesh_quad.grammar_pattern import add_strip
from compas_pattern.datastructures.mesh_quad.grammar_pattern import delete_strip

__all__ = [
	'Formal'
]

class Formal:

	def __init__(self, quad_mesh):
		self.quad_mesh = quad_mesh

		self.tail = None
		self.head = None

		self.collect_polyedge = False
		self.polyedge = []

	def start(self):
		self.tail = list(self.quad_mesh.vertices())[0]
		self.head = self.quad_mesh.vertex_neighbors(self.tail, ordered = True)[0]

	def interpret(self, string):
		rules = deque(string)
		while rules:
			rule = rules.popleft()
			#print(rule)
			if rule == 'r':
				self.move_right()
			elif rule == 'l':
				self.move_left()
			elif rule == '+':
				out = self.addition()
				if out == 'no':
					return 'no'
			elif rule == '-':
				self.deletion()

	def move_right(self):
		u, v = self.tail, self.head
		#print(u, v, self.quad_mesh.number_of_vertices())
		neighbors = self.quad_mesh.vertex_neighbors(v, ordered = True)
		i = neighbors.index(u)
		w = neighbors[i + 1 - len(neighbors)]
		self.tail, self.head = v, w
		if self.collect_polyedge:
			self.polyedge.append(self.tail)

	def move_left(self):
		u, v = self.tail, self.head
		#print(u, v, self.quad_mesh.number_of_vertices())
		neighbors = self.quad_mesh.vertex_neighbors(u, ordered = True)
		i = neighbors.index(v)
		w = neighbors[i + 1 - len(neighbors)]
		self.head = w

	def addition(self):
		if self.collect_polyedge:
			if self.is_polyedge_valid_for_strip_addition():
				if all([self.polyedge.count(vkey) == 1 for vkey in self.polyedge[1:-1]]) and not(self.polyedge[0] == self.polyedge[-1] and len(self.polyedge) <= 3):
					skey, left_polyedge, right_polyedge = add_strip(self.quad_mesh, self.polyedge)
					self.tail, self.head = left_polyedge[-1], right_polyedge[-1]
				else:
					print('not implemented')
					return 'no'
			self.polyedge = []
		else:
			self.polyedge = [self.tail]

		self.collect_polyedge = bool(1 - self.collect_polyedge)

	def is_polyedge_valid_for_strip_addition(self):
		# the polyedge must be at leat one edge long, and closed or have extremities on the boundary
		if len(self.polyedge) > 1:
			if self.polyedge[0] == self.polyedge [-1] or (self.quad_mesh.is_vertex_on_boundary(self.polyedge[0]) and self.quad_mesh.is_vertex_on_boundary(self.polyedge[-1])):
				return True
		return False

	def deletion(self):
		if not self.collect_polyedge:
			copy_mesh = self.quad_mesh.copy()
			skey = copy_mesh.edge_strip((self.tail, self.head))
			old_vkeys_to_new_vkeys = delete_strip(copy_mesh, skey, preserve_boundaries=True)
			if copy_mesh.number_of_faces() > 0 and len(copy_mesh.boundaries()) != len(self.quad_mesh.boundaries()) or copy_mesh.genus() != self.quad_mesh.genus():
				self.quad_mesh = copy_mesh
				u, v = self.tail, self.head
				self.move_left()
				if self.tail in old_vkeys_to_new_vkeys:
					self.tail = old_vkeys_to_new_vkeys[self.tail]
				if self.head in old_vkeys_to_new_vkeys:
					self.head = old_vkeys_to_new_vkeys[self.head]


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	import compas
	from random import randint
	from math import pi
	from compas_pattern.datastructures.mesh_quad_coarse.mesh_quad_coarse import CoarseQuadMesh
	from compas_pattern.algorithms.formal_system.formal_system import Formal
	from compas.geometry.analytical import circle_evaluate
	from compas_pattern.datastructures.mesh.operations import mesh_move_vertex_to
	from compas.datastructures import mesh_smooth_centroid
	from compas.datastructures import mesh_smooth_area
	from compas.numerical import fd_numpy
	from compas.numerical import ga
	from compas_plotters.meshplotter import MeshPlotter
	from compas_plotters.gaplotter import visualize_evolution

	def encode(code):
		encoded = []
		for x in code:
			if x == 'r':
				encoded.append(0.0)
			elif x == 'l':
				encoded.append(1.0)
			elif x == '+':
				encoded.append(2.0)
			elif x == '-':
				encoded.append(3.0)
		return encoded

	def decode(code):
		decoded = ''
		for x in code:
			if x == 0.0:
				decoded += 'r'
			elif x == 1.0:
				decoded += 'l'
			elif x == 2.0:
				decoded += '+'
			elif x == 3.0:
				decoded += '-'
		return decoded

	def define_density(mesh):
		mesh.set_strips_density(1)
		mesh.set_mesh_density_face_target(500)
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
	    #vertex_areas = [mesh.vertex_area(vkey) for vkey in mesh.vertices()]
	    #load = 1000
	    #loads = [[0.0, 0.0, load * mesh.vertex_area(vkey) / mesh.area()] for vkey in mesh.vertices()]
	    xyz, q, f, l, r = fd_numpy(vertices, edges, fixed, q, loads)
	    for vkey, coordinates in zip(mesh.vertices(), xyz):
	        mesh.vertex[vkey]['x'] = coordinates[0]
	        mesh.vertex[vkey]['y'] = coordinates[1]
	        mesh.vertex[vkey]['z'] = coordinates[2]

	def compute_load_path(mesh):
		return sum([mesh.edge_length(*edge) ** 2 for edge in mesh.edges()])

	def fit_function(code, **fkwargs):

		mesh = fkwargs['mesh']
		
		print(code)
		decoded = decode(code)
		print(decoded)
		mesh_2 = mesh.copy()
		formal = Formal(mesh_2)
		formal.start()
		formal.interpret(decoded)
		
		#define_density(mesh_2)
		#fix_boundaries(mesh_2.get_quad_mesh())
		#mesh_smooth_centroid(mesh_2.get_quad_mesh(), fixed=mesh_2.get_quad_mesh().vertices_on_boundary(), kmax=100, damping=0.5)
		#mesh_smooth_area(mesh_2.get_quad_mesh(), fixed=mesh_2.get_quad_mesh().vertices_on_boundary(), kmax=100, damping=0.5)
		#find_form(mesh_2.get_quad_mesh())

		return mesh_2, mesh_2.number_of_strips() #, compute_load_path(mesh_2.get_quad_mesh())

	vertices = [
		[0.0, 0.0, 0.0],
		[1.0, 0.0, 0.0],
		[1.0, 1.0, 0.0],
		[0.0, 1.0, 0.0],
	]

	faces = [
		[0, 1, 2, 3]
	]

	mesh = CoarseQuadMesh.from_vertices_and_faces(vertices, faces)

	#mesh = CoarseQuadMesh.from_obj(compas.get('faces.obj'))

	mesh.collect_strips()

	# encode = Formal(mesh)
	# encode.start()
	# encode.interpret('rlltltrrtlrrrtrtttrttrtrlrlrrr')

	# rrl+++++rrrlll+llrll
	# r+l+lrr+++ll+r++rrl+
	# l+l+llrlrrllllrlrrlr

	code = [2.0, 0.0, 2.0, 2.0, 0.0, 2.0, 2.0, 0.0, 2.0, 2.0, 0.0, 2.0, 2.0, 0.0, 2.0, 2.0, 0.0, 2.0, 2.0, 0.0, 2.0, 2.0, 0.0, 2.0]
	print(len(code))
	mesh_2, fit_value = fit_function(encode('l+l+llrlrrllllrlrrlr'), **{'mesh': mesh})
	print(fit_value)

	# for vkey in mesh_2.get_quad_mesh().vertices():
	# 	attr = mesh_2.get_quad_mesh().vertex[vkey]
	# 	attr['x'], attr['z'], attr['y'] = attr['x'], attr['y'], attr['z']

	plotter = MeshPlotter(mesh_2, figsize = (5, 5))
	plotter.draw_vertices(radius = 0.01)
	plotter.draw_edges()
	plotter.draw_faces()
	plotter.show()


