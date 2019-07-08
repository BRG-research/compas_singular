
__all__ = [
	'mesh_insert_vertex_on_edge',
	'mesh_substitute_vertex_in_faces',
	'mesh_move_vertex_by',
	'mesh_move_by',
	'mesh_move_vertices_by',
	'mesh_move_vertex_to',
	'mesh_move_vertices_to'
]


### TO BE PUSHED TO COMPAS ###


def mesh_insert_vertex_on_edge(mesh, u, v, vkey=None):
	"""Insert an existing vertex on an edge.

	Parameters
	----------
	u: hashable
		The first edge vertex.
	v: hashable
		The second edge vertex.
	vkey: hashable, optional
		The vertex key to insert.
		Default is add a new vertex at mid-edge.

	"""

	# add new vertex if there is none
	if vkey is None:
		mesh.add_vertex(attr_dict = {attr: xyz for attr, xyz in zip(['x', 'y', 'z'], mesh.edge_midpoint(u, v))})

	# insert vertex
	for fkey, halfedge in zip(mesh.edge_faces(u, v), [(u, v), (v, u)]):
		if fkey is not None:
			face_vertices = mesh.face_vertices(fkey)[:]
			face_vertices.insert(face_vertices.index(halfedge[-1]), vkey)
			mesh.delete_face(fkey)
			mesh.add_face(face_vertices, fkey)


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


def mesh_move_vertex_by(mesh, vector, vkey):
	"""Move a mesh vertex by a vector.

	Parameters
	----------
	mesh : Mesh
		A mesh.
	vector : list
		An XYZ vector.
	vkey : hashable
		A vertex key.
	"""

	mesh.vertex[vkey]['x'] += vector[0]
	mesh.vertex[vkey]['y'] += vector[1]
	mesh.vertex[vkey]['z'] += vector[2]


def mesh_move_by(mesh, vector):
	"""Move a mesh by a vector.

	Parameters
	----------
	mesh : Mesh
		A mesh.
	vector : list
		An XYZ vector.
	"""

	for vkey in mesh.vertices():
		mesh_move_vertex_by(mesh, vector, vkey)


def mesh_move_vertices_by(mesh, key_to_vector):
	"""Move mesh vertices by different vectors.

	Parameters
	----------
	mesh : Mesh
		A mesh.
	key_to_vector : dict
		A dictionary of vertex keys pointing to vectors.
	"""

	for vkey, vector in key_to_vector.items():
		mesh_move_vertex(mesh, vector, vkey)


def mesh_move_vertex_to(mesh, point, vkey):
	"""Move a mesh vertex to a point.

	Parameters
	----------
	mesh : Mesh
		A mesh.
	point : list
		An XYZ point.
	vkey : hashable
		A vertex key.
	"""

	mesh.vertex[vkey]['x'] = point[0]
	mesh.vertex[vkey]['y'] = point[1]
	mesh.vertex[vkey]['z'] = point[2]


def mesh_move_vertices_to(mesh, key_to_point):
	"""Move mesh vertices to different points.

	Parameters
	----------
	mesh : Mesh
		A mesh.
	key_to_point : dict
		A dictionary of vertex keys pointing to points.
	"""

	for vkey, point in key_to_point.items():
		mesh_move_vertex_to(mesh, point, vkey)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	import compas
	