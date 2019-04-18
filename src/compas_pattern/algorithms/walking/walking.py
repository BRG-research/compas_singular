from collections import deque

from compas_pattern.datastructures.mesh_quad.mesh_quad import QuadMesh
from compas_pattern.datastructures.mesh_quad.grammar_pattern import add_strip

from compas.utilities import pairwise

__all__ = [
	'Walker'
]


class Walker(QuadMesh):

	def __init__(self):
		super(Walker, self).__init__()
		self.position = None
		self.direction = None
		self.polyedge = None

	def start_walking(self):
		self.position = list(self.vertices())[0]
		self.direction = self.vertex_neighbors(self.position, ordered = True)[0]

	def forward(self):
		u, v = self.position, self.direction
		neighbors = self.vertex_neighbors(v, ordered = True)
		i = neighbors.index(u)
		w = neighbors[i + 1 - len(neighbors)]
		self.position, self.direction = v, w
		if self.polyedge:
			self.polyedge.append(self.position)

	def rotate(self):
		u, v = self.position, self.direction
		neighbors = self.vertex_neighbors(u, ordered = True)
		i = neighbors.index(v)
		w = neighbors[i + 1 - len(neighbors)]
		self.direction = w

	def start_polyedge(self):
		self.polyedge = [self.position]

	def end_polyedge(self):
		if not self.is_polyedge_valid_strip():
			print 'invalid polyedge for strip'
			return 0
		skey, left_polyedge, right_polyedge = add_strip(self, self.polyedge)
		self.position, self.direction = left_polyedge[-1], right_polyedge[-1]
		self.polyedge = None
		return skey

	def get_eligible_rules(self):

		eligible_rules = 'fr'

		if self.polyedge is None:
			eligible_rules += 's'

		if self.is_polyedge_valid_strip():
			eligible_rules += 'e'

		return eligible_rules

	def is_polyedge_valid_strip(self):

		# the polyedge must be non empty and have at least two vertices
		if self.polyedge is None or len(self.polyedge) < 2:
			return False

		# the polyedge must be closed or have extremities on the boundary
		if self.polyedge[0] == self.polyedge [-1] or (self.is_vertex_on_boundary(self.polyedge[0]) and self.is_vertex_on_boundary(self.polyedge[-1])):
			occurences = [self.polyedge.count(i) for i in self.polyedge]
			if self.polyedge[0] == self.polyedge [-1]:
				occurences = occurences[1 : -1]
			# the polyedge can not have multiple vertex occurences (except for the extremities if the polyedge is closed)
			if not sum([i > 1 for i in occurences]):
				return True

		return False

	def apply_rules(self, string):
		rules = deque(string)
		while rules:
			rule = rules.popleft()
			if rule == 'f':
				self.forward()
			elif rule == 'r':
				self.rotate()
			elif rule == 's':
				self.start_polyedge()
			elif rule == 'e':
				self.end_polyedge()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	import compas
	from compas.datastructures import mesh_unify_cycles
	from compas.plotters import MeshPlotter

	vertices = [
		[0.0, 0.0, 0.0],
		[1.0, 0.0, 0.0],
		[1.0, 1.0, 0.0],
		[0.0, 1.0, 0.0],
	]

	faces = [
		[0, 1, 2, 3]
	]

	walker = Walker.from_vertices_and_faces(vertices, faces)
	walker.collect_strips()
	mesh_unify_cycles(walker)

	walker.start_walking()
	#print walker.position, walker.direction
	
	#walker.apply_rules('sffe')
	walker.apply_rules('fsffesfrfffe')

	plotter = MeshPlotter(walker, figsize = (5, 5))
	plotter.draw_vertices(radius = 0.01)
	plotter.draw_edges()
	plotter.draw_faces()
	plotter.show()
