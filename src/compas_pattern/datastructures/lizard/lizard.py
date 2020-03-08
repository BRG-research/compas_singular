from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas_pattern.datastructures.mesh_quad.mesh_quad import QuadMesh
from compas_pattern.datastructures.mesh_quad.grammar.add_strip import add_strip
from compas_pattern.datastructures.mesh_quad.grammar.delete_strip import delete_strip

__all__ = ['Lizard']



class Lizard(QuadMesh):

	def __init__(self, mesh):
		super(Lizard, self).__init__()
		self.tail = None
		self.head = None
		self.full_tail = None

	def set_head_and_tail(self, tail=None, head=None):
		if tail in self.vertex and head in self.vertex and tail in self.vertex[head]:
			self.tail, self.head = tail, head
		else:
			self.tail, self.head = self.mesh.vertices_on_boundary()[0], self.mesh.vertex_neighbors(self.tail)[0]

	def face_turn(self, k=1):
		nbrs = self.mesh.vertex_neighbors(self.head, ordered=True)
		i = nbrs.index(self.tail)
		self.tail = self.head
		self.head = nbrs[i + k - len(nbrs)]
		if self.full_tail is not None:
			self.full_tail.append(self.tail)
			

	def vertex_pivot(self, k=1):
		nbrs = self.mesh.vertex_neighbors(self.tail, ordered=True)
		i = nbrs.index(self.head)
		self.head = nbrs[i + k - len(nbrs)]

	def add(lizard):
		if self.full_tail is None:
			self.full_tail = [self.tail]
		else:
			self.full_tail = None

def add_strip_lizard(lizard):
	if len(self.polyedge) == 0:
		self.polyedge.append(self.tail)
	else:
		self.added_polyedges.append(self.polyedge.copy())
		old_vkeys_to_new_vkeys = add_strip(self.mesh, self.polyedge)
		self.head = old_vkeys_to_new_vkeys[self.tail][0]
		self.tail = old_vkeys_to_new_vkeys[self.tail][1]
		self.polyedge = []

def delete_strip_lizard(lizard):
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

