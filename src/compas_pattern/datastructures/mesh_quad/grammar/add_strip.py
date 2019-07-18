from compas_pattern.datastructures.mesh.operations import mesh_substitute_vertex_in_faces

__all__ = [
	'add_strip'
]


def sort_faces(mesh, u, v, w):
	print(u, v, w)

	faces = [[], []]
	k = 0
	vertex_faces = mesh.vertex_faces(v, ordered=True, include_none=True)
	f0 = mesh.halfedge[w][v] if w is not None else None
	i0 = vertex_faces.index(f0)
	vertex_faces = vertex_faces[i0:] + vertex_faces[:i0]

	for face in vertex_faces:
		
		if face is not None:
			faces[k].append(face)

		if u is None:
		 	if face is None:
		 		k = 1 - k
		elif face == mesh.halfedge[v][u]:
		 		k = 1 - k

	return faces


def add_strip(mesh, polyedge):

	# store data
	left_polyedge = []
	right_polyedge = []
	new_faces = []

	# exception if closed
	is_closed = polyedge[0] == polyedge[-1]
	if is_closed:
		polyedge.pop()

	k = -1
	count = len(polyedge) * 2
	while count and len(polyedge) > 0:
		k += 1
		count -= 1
		
		# select u, v, w if closed
		if not is_closed:
			# u
			if len(new_faces) != 0:
				u1, u2 = left_polyedge[-1], right_polyedge[-1]
			else:
				u1, u2 = None, None
			# v
			v = polyedge.pop(0)
			# w
			if len(polyedge) != 0:
				w = polyedge[0]
			else:
				w = None
		
		# select u, v, w if closed
		else:
			# u
			if len(new_faces) != 0:
				u1, u2 = left_polyedge[-1], right_polyedge[-1]
			else:
				u1 = polyedge[-1] # artificial u1
			# v
			v = polyedge.pop(0)
			# w
			if len(polyedge) != 0:
				w = polyedge[0]
			else:
				w = left_polyedge[0]

		

		# add new vertices
		faces_1, faces_2 = sort_faces(mesh, u1, v, w)
		v1, v2 = mesh.add_vertex(attr_dict=mesh.vertex[v]), mesh.add_vertex(attr_dict=mesh.vertex[v])
		mesh_substitute_vertex_in_faces(mesh, v, v1, faces_1)
		mesh_substitute_vertex_in_faces(mesh, v, v2, faces_2)
		mesh.delete_vertex(v)
		left_polyedge.append(v1)
		right_polyedge.append(v2)

		print(new_faces)
		# add new faces, different if at the start, end or main part of the polyedge
		if len(new_faces) == 0:
			if not is_closed:
				new_faces.append(mesh.add_face([v1, w, v2]))
			else:
				new_faces.append(mesh.add_face([v1, w, v2]))
				new_faces.append(mesh.add_face([v1, v2, u1]))
		elif len(polyedge) == 0:
			if not is_closed:
				u1, u2 = left_polyedge[-2], right_polyedge[-2]
				face = new_faces.pop()
				mesh.delete_face(face)
				new_faces.append(mesh.add_face([u1, v1, v2, u2]))
			else:
				u1, u2 = left_polyedge[0], right_polyedge[0]
				face = new_faces.pop()
				mesh.delete_face(face)
				new_faces.append(mesh.add_face([u1, v1, v2, u2]))
				face = new_faces.pop(0)
				mesh.delete_face(face)
				new_faces.append(mesh.add_face([u1, v1, v2, u2]))
		else:
			face = new_faces.pop()
			mesh.delete_face(face)
			new_faces.append(mesh.add_face([u1, v1, v2, u2]))
			new_faces.append(mesh.add_face([v1, w, v2]))


		# include pseudo closed polyedges
		
		# update polyedge

	# strip data update

	# geometry processing

	# out put new_faces, left_polyedge, right_polyedge, map vertices

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	import compas
	from compas_pattern.datastructures.mesh_quad.mesh_quad import QuadMesh
	from compas.datastructures import mesh_smooth_centroid
	from compas_plotters.meshplotter import MeshPlotter


	mesh = QuadMesh.from_obj(compas.get('faces.obj'))

	# plotter = MeshPlotter(mesh, figsize = (20, 20))
	# plotter.draw_vertices(radius = 0.25, text='key')
	# plotter.draw_edges()
	# plotter.draw_faces(text='key')
	# plotter.show()

	# polyedge = [6, 7, 8, 9, 10, 11]
	# polyedge = [0, 1, 2, 3, 4, 5]
	# polyedge = [30, 31, 32, 33, 34, 35]
	# polyedge = [24, 25, 26, 32]
	polyedge = [14, 15, 21, 20, 14]
	# polyedge = [6, 7, 8, 14, 13, 7, 1]
	# polyedge = [0, 1, 2, 8, 2]


	add_strip(mesh, polyedge)
	mesh_smooth_centroid(mesh, fixed=[vkey for vkey in mesh.vertices_on_boundary() if len(mesh.vertex_neighbors(vkey)) == 2], kmax=1)

	plotter = MeshPlotter(mesh, figsize = (20, 20))
	plotter.draw_vertices(radius = 0.1)
	plotter.draw_edges()
	plotter.draw_faces()
	plotter.show()



