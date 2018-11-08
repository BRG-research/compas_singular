from math import floor
from operator import itemgetter

from compas_pattern.geometry.skeleton import Skeleton

from compas_pattern.datastructures.mesh import Mesh

from compas_pattern.geometry.utilities import polyline_point

from compas.utilities import geometric_key
from compas_pattern.utilities.lists import splits_closed_list

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2018, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'

__all__ = [
	'SkeletonMesh',
]

class SkeletonMesh(Skeleton):
	"""SkeletonMesh class for the generate a coarse quad mesh based on a topological skeleton and its singularities.

	References
	----------
	.. [1] Oval et al. 2018. *Topology finding of patterns for shell structures*.
		   Submitted for publication in Automation in Construction.

	"""

	def __init__(self):
		super(SkeletonMesh, self).__init__()
		self.mesh = None

	# --------------------------------------------------------------------------
	# key elements
	# --------------------------------------------------------------------------
	
	def corner_faces(self):
		# one-neighbour faces
		return [fkey for fkey in self.faces() if len(self.face_neighbors(fkey)) == 1]

	def corner_vertices(self):
		# two-valent boundary vertices
		return [vkey for vkey in self.vertices_on_boundary() if len(self.vertex_neighbors(vkey)) == 2]

	def split_vertices(self):
		# vertices of three-neighbour faces
		return [vkey for fkey in self.singular_faces() for vkey in self.face_vertices(fkey)]

	# --------------------------------------------------------------------------
	# branches
	# --------------------------------------------------------------------------

	def branches_singularity_to_singularity(self):
		# branches between singularities (= topological skeleton - branches between singularities and corners)
		map_corners = [geometric_key(self.face_circle(corner)[0]) for corner in self.corner_faces()]
		return [branch for branch in self.branches() if geometric_key(branch[0]) not in map_corners and geometric_key(branch[-1]) not in map_corners]

	def branches_singularity_to_boundary(self):
		# branches between singularities and the vertices of the corresponding face
		return [[self.face_circle(fkey)[0], self.vertex_coordinates(vkey)] for fkey in self.singular_faces() for vkey in self.face_vertices(fkey)]

	def branches_boundary(self):
		# branches along boundaries split by the corner vertices and the split vertices
		boundaries = self.boundary_polyedges()
		splits = self.corner_vertices() + self.split_vertices()
		split_boundaries = [split_boundary for boundary in boundaries for split_boundary in splits_closed_list(boundary, [boundary.index(split) for split in splits if split in boundary])]
		return [[self.vertex_coordinates(vkey) for vkey in boundary] for boundary in split_boundaries]

	def branches_split(self):
		
		face_splits = []
		singular_faces = self.singular_faces()

		for polyedge in self.boundary_polyedges():
			sorted_boundary_faces = list(set([fkey for vkey in reversed(polyedge) for fkey in self.vertex_faces(vkey, ordered = True)]))
			singular_boundary_faces = [fkey for fkey in sorted_boundary_faces if fkey in singular_faces]

			if len(singular_boundary_faces) < 3:
				n = len(singular_boundary_faces)

				if len(singular_boundary_faces) == 0:
					face_splits += list(itemgetter(0, int(floor(n / 3)), int(floor(n * 2 / 3))), singular_boundary_faces)
				
				elif len(singular_boundary_faces) == 1:
					i = sorted_boundary_faces.index(singular_boundary_faces[0])
					face_splits += list(itemgetter(i - int(floor(n * 2 / 3)), i - int(floor(n / 3)), 0), singular_boundary_faces)
				
				else:
					one, two = splits_closed_list(sorted_boundary_faces, [sorted_boundary_faces.index(fkey) for fkey in singular_boundary_faces])
					split_half = one if len(one) > len(two) else two
					face_splits.append(split_half[int(floor(len(split_half) / 2))])

		branch_splits = []
		for fkey in face_splits:
			for edge in self.face_halfedges(fkey):
				if not self.is_edge_on_boundary(*edge):
					branch_splits += [(self.face_circle(fkey[0]), self.vertex_coordinates(vkey)) for vkey in edge]
					break
					
		return branch_splits

	# --------------------------------------------------------------------------
	# decomposition
	# --------------------------------------------------------------------------
	
	def decomposition_polylines(self):
		# polyline branches from skeleton-based decomposition into quad patches
		return self.branches_singularity_to_singularity() + self.branches_singularity_to_boundary() + self.branches_boundary()

	def decomposition_polyline(self, geom_key_1, geom_key_2):
		# polyline branch from two extremity geoemtric keys
		polylines = {(geometric_key(polyline[0]), geometric_key(polyline[-1])): polyline for polyline in self.decomposition_polylines()}
		return polylines.get((geom_key_1, geom_key_2), polylines.get((geom_key_2, geom_key_1)))


	def decomposition_mesh(self):
		# mesh from skeleton-based decomposition into quad patches
		self.mesh =  Mesh.from_polylines(self.branches_boundary(), self.branches_singularity_to_singularity() + self.branches_singularity_to_boundary())
		self.solve_triangular_faces()
		self.solve_flipped_faces()
		return self.mesh

	def solve_triangular_faces(self):

		mesh = self.mesh

		for fkey in list(mesh.faces()):
			if len(mesh.face_vertices(fkey)) == 3:
				
				boundary_vertices = [vkey for vkey in mesh.face_vertices(fkey) if mesh.is_vertex_on_boundary(vkey)]
				test = sum(mesh.is_vertex_on_boundary(vkey) for vkey in mesh.face_vertices(fkey))

				if test == 1:
					# convert triangular face to quad by duplicating the boundary vertex
					# due to singular face vertices at the same location
					u = boundary_vertices[0]
					v = mesh.add_vertex(attr_dict = {attr: xyz for attr, xyz in zip(['x', 'y', 'z'], mesh.vertex_coordinates(u))})
					
					# modify adjacent faces
					vertex_faces = mesh.vertex_faces(u, ordered = True)
					mesh.substitute_vertex_in_faces(u, v, vertex_faces[: vertex_faces.index(fkey)])

					# modify triangular face
					mesh.insert_vertex_in_face(fkey, u, v)

				elif test == 2:
					# remove triangular face and merge the two boundary vertices
					# due to singularities at the same location
					polyline = self.decomposition_polyline(*map(lambda x: geometric_key(mesh.vertex_coordinates(x)), boundary_vertices))
					point = polyline_point(polyline, t = .5, snap = True)
					new_vkey = mesh.add_vertex(attr_dict = {'x': point.x, 'y': point.y , 'z': point.z})
					
					# modify triangular face
					mesh.delete_face(fkey)
					
					# modify adjacent faces
					for old_vkey in boundary_vertices:
						mesh.substitute_vertex_in_faces(old_vkey, new_vkey, mesh.vertex_faces(old_vkey))
						mesh.delete_vertex(old_vkey)

		def solve_flipped_faces(self):

			mesh = self.mesh


		return mesh

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	import compas
