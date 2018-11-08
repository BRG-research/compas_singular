from math import floor
from operator import itemgetter

from compas_pattern.geometry.skeleton import Skeleton

from compas_pattern.datastructures.mesh import Mesh

from compas_pattern.geometry.utilities import polyline_point
from compas_pattern.geometry.join import join_polylines

from compas.utilities import geometric_key
from compas.utilities import pairwise
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
		self.polylines = None

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
		boundaries = [polyedge + polyedge[0 :] for polyedge in self.boundary_polyedges()]
		splits = self.corner_vertices() + self.split_vertices()
		split_boundaries = [split_boundary for boundary in boundaries for split_boundary in splits_closed_list(boundary, [boundary.index(split) for split in splits if split in boundary])]
		return [[self.vertex_coordinates(vkey) for vkey in boundary] for boundary in split_boundaries]

	def branches_splitting_collapsed_boundaries(self):
		
		new_branches = []

		all_splits = set(list(self.corner_vertices()) + list(self.split_vertices()))

		for polyedge in self.boundary_polyedges():

			splits = [vkey for vkey in polyedge if vkey in all_splits]
			new_splits = []

			if len(splits) == 0:
				new_splits += [vkey for vkey in list(itemgetter(0, int(floor(len(polyedge) / 3)), int(floor(len(polyedge) * 2 / 3)))(polyedge))]
			
			elif len(splits) == 1:
				i = polyedge.index(splits[0])
				new_splits += list(itemgetter(i - int(floor(len(polyedge) * 2 / 3)), i - int(floor(len(polyedge) / 3)))(polyedge))
			
			elif len(splits) == 2:
				one, two = splits_closed_list(polyedge, [polyedge.index(vkey) for vkey in splits])
				half = one if len(one) > len(two) else two
				new_splits.append(half[int(floor(len(half) / 2))])

			for vkey in new_splits:
				fkey = list(self.vertex_faces(vkey))[0]
				for edge in self.face_halfedges(fkey):
					if vkey in edge and not self.is_edge_on_boundary(*edge):
						new_branches += [[self.face_circle(fkey)[0], self.vertex_coordinates(vkey_2)] for vkey_2 in edge]
						all_splits.update(edge)
						break

		return new_branches

	def branches_splitting_flipped_faces(self):
		return 0

	# --------------------------------------------------------------------------
	# decomposition
	# --------------------------------------------------------------------------
	
	def decomposition_polylines(self):
		# store all polyline branches from skeleton-based decomposition into quad patches
		self.polylines =  join_polylines(self.branches_singularity_to_singularity() + self.branches_singularity_to_boundary() + self.branches_boundary() + self.branches_splitting_collapsed_boundaries(), stops = [self.vertex_coordinates(vkey) for vkey in self.corner_vertices()])
		return self.polylines

	def decomposition_polyline(self, geom_key_1, geom_key_2):
		# polyline branch from two extremity geometric keys
		polylines = {(geometric_key(polyline[0]), geometric_key(polyline[-1])): polyline for polyline in self.polylines}
		return polylines.get((geom_key_1, geom_key_2), polylines.get((geom_key_2, geom_key_1)))

	def decomposition_mesh(self):
		# mesh from skeleton-based decomposition into quad patches
		polylines = self.decomposition_polylines()
		boundary_keys = set([geometric_key(self.vertex_coordinates(vkey)) for vkey in self.vertices_on_boundary()])
		boundary_polylines = [polyline for polyline in polylines if geometric_key(polyline[0]) in boundary_keys and geometric_key(polyline[1]) in boundary_keys ]
		other_polylines = [polyline for polyline in polylines if geometric_key(polyline[0]) not in boundary_keys or geometric_key(polyline[1]) not in boundary_keys]
		
		self.mesh =  Mesh.from_polylines(boundary_polylines, other_polylines)
		
		self.solve_triangular_faces()
		self.solve_flipped_faces()
		
		return self.mesh

	def solve_triangular_faces(self):

		mesh = self.mesh

		for fkey in list(mesh.faces()):
			if len(mesh.face_vertices(fkey)) == 3:
				
				boundary_vertices = [vkey for vkey in mesh.face_vertices(fkey) if mesh.is_vertex_on_boundary(vkey)]
				case = sum(mesh.is_vertex_on_boundary(vkey) for vkey in mesh.face_vertices(fkey))

				if case == 1:
					# convert triangular face to quad by duplicating the boundary vertex
					# due to singular face vertices at the same location
					u = boundary_vertices[0]
					v = mesh.add_vertex(attr_dict = {attr: xyz for attr, xyz in zip(['x', 'y', 'z'], mesh.vertex_coordinates(u))})
					
					# modify adjacent faces
					vertex_faces = mesh.vertex_faces(u, ordered = True)
					mesh.substitute_vertex_in_faces(u, v, vertex_faces[: vertex_faces.index(fkey)])

					# modify triangular face
					mesh.insert_vertex_in_face(fkey, u, v)

				elif case == 2:
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
