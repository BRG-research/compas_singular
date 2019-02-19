import itertools

from compas.datastructures.mesh import Mesh

from compas.geometry import circle_from_points
from compas.geometry import circle_from_points_xy
from compas.geometry import angle_points
from compas.geometry import bestfit_plane

from compas.utilities import geometric_key
from compas.utilities import pairwise

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2017, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'

__all__ = [

]

class Mesh(Mesh):

	def __init__(self):
		super(Mesh, self).__init__()


	@classmethod
	def from_polylines(cls, boundary_polylines, other_polylines):
		"""Construct mesh from polylines.

		Based on construction from_lines,
		with removal of vertices that are not polyline extremities
		and of faces that represent boundaries.

		This specific method is useful to get the mesh connectivity from a set of (discretised) curves,
		that could overlap and yield a wrong connectivity if using from_lines based on the polyline extremities only.

		Parameters
		----------
		boundary_polylines : list
			List of polylines representing boundaries as lists of vertex coordinates.
		other_polylines : list
			List of the other polylines as lists of vertex coordinates.

		Returns
		-------
		Mesh
			A mesh object.
		"""

		corner_vertices = [geometric_key(xyz) for polyline in boundary_polylines + other_polylines for xyz in [polyline[0], polyline[-1]]]
		boundary_vertices = [geometric_key(xyz) for polyline in boundary_polylines for xyz in polyline]

		mesh = cls.from_lines([(u, v) for polyline in boundary_polylines + other_polylines for u, v in pairwise(polyline)])

		# remove the vertices that are not from the polyline extremities and the faces with all their vertices on the boundary
		vertex_keys = [vkey for vkey in mesh.vertices() if geometric_key(mesh.vertex_coordinates(vkey)) in corner_vertices]
		vertex_map = {vkey: i for i, vkey in enumerate(vertex_keys)}
		vertices = [mesh.vertex_coordinates(vkey) for vkey in vertex_keys]
		faces = [[vertex_map[vkey] for vkey in mesh.face_vertices(fkey) if geometric_key(mesh.vertex_coordinates(vkey)) in corner_vertices] for fkey in mesh.faces() if sum([geometric_key(mesh.vertex_coordinates(vkey)) not in boundary_vertices for vkey in mesh.face_vertices(fkey)])]

		mesh.cull_vertices()

		return cls.from_vertices_and_faces(vertices, faces)

	# --------------------------------------------------------------------------
	# global
	# --------------------------------------------------------------------------


	# --------------------------------------------------------------------------
	# local
	# --------------------------------------------------------------------------


	def delete_face(self, fkey):
		"""Delete a face from the mesh object.

		Parameters
		----------
		fkey : hashable
			The identifier of the face.

		Examples
		--------
		.. plot::
			:include-source:

			import compas
			from compas.datastructures import Mesh
			from compas.plotters import MeshPlotter

			mesh = Mesh.from_obj(compas.get('faces.obj'))

			mesh.delete_face(12)

			plotter = MeshPlotter(mesh)
			plotter.draw_vertices()
			plotter.draw_faces()
			plotter.show()

		"""

		for u, v in self.face_halfedges(fkey):
			self.halfedge[u][v] = None
			# additionnal check u in self.halfedge[v]
			if u in self.halfedge[v] and self.halfedge[v][u] is None:
				del self.halfedge[u][v]
				del self.halfedge[v][u]
		del self.face[fkey]

	def face_circle(self, fkey):
		"""Get data on circumcentre of triangular face.

		Parameters
		----------
		fkey : Key
			The face key.

		Returns
		-------
		list, None
			The centre coordinates, the radius value and the normal vector of the circle.
			None if the face is not a triangle

		"""

		face_vertices = self.face_vertices(fkey)

		# return None if not a triangle (possible improvement with best-fit circle)
		if len(face_vertices) != 3:
			return None
		
		a, b, c = face_vertices

		return circle_from_points(self.vertex_coordinates(a), self.vertex_coordinates(b), self.vertex_coordinates(c))

	def face_circle_xy(self, fkey):
		"""Get data on circumcentre of triangular face.

		Parameters
		----------
		fkey : Key
			The face key.

		Returns
		-------
		list, None
			The centre coordinates, the radius value and the normal vector of the circle.
			None if the face is not a triangle

		"""

		face_vertices = self.face_vertices(fkey)

		# return None if not a triangle (possible improvement with best-fit circle)
		if len(face_vertices) != 3:
			return None
		
		a, b, c = face_vertices

		return circle_from_points_xy(self.vertex_coordinates(a), self.vertex_coordinates(b), self.vertex_coordinates(c))

	# --------------------------------------------------------------------------
	# modifications
	# --------------------------------------------------------------------------

	def substitute_vertex_in_faces(self, old_vkey, new_vkey, fkeys):
		"""Substitute a vertex by another one in a given set of faces.

		Parameters
		----------
		old_vkey : hashable
			The old vertex key.
		new_vkey : hashable
			The new vertex key.
		fkeys : list
			List of face keys to modify

		"""

		for fkey in fkeys:
			face_vertices = [new_vkey if key == old_vkey else key for key in self.face_vertices(fkey)]
			self.delete_face(fkey)
			self.add_face(face_vertices, fkey)

	def insert_vertex_in_face(self, fkey, vkey_0, vkey):
		"""Insert a vertex in a face before a given vertex.

		Parameters
		----------
		fkey: hashable
			The face key.
		vkey_0: hashable
			The existing vertex key.
		vkey: hashable
			The vertex key to insert.

		"""
		face_vertices = self.face_vertices(fkey)[:]
		face_vertices.insert(face_vertices.index(vkey_0), vkey)
		self.delete_face(fkey)
		self.add_face(face_vertices, fkey)

	def open_boundary_polyedges_no_duplicates(self, fmax=None):
		"""All open polyedges from a boundary vertex to another one, without duplicate vertices.
		Optional maximum on the length (number of faces) of the added strip. 

		Parameters
		----------
		fmax : int, optional
			An optional maximum length (number of faces) on the length of the added strip.
			Default is None.
	
		Returns
		-------
		polyedges : list
			List of polyedges as tuples of vertices

		"""

		if fmax is None:
			fmax = self.number_of_vertices()

		polyedges = []

		for f in range(2, fmax + 1):
			for permutation in itertools.permutations(self.vertices(), f):
				if self.is_vertex_on_boundary(permutation[0]) and self.is_vertex_on_boundary(permutation[-1]):
					if all([v in self.halfedge[u] for u, v in pairwise(permutation)]):
						# avoid reversed polyedges
						if permutation[::-1] not in polyedges:
							polyedges.append(permutation)

		return polyedges


	def closed_polyedges_no_duplicates(self, fmax=None):
		"""All closed polyedges, without duplicate vertices.
		Optional maximum on the length (number of faces) of the added strip. 

		Parameters
		----------
		fmax : int, optional
			An optional maximum length (number of faces) on the length of the added strip.
			Default is None.

		Returns
		-------
		polyedges : list
			List of polyedges as tuples of vertices

		"""

		if fmax is None:
			fmax = self.number_of_vertices()

		polyedges = []

		for f in range(3, fmax + 1):
			for permutation in itertools.permutations(self.vertices(), f):
				if all([v in self.halfedge[u] for u, v in pairwise(permutation + permutation[: 1])]):
					# avoid redundant polyedges
					for i in range(f):
						offset_permutation = permutation[i :] + permutation[: i]
						if offset_permutation in polyedges or offset_permutation[::-1] in polyedges:
							break
						if i == f -1:
							polyedges.append(permutation)

		return polyedges


def mesh_substitute_vertex_in_faces(mesh, old_vkey, new_vkey, fkeys=None):
	"""Substitute in a mesh a vertex by another one.
	In all faces by default or in a given set of faces.

	Parameters
	----------
	old_vkey : hashable
		The old vertex key.
	new_vkey : hashable
		The new vertex key.
	fkeys : list, optional
		List of face keys where to subsitute the old vertex by the new one.
		Default is to subsitute in all faces.

	"""

	# apply to all faces if there is none chosen
	if fkeys is None:
		fkeys = mesh.faces()

	# substitute vertices
	for fkey in fkeys:
		face_vertices = [new_vkey if key == old_vkey else key for key in mesh.face_vertices(fkey)]
		mesh.delete_face(fkey)
		mesh.add_face(face_vertices, fkey)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	import compas

	mesh = Mesh.from_obj(compas.get('faces.obj'))

	#print len(mesh.open_boundary_polyedges_no_duplicates(fmax=4))
	print len(mesh.closed_polyedges_no_duplicates(fmax=4))

