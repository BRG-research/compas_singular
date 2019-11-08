from compas_pattern.datastructures.mesh_quad.grammar.add_strip import add_strip
from compas_pattern.datastructures.mesh_quad.grammar.delete_strip import delete_strip

__all__ = [
	'Walker'
]


class Walker:

	def __init__(self, mesh):
		self.mesh = mesh
		self.tail = None
		self.head = None
		self.polyedge = []
		self.added_polyedges = []
		self.delete_strips = []

	def reset(self):
		self.__init__(self.mesh)
		
	def start(self, tail=None, head=None):
			self.tail = self.mesh.vertices_on_boundary()[0] if tail is None else tail
			self.head = self.mesh.vertex_neighbors(self.tail)[0] if head is None else head

	def face_rotate(self, k=1):
		nbrs = self.mesh.vertex_neighbors(self.head, ordered=True)
		i = nbrs.index(self.tail)
		self.tail = self.head
		self.head = nbrs[i + k - len(nbrs)]
		if len(self.polyedge) != 0:
			self.polyedge.append(self.tail)

	def vertex_pivot(self, k=1):
		nbrs = self.mesh.vertex_neighbors(self.tail, ordered=True)
		i = nbrs.index(self.head)
		self.head = nbrs[i + k - len(nbrs)]

	def add_strip_toggle(self):
		if len(self.polyedge) == 0:
			self.polyedge.append(self.tail)
		else:
			self.added_polyedges.append(self.polyedge.copy())
			old_vkeys_to_new_vkeys = add_strip(self.mesh, self.polyedge)
			self.head = old_vkeys_to_new_vkeys[self.tail][0]
			self.tail = old_vkeys_to_new_vkeys[self.tail][1]
			self.polyedge = []

	def delete_strip(self):
		if len(self.polyedge) != 0:
			return
		mesh, tail, head = self.mesh, self.tail, self.head

		if mesh.halfedge[tail][head] is not None:
			fkey = mesh.halfedge[tail][head]
		else:
			fkey = mesh.halfedge[head][tail]
		next_head = mesh.face_vertex_ancestor(fkey, head)
	
		skey = mesh.edge_strip((tail, head))
		old_vkeys_to_new_vkeys = delete_strip(mesh, skey)
		self.tail = old_vkeys_to_new_vkeys[tail]
		self.head = old_vkeys_to_new_vkeys[next_head]
		self.delete_strips.append(skey)
		polyedge = [old_vkeys_to_new_vkeys.get(vkey, vkey) for vkey in self.polyedge]
		self.polyedge = []
		for vkey in polyedge:
			if len(self.polyedge) == 0 or self.polyedge[-1] != vkey:
				self.polyedge.append(vkey)

	def stop(self):
		add_strip(self.mesh, self. polyedge)
		self.added_polyedges.append(self.polyedge)
		self.polyedge = []

	def restart(self):
		self.tail, self.head = self.polyedge[:2]
		self.polyedge = self.polyedge[:1]

	def interpret_order(self, order):
		if order == 0:
			self.face_rotate()
		elif order == 1:
			self.vertex_pivot()
		elif order == 2:
			self.add_strip_toggle()
		elif order == 3:
			self.delete_strip()

	def interpret_orders(self, orders):
		for order in orders:
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

	import random as rd
	import compas
	from compas_pattern.datastructures.mesh_quad.mesh_quad import QuadMesh
	from compas.datastructures import mesh_smooth_centroid
	from compas_plotters.meshplotter import MeshPlotter

	mesh = QuadMesh.from_obj(compas.get('faces.obj'))
	mesh.collect_strips()
	walker = Walker(mesh)
	walker.start()
	orders = [2,0,2]
	#orders = [rd.randint(0,1) for _ in range(10)]
	#orders = [2] + orders + [2]
	#orders = [2, 1, 3, 0, 3, 2, 1, 3, 2, 2]
	print(orders)
	walker.interpret_orders(orders)
	print(walker.polyedge)
	print('added: ', walker.added_polyedges)
	print('deleted: ', walker.delete_strips)

	mesh_smooth_centroid(walker.mesh, kmax=1)

	plotter = MeshPlotter(walker.mesh)
	plotter.draw_vertices(radius=.1, text='key')
	plotter.draw_edges()
	plotter.draw_faces()
	plotter.show()

