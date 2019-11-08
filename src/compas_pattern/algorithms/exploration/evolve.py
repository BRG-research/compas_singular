
__all__ = [

]


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	from compas_pattern.datastructures.mesh_quad_coarse import CoarseQuadMesh
	from compas_pattern.algorithms.exploration.walk import Walker
	import random as rd
	from math import pi
	from compas.geometry import add_vectors
	from compas.geometry import circle_evaluate
	from compas_pattern.datastructures.mesh.operations import mesh_move_vertex_to
	from compas_pattern.datastructures.mesh.operations import mesh_move_by
	from compas.numerical.fd.fd_numpy import fd_numpy
	from compas.geometry import rotate_points
	from compas_plotters.meshplotter import MeshPlotter
	from compas_pattern.algorithms.interpolation.isomorphism import are_meshes_isomorphic
	from compas.datastructures import meshes_join

	def define_density(mesh, nb_faces):
		mesh.set_strips_density(1)
		mesh.set_mesh_density_face_target(nb_faces)
		mesh.densification()

	def fix_boundaries(mesh):
		n = len(mesh.vertices_on_boundary())
		for i, vkey in enumerate(mesh.boundaries()[0]):
			xyz = add_vectors(mesh.vertex_centroid(), circle_evaluate(2.0 * pi * i / n, 10))
			mesh_move_vertex_to(mesh, xyz, vkey)

	def find_form(mesh, total_load):
		vertices = [mesh.vertex_coordinates(vkey) for vkey in mesh.vertices()]
		edges = list(mesh.edges())
		fixed = mesh.vertices_on_boundary()
		q = [1.0] * len(edges)
		total_area = mesh.area()
		loads = [[0.0, 0.0, total_load * mesh.vertex_area(vkey) / total_area] for vkey in mesh.vertices()] 
		xyz, q, f, l, r = fd_numpy(vertices, edges, fixed, q, loads)
		for vkey, coordinates in zip(mesh.vertices(), xyz):
			mesh_move_vertex_to(mesh, coordinates, vkey)

	def eval(mesh):
		return sum([mesh.edge_length(*edge) ** 2 for edge in mesh.edges()])

	def rotate_mesh(mesh):
		origin = mesh.centroid()
		axis = [1, 0, 0]

		new_points = rotate_points([mesh.vertex_coordinates(vkey) for vkey in mesh.vertices()], -pi / 4, axis, origin)
		for vkey, (x, y, z) in zip(mesh.vertices(), new_points):
			mesh.vertex[vkey]['x'] = x
			mesh.vertex[vkey]['y'] = y
			mesh.vertex[vkey]['z'] = z


	dx = 10
	dy = 10

	vertices = [
		[-dx/2, -dy/2, 0],
		[0, -dy/2, 0],
		[dx/2, -dy/2, 0],
		[-dx/2, 0, 0],
		[0, 0, 0],
		[dx/2, 0, 0],
		[-dx/2, dy/2, 0],
		[0, dy/2, 0],
		[dx/2, dy/2, 0],
	]

	faces = [
		[0,1,4,3],
		[1,2,5,4],
		[4,5,8,7],
		[3,4,7,6],
	]

	mesh = CoarseQuadMesh.from_vertices_and_faces(vertices, faces)
	mesh.collect_strips()

	meshes = [mesh]
	count = 1000
	while count and len(meshes) < 9:
		count -= 1
		mesh2 = mesh.copy()
		walker = Walker(mesh2)
		walker.start()
		orders = [rd.randint(0,2) for _ in range(10)]
		# print(orders)
		try:
			walker.interpret_orders(orders)
			if not any([are_meshes_isomorphic(mesh1, mesh2, boundary_edge_data=True) for mesh1 in meshes]):
				meshes.append(mesh2)
		except:
			pass

	print('nb meshes', len(meshes))
	for mesh2 in meshes:
		print('nb faces', mesh2.number_of_faces())
	# plotter = MeshPlotter(mesh, figsize=(5.0, 5.0))
	# plotter.draw_edges()
	# plotter.draw_faces()
	# plotter.show()

	vectors = [
		[0,0,0],
		[30,0,0],
		[30,30,0],
		[0,30,0],
		[-30,30,0],
		[-30,0,0],
		[-30,-30,0],
		[0,-30,0],
		[30,-30,0],
	]
	
	for vector, mesh2 in zip(vectors, meshes):
		mesh2.collect_strips()
		fix_boundaries(mesh2)
		define_density(mesh2, 300)
		fix_boundaries(mesh2.get_quad_mesh())
		find_form(mesh2.get_quad_mesh(), 100.0)
		mesh_move_by(mesh2.get_quad_mesh(), vector)
		rotate_mesh(mesh2.get_quad_mesh())

	# for mesh2 in meshes:
	# 	if mesh2.get_quad_mesh() is None:
	# 		print('!')

	# for mesh in meshes:
	# 	plotter = MeshPlotter(mesh, figsize=(5.0, 5.0))
	# 	plotter.draw_edges()
	# 	plotter.draw_faces()
	# 	plotter.show()

	all_meshes = meshes_join([mesh2.get_quad_mesh() for mesh2 in meshes])
	plotter = MeshPlotter(all_meshes, figsize=(5.0, 5.0))
	plotter.draw_edges()
	plotter.draw_faces()
	plotter.show()


