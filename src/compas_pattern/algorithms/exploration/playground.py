from math import pi
from compas_pattern.datastructures.mesh_quad_coarse.mesh_quad_coarse import CoarseQuadMesh
from compas_pattern.algorithms.exploration.encoding import Snake
from compas_pattern.datastructures.mesh_quad.grammar.add_strip import add_strip
from compas.datastructures import mesh_smooth_centroid
from compas.geometry.analytical import circle_evaluate
from compas_pattern.datastructures.mesh.operations import mesh_move_vertex_to
from compas_pattern.datastructures.mesh.operations import mesh_move_by
from compas.numerical import fd_numpy
from compas_plotters.meshplotter import MeshPlotter

def define_density(mesh, nb_faces):
	mesh.set_strips_density(1)
	mesh.set_mesh_density_face_target(nb_faces)
	mesh.densification()

def fix_boundaries(mesh):
	n = len(mesh.vertices_on_boundary())
	for i, vkey in enumerate(mesh.boundaries()[0]):
		xyz = circle_evaluate(2.0 * pi * i / n, 10)
		mesh_move_vertex_to(mesh, xyz, vkey)

def find_form(mesh):
    vertices = [mesh.vertex_coordinates(vkey) for vkey in mesh.vertices()]
    edges = list(mesh.edges())
    fixed = mesh.vertices_on_boundary()
    q = [1.0] * len(edges)
    loads = [[0.0, 0.0, 50.0 / len(vertices)]] * len(vertices)
    xyz, q, f, l, r = fd_numpy(vertices, edges, fixed, q, loads)
    for vkey, coordinates in zip(mesh.vertices(), xyz):
    	mesh_move_vertex_to(mesh, coordinates, vkey)

vertices = [
	[0.0, 0.0, 0.0],
	[1.0, 0.0, 0.0],
	[1.0, 1.0, 0.0],
	[0.0, 1.0, 0.0],
]

faces = [
	[0, 1, 2, 3]
]

mesh = CoarseQuadMesh.from_vertices_and_faces(vertices, faces)

snake = Snake(mesh)
snake.start()

mesh = snake.interpret_values([2, 0, 0, 0, 2])
print(snake.added_polyedges)

mesh.collect_strips()
fix_boundaries(mesh)
define_density(mesh, 500)
fix_boundaries(mesh.get_quad_mesh())
find_form(mesh.get_quad_mesh())

plotter = MeshPlotter(mesh.get_quad_mesh(), figsize = (20, 20))
plotter.draw_vertices(radius = 0.01)
plotter.draw_edges()
plotter.draw_faces()
plotter.show()

