from compas.datastructures.mesh import Mesh

from compas.geometry import circle_from_points
from compas.geometry import angle_points
from compas.geometry import bestfit_plane

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
	def from_vertices_and_faces(cls, vertices, faces):
		"""Construct a mesh object from a list of vertices and faces.

		Parameters
		----------
		vertices : list, dict
			A list of vertices, represented by their XYZ coordinates, or a dictionary of vertex keys pointing to their XYZ coordinates.
		faces : list, dict
			A list of faces, represented by a list of indices referencing the list of vertex coordinates, or a dictionary of face keys pointing to a list of indices referencing the list of vertex coordinates.

		Returns
		-------
		Mesh
			A mesh object.

		Examples
		--------
		.. code-block:: python

			import compas
			from compas.datastructures import Mesh

			vertices = [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 1.0, 0.0]]
			faces = [[0, 1, 2]]

			mesh = Mesh.from_vertices_and_faces(vertices, faces)

		"""
		mesh = cls()

		if type(vertices) == list:
			for x, y, z in iter(vertices):
				mesh.add_vertex(x=x, y=y, z=z)
		elif type(vertices) == dict:
			for key, xyz in vertices.items():
				mesh.add_vertex(key = key, attr_dict = {i: j for i, j in zip(['x', 'y', 'z'], xyz)})
		
		if type(faces) == list:
			for face in iter(faces):
				mesh.add_face(face)
		elif type(faces) == dict:
			for fkey, vertices in faces.items():
				mesh.add_face(vertices, fkey)

		return mesh

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

	def vertex_valency(self, vkey):
		"""Valency of a vertex, i.e. number of adjacent vertices.

		Parameters
		----------
		vkey : hashable
			The vertex key.

		Returns
		-------
		int
			The valency.
		"""

		return len(self.vertex_neighbors(vkey))

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

	def face_aspect_ratio(self, fkey):
		"""Face aspect ratio as the ratio between the lengths of the maximum and minimum face edges.

		Parameters
		----------
		fkey : Key
			The face key.

		Returns
		-------
		float
			The aspect ratio.
		  
		 References
	    ----------
	    .. [1] Wikipedia. *Types of mesh*.
	           Available at: https://en.wikipedia.org/wiki/Types_of_mesh.

		"""

		face_edge_lengths = [self.edge_length(u, v) for u, v in self.face_halfedges(fkey)]
		return max(face_edge_lengths) / min(face_edge_lengths)

	def face_skewness(self, fkey):
		"""Face skewness as the maximum absolute angular deviation from the ideal polygon angle.

		Parameters
		----------
		fkey : Key
			The face key.

		Returns
		-------
		float
			The skewness.
		  
		 References
	    ----------
	    .. [1] Wikipedia. *Types of mesh*.
	           Available at: https://en.wikipedia.org/wiki/Types_of_mesh.

		"""

		ideal_angle = 180 * (1 - 2 / float(len(self.face_vertices(fkey))))
		
		angles = []
		
		for v in self.face_vertices(fkey):
			u = self.face_vertex_ancestor(fkey, v)
			w = self.face_vertex_descendant(fkey, v)
			angles.append(angle_points(self.vertex_coordinates(u), self.vertex_coordinates(v), self.vertex_coordinates(w), deg = True))
		
		return max((max(angles) - ideal_angle) / (180 - ideal_angle), (ideal_angle - min(angles)) / ideal_angle)

	def face_curvature(self, fkey):
		"""Dimensionless face curvature as the maximum face vertex deviation from the best-fit plane of the face vertices divided by the average lengths of the face vertices to the face centroid.

		Parameters
		----------
		fkey : Key
			The face key.

		Returns
		-------
		float
			The dimensionless curvature.

		"""

		plane = bestfit_plane([self.vertex_coordinates(vkey) for vkey in self.vertices()])

		max_deviation = max([distance_point_plane(self.vertex_coordinates(vkey), plane) for vkey in self.vertices()])

		average_distances = avrg([distance_point_point(self.vertex_coordinates(vkey), self.face_centroid(fkey)) for vkey in self.vertices()])

		return max_deviation / average_distances

	def mesh_vertex_curvatures(self, vkey):
		"""Dimensionless vertex curvature.

		Parameters
		----------
		fkey : Key
			The face key.

		Returns
		-------
		float
			The dimensionless curvature.

		"""

		return 2 * pi - sum([angle_points(mesh.vertex_coordinates(u), mesh.vertex_coordinates(vkey), mesh.vertex_coordinates(v)) for u, v in pairwise(self.vertex_neighbours(vkey, ordered = True))])

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

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	import compas

	mesh = Mesh.from_obj(compas.get('faces.obj'))

	#mesh.delete_face(13)
