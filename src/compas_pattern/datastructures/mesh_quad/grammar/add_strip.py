from compas.topology import breadth_first_paths
from compas_pattern.datastructures.mesh.operations import mesh_substitute_vertex_in_faces
from compas_pattern.datastructures.mesh_quad.grammar_pattern import strip_polyedge_update

__all__ = [
	'add_strip'
]


def sort_faces(mesh, u, v, w):
	#print(u, v, w)

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


def add_strip(mesh, polyedge, close=True):

	# store data
	left_polyedge = []
	right_polyedge = []
	new_faces = []

	# exception if closed
	is_closed = polyedge[0] == polyedge[-1] and close
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

		# add new faces, different if at the start, end or main part of the polyedge
		if len(new_faces) == 0:
			if not is_closed:
				new_faces.append(mesh.add_face([v1, w, v2]))
			else:
				new_faces.append(mesh.add_face([v1, v2, u1]))
				new_faces.append(mesh.add_face([v1, w, v2]))
		elif len(polyedge) == 0:
			if not is_closed:
				u1, u2 = left_polyedge[-2], right_polyedge[-2]
				face = new_faces.pop()
				mesh.delete_face(face)
				new_faces.append(mesh.add_face([u1, v1, v2, u2]))
			else:
				u1, u2 = left_polyedge[-2], right_polyedge[-2]
				face = new_faces.pop()
				mesh.delete_face(face)
				new_faces.append(mesh.add_face([v1, u1, u2, v2]))
				face = new_faces.pop(0)
				mesh.delete_face(face)
				u1, u2 = left_polyedge[0], right_polyedge[0]
				new_faces.append(mesh.add_face([v1, u1, u2, v2]))
		else:
			face = new_faces.pop()
			mesh.delete_face(face)
			new_faces.append(mesh.add_face([u1, v1, v2, u2]))
			new_faces.append(mesh.add_face([v1, w, v2]))

		# print('!', polyedge)
		#print(v, v1, v2)
		# update
		polyedge_0 = []
		via_vkeys = [v1, v2]
		for i, vkey in enumerate(polyedge):
			if vkey != v:
				polyedge_0.append(vkey)
			else:
				# print('?')
				from_vkey = polyedge[i - 1]
				to_vkey = polyedge[i + 1]
				polyedge_0 += polyedge_from_to_via_vertices(mesh, from_vkey, to_vkey, via_vkeys)[1:-1]
		polyedge = polyedge_0
		# print('!!', polyedge)


		# for fkey in new_faces:
		# 	print(fkey, mesh.face_vertices(fkey))
		
		# mesh_smooth_centroid(mesh, kmax=1)
		# plotter = MeshPlotter(mesh, figsize = (20, 20))
		# plotter.draw_vertices(radius = 0.25, text='key')
		# plotter.draw_edges()
		# plotter.draw_faces(text='key')
		# plotter.show()

		# include pseudo closed polyedges
		# update polyedge

	# strip data update
	# out put new_faces, left_polyedge, right_polyedge, map vertices




def adjacency_from_to_via_vertices(mesh, from_vkey, to_vkey, via_vkeys):
	# get mesh adjacency constraiend to from_vkey and via_keys, via_keys and via_keys, and via_vkeys and to_vkey

	all_vkeys = set([from_vkey, to_vkey, *via_vkeys])
	adjacency = {}
	for vkey, nbrs in mesh.adjacency.items():
		if vkey not in all_vkeys:
			continue
		else:
			sub_adj = {}
			for nbr, face in nbrs.items():
				if nbr not in all_vkeys or (vkey == from_vkey and nbr == to_vkey) or (vkey == to_vkey and nbr == from_vkey):
						continue
				else:
					sub_adj.update({nbr: face})
			adjacency.update({vkey: sub_adj})
	return adjacency


def polyedge_from_to_via_vertices(mesh, from_vkey, to_vkey, via_vkeys):
	# return shortest polyedge from_vkey to_vkey via_vkeys

	adjacency = adjacency_from_to_via_vertices(mesh, from_vkey, to_vkey, via_vkeys)
	return next(breadth_first_paths(adjacency, from_vkey, to_vkey))

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	import compas
	from compas_pattern.datastructures.mesh_quad.mesh_quad import QuadMesh
	from compas.datastructures import mesh_smooth_centroid
	from compas_pattern.datastructures.mesh.operations import mesh_move_by
	from compas.datastructures import meshes_join
	from compas_plotters.meshplotter import MeshPlotter


	mesh = QuadMesh.from_obj(compas.get('faces.obj'))

	# plotter = MeshPlotter(mesh, figsize = (20, 20))
	# plotter.draw_vertices(radius = 0.25, text='key')
	# plotter.draw_edges()
	# plotter.draw_faces(text='key')
	# plotter.show()

	polyedges = [
		[6, 7, 8, 9, 10, 11],
		[0, 1, 2, 3, 4, 5],
		[30, 31, 32, 33, 34, 35],
		[24, 25, 26, 32],
		[14, 15, 21, 20, 14],
		[6, 7, 8, 14, 13, 7, 1],
		# [2, 8, 2],
		# [1, 2, 8, 2, 3],
		# [2, 8, 14, 8, 2],
		# [0, 1, 2, 8, 2, 3, 4, 5],
	]

	meshes = []
	for i, polyedge in enumerate(polyedges):
		mesh2 = mesh.copy()
		add_strip(mesh2, polyedge, close=True)
		#mesh_smooth_centroid(mesh2, fixed=[vkey for vkey in mesh.vertices_on_boundary() if len(mesh.vertex_neighbors(vkey)) == 2], kmax=1)
		mesh_smooth_centroid(mesh2, kmax=1)
		mesh_move_by(mesh2, [i * 10.0, 0.0, 0.0])
		meshes.append(mesh2)

	mesh = meshes_join(meshes)

	plotter = MeshPlotter(mesh, figsize=(20, 20))
	plotter.draw_vertices(radius=0.1)
	plotter.draw_edges()
	plotter.draw_faces()
	plotter.show()

	#print(polyedge_from_to_via_vertices(mesh, 6, 8, [12, 13, 14]))

