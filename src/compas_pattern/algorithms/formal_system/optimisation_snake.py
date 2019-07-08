import random
from math import pi
from math import floor
from compas_pattern.datastructures.mesh_quad_coarse.mesh_quad_coarse import CoarseQuadMesh
from compas_pattern.algorithms.formal_system.snake import Snake
from compas.geometry.analytical import circle_evaluate
from compas_pattern.datastructures.mesh.operations import mesh_move_vertex_to
from compas_pattern.datastructures.mesh.operations import mesh_move_by
from compas.numerical import fd_numpy
from compas.numerical import ga
from compas.datastructures import meshes_join
from compas_plotters.meshplotter import MeshPlotter
from compas_plotters.gaplotter import visualize_evolution

def get_step_size(bin_dig, delta):
    binary = ''
    for i in range(bin_dig):
        binary += '1'
    value = 0
    for i in range(bin_dig):
        value = value + 2**i
    print('number of steps', value)
    print('step size', delta / float(value))

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
        mesh.vertex[vkey]['x'] = coordinates[0]
        mesh.vertex[vkey]['y'] = coordinates[1]
        mesh.vertex[vkey]['z'] = coordinates[2]

def compute_load_path(mesh):
	return sum([mesh.edge_length(*edge) ** 2 for edge in mesh.edges()])

def fit_function(code, **fkwargs):

	mesh = fkwargs['mesh']
	output_mesh = fkwargs['output_mesh']
	
	mesh_2 = mesh.copy()
	snake = Snake(mesh_2)
	snake.interpret(code)
	fix_boundaries(mesh_2)
	define_density(mesh_2, 500)
	fix_boundaries(mesh_2.get_quad_mesh())
	find_form(mesh_2.get_quad_mesh())

	if output_mesh:
		return mesh_2
	#fit_value = - mesh_2.number_of_strips()
	#fit_value = compute_load_path(mesh_2.get_quad_mesh())
	fit_value = sum([mesh_2.get_quad_mesh().face_skewness(fkey) * mesh_2.get_quad_mesh().face_area(fkey) for fkey in mesh_2.get_quad_mesh().faces()]) / sum([mesh_2.get_quad_mesh().face_area(fkey) for fkey in mesh_2.get_quad_mesh().faces()])
	return fit_value

vertices = [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 1.0, 0.0], [0.0, 1.0, 0.0]]
faces = [[0, 1, 2, 3]]

mesh = CoarseQuadMesh.from_vertices_and_faces(vertices, faces)
mesh.collect_strips()

output_path = '/Users/Robin/Desktop/ga_results/'

num_var = 8
boundaries = [(0.0, 1.0)] * num_var
num_pop = 10
num_gen = 10
num_elite = 2
num_bin_dig = [16] * num_var
mutation_probability = 0.03 
n_cross = 2
fkwargs = {'mesh': mesh, 'output_mesh': False}

ga_ = ga(fit_function, 'min', num_var, boundaries, output_path=output_path, num_pop=num_pop, num_gen=num_gen, num_elite=num_elite, num_bin_dig=num_bin_dig, mutation_probability=mutation_probability, n_cross=n_cross, fkwargs=fkwargs)

visualize_evolution(ga_.output_path)

best_vector = ga_.current_pop['scaled'][ga_.best_individual_index]
best_mesh = fit_function(best_vector, **{'mesh': mesh, 'output_mesh': True})
plotter = MeshPlotter(best_mesh.get_quad_mesh(), figsize = (5, 5))
plotter.draw_vertices(radius = 0.01)
plotter.draw_edges()
plotter.draw_faces()
plotter.show()
