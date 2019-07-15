from compas_pattern.datastructures.mesh_quad_coarse.mesh_quad_coarse import CoarseQuadMesh
from compas_pattern.datastructures.mesh_quad_pseudo.mesh_quad_pseudo import PseudoQuadMesh

from compas.geometry import discrete_coons_patch
from compas.datastructures.mesh import meshes_join_and_weld

from compas.utilities import geometric_key
from compas.utilities import pairwise


__all__ = [	'CoarsePseudoQuadMesh']


class CoarsePseudoQuadMesh(PseudoQuadMesh, CoarseQuadMesh):

	def __init__(self):
		super(CoarsePseudoQuadMesh, self).__init__()

	
	def densification(self):
		"""Generate a denser quad mesh from the coarse quad mesh and its strip densities.

		Returns
		-------
		QuadMesh
			A denser quad mesh.

		"""

		pole_map = tuple([geometric_key(self.vertex_coordinates(pole)) for pole in self.poles()])

		meshes = []
		for fkey in self.faces():
			polylines = [[self.edge_point(u, v, float(i) / float(self.get_strip_density(self.edge_strip((u, v))))) for i in range(0, self.get_strip_density(self.edge_strip((u, v))) + 1)] for u, v in self.face_halfedges(fkey)]
			if self.is_face_pseudo_quad(fkey):
				pole = self.data['attributes']['face_pole'][fkey]
				idx = self.face_vertices(fkey).index(pole)
				polylines.insert(idx, None)
			ab, bc, cd, da = polylines
			if cd is not None:
				dc = list(reversed(cd))
			else:
				dc = None
			if da is not None:
				ad = list(reversed(da))
			else:
				ad = None
			vertices, faces = discrete_coons_patch(ab, bc, dc, ad)
			faces = [[u for u, v in pairwise(face + face[:1]) if u != v] for face in faces]
			mesh = PseudoQuadMesh.from_vertices_and_faces_with_face_poles(vertices, faces)
			meshes.append(mesh)
		
		face_pole_map = {}
		for mesh in meshes:
			for fkey in mesh.faces():
				for u, v in pairwise(mesh.face_vertices(fkey) + mesh.face_vertices(fkey)[: 1]):
					if geometric_key(mesh.vertex_coordinates(u)) in pole_map and geometric_key(mesh.vertex_coordinates(u)) == geometric_key(mesh.vertex_coordinates(v)):
						face_pole_map[geometric_key(mesh.face_center(fkey))] = geometric_key(mesh.vertex_coordinates(u))
						break

		self.set_quad_mesh(meshes_join_and_weld(meshes))

		face_pole = {}
		for fkey in self.get_quad_mesh().faces():
			if geometric_key(self.get_quad_mesh().face_center(fkey)) in face_pole_map:
				for vkey in self.get_quad_mesh().face_vertices(fkey):
					if geometric_key(self.get_quad_mesh().vertex_coordinates(vkey)) == face_pole_map[geometric_key(self.get_quad_mesh().face_center(fkey))]:
						face_pole[fkey] = vkey
						break
		self.get_quad_mesh().data['attributes']['face_pole'] = face_pole
		return self.get_quad_mesh()
	

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	import compas
