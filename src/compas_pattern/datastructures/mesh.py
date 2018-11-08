from compas.datastructures.mesh import Mesh

from compas.geometry import circle_from_points

from compas.topology import mesh_unify_cycles

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

	def is_mesh_empty(self):
		"""Boolean whether the mesh is empty.

		Parameters
		----------

		Returns
		-------
		bool
			True if no vertices. False otherwise.
		"""

		if self.number_of_vertices() == 0:
			return True

		return False

	def mesh_euler(self):
		"""Calculate the Euler characterisic.

		Parameters
		----------

		Returns
		-------
		int
			The Euler chracteristic.
		"""

		V = len([vkey for vkey in self.vertices() if len(self.vertex_neighbours(vkey)) != 0])
		E = self.number_of_edges()
		F = self.number_of_faces()
		
		return V - E + F

	def mesh_genus(self):
		"""Calculate the genus.

		Parameters
		----------

		Returns
		-------
		int
			The genus.

		 References
		----------
		.. [1] Wolfram MathWorld. *Genus*.
			   Available at: http://mathworld.wolfram.com/Genus.html.

		"""

		X = self.mesh_euler()

		# each boundary must be taken into account as if it was one face
		B = len(self.boundary_polyedges())
		
		if mesh.is_orientable:
			return (2 - (X + B)) / 2
		else:
			return 2 - (X + B)

	def mesh_area(self):
		"""Calculate the total mesh area.

		Parameters
		----------

		Returns
		-------
		float
			The area.
		"""

		return sum([self.face_area(fkey) for fkey in self.faces()])

	def mesh_centroid(self):
		"""Calculate the mesh centroid.

		Parameters
		----------

		Returns
		-------
		list
			The coordinates of the mesh centroid.
		"""

		return scale_vector(1. / self.mesh_area(), add_vectors([scale_vector(self.face_area(fkey), self.face_centroid(fkey)) for fkey in mesh.faces()]))

	def mesh_normal(self):
		"""Calculate the average mesh normal.

		Parameters
		----------

		Returns
		-------
		list
			The coordinates of the mesh normal.
		"""

		return scale_vector(1. / self.mesh_area(), add_vectors([scale_vector(self.face_area(fkey), self.face_normal(fkey)) for fkey in mesh.faces()]))

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

	def face_adjacency_vertices(self, f1, f2):
		"""Find the vertices over which two faces are adjacent.

		Parameters
		----------
		f1 : hashable
			The identifier of the first face.
		f2 : hashable
			The identifier of the second face.

		Returns
		-------
		list
			The vertices separating face 1 from face 2.
		"""

		return [vkey for vkey in self.face_vertices(f1) if vkey in self.face_vertices(f2)]

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

	def edges_on_boundary(self, oriented = True):
		"""Find the edges on the boundary.

		Parameters
		----------
		oriented : bool
			Boolean whether the boundary edges should point outwards.

		Returns
		-------
		boundary_edges : list
			The boundary edges.

		"""

		boundary_edges =  [(u, v) for u, v in self.edges() if self.is_edge_on_boundary(u, v)]
		
		if not oriented:
			return boundary_edges

		else:
			return [(v, u) if self.halfedge[u][v] is not None else (u, v) for u, v in boundary_edges]

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

	# --------------------------------------------------------------------------
	# advanced
	# --------------------------------------------------------------------------

	def boundary_polyedges(self):
		"""Collect the mesh boundaries as lists of vertices.
		The polyedge is closed but the first and last item are not the same!

		Parameters
		----------
		mesh : Mesh
			Mesh.

		Returns
		-------
		boundaries : list
			List of boundaries as lists of vertex keys.

		"""

		boundaries = []

		# get all boundary edges pointing outwards
		boundary_edges = {u: v for u, v in self.edges_on_boundary()}

		# start new boundary
		while len(boundary_edges) > 0:
			boundary = list(boundary_edges.popitem())

			# get consecuvite vertex until the boundary is closed
			while boundary[0] != boundary[-1]:
				boundary.append(boundary_edges[boundary[-1]])
				boundary_edges.pop(boundary[-2])

			boundaries.append(boundary[: -1])
		
		return boundaries

def add_vertex_from_vertices(mesh, vertices, weights):
	n = len(vertices)
	if len(weights) != n:
		weights = [1] * n
	x, y, z = 0, 0, 0
	for i, vkey in enumerate(vertices):
		xyz = mesh.vertex_coordinates(vkey)
		x += xyz[0] * weights[i]
		y += xyz[1] * weights[i]
		z += xyz[2] * weights[i]
	sum_weights = sum(weights)
	x /= sum_weights
	y /= sum_weights
	z /= sum_weights

	return mesh.add_vertex(attr_dict = {'x': x, 'y': y, 'z': z})

def insert_vertices_in_halfedge(mesh, u, v, vertices):
	if v in mesh.halfedge[u] and mesh.halfedge[u][v] is not None:
		fkey = mesh.halfedge[u][v]
		return insert_vertices_in_face(mesh, fkey, u, vertices)
	else:
		return 0


def insert_vertex_in_face(mesh, fkey, vkey, added_vkey):
	"""Insert a vertex in the vertices of a face after a vertex.

	Parameters
	----------
	mesh : Mesh
		A mesh.
	fkey: int
		Face key.
	vkey: int
		Vertex key to insert.
	added_vkey: int
		Vertex key to insert after the existing vertex.

	Returns
	-------
	face_vertices: list or None
		New list of face vertices.
		None if vkey is not a vertex of the face.

	Raises
	------
	-

	"""

	if vkey not in mesh.face_vertices(fkey):
		return None

	face_vertices = mesh.face_vertices(fkey)[:]
	idx = face_vertices.index(vkey) + 1 - len(face_vertices)
	face_vertices.insert(idx, added_vkey)
	mesh.delete_face(fkey)
	mesh.add_face(face_vertices, fkey = fkey)

	return face_vertices

def insert_vertices_in_face(mesh, fkey, vkey, added_vkeys):
	"""Insert vertices in the vertices of a face after a vertex.

	Parameters
	----------
	mesh : Mesh
		A mesh.
	fkey: int
		Face key.
	vkeys: int
		Vertex key to insert.
	added_vkey: list
		List of vertex keys to insert after the existing vertex.

	Returns
	-------
	face_vertices: list or None
		New list of face vertices.
		None if vkey is not a vertex of the face.

	Raises
	------
	-

	"""

	if vkey not in mesh.face_vertices(fkey):
		return None

	face_vertices = mesh.face_vertices(fkey)[:]
	for added_vkey in reversed(added_vkeys):
		idx = face_vertices.index(vkey) + 1 - len(face_vertices)
		face_vertices.insert(idx, added_vkey)
	mesh.delete_face(fkey)
	mesh.add_face(face_vertices, fkey = fkey)

	return face_vertices

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	import compas

	mesh = Mesh.from_obj(compas.get('faces.obj'))

	#mesh.delete_face(13)
