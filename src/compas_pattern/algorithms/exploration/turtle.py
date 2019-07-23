from math import floor
from compas_pattern.datastructures.mesh_quad.grammar.add_strip import add_strip


__all__ = [
	'Turtle'
]


class Turtle:

	def __init__(self, mesh):
		self.mesh = mesh
		self.tail = None
		self.head = None
		self.polyedge = []
		self.added_polyedges = []

	def reset(self):
		self.__init__(self.mesh)
		
	def start(self, tail=None, head=None):
			self.tail = self.mesh.vertices_on_boundary()[0] if tail is None else tail
			self.head = self.mesh.vertex_neighbors(self.tail)[0] if head is None else head

	def forward(self, k=1):
		nbrs = self.mesh.vertex_neighbors(self.head, ordered=True)
		i = nbrs.index(self.tail)
		self. tail = self.head
		self.head = nbrs[i + k - len(nbrs)]
		if len(self.polyedge) != 0:
			self.polyedge.append(self.tail)

	def pivot(self, k=1):
		nbrs = self.mesh.vertex_neighbors(self.tail, ordered=True)
		i = nbrs.index(self.head)
		self.head = nbrs[i + k - len(nbrs)]

	def toggle(self):
		if len(self.polyedge) == 0:
			self.polyedge.append(self.tail)
		else:
			add_strip(self.mesh, self. polyedge)
			self.added_polyedges.append(self.polyedge)
			self.polyedge = []

	def stop(self):
		add_strip(self.mesh, self. polyedge)
		self.added_polyedges.append(self.polyedge)
		self.polyedge = []

	def restart(self):
		self.tail, self.head = self.polyedge[:2]
		self.polyedge = self.polyedge[:1]

	def interpret_order(self, order):
		if order == 0:
			self.forward()
		elif order == 1:
			self.pivot()
		elif order == 2:
			self.toggle()

	def interpret_path(self, path):
		for order in path:
			self.interpret_order(order)
		return self.mesh

	def is_polyedge_valid_for_strip_addition(self):
		# the polyedge must be at leat one edge long, and closed or have extremities on the boundary
		if len(self.polyedge) > 1:
			if self.polyedge[0] == self.polyedge [-1] or (self.mesh.is_vertex_on_boundary(self.polyedge[0]) and self.mesh.is_vertex_on_boundary(self.polyedge[-1])):
				return True
		return False


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	pass