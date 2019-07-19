import compas
from math import pi
from compas_pattern.datastructures.mesh_quad_coarse.mesh_quad_coarse import CoarseQuadMesh
from compas_pattern.algorithms.formal_system.formal_system import Formal
from compas.geometry.analytical import circle_evaluate
from compas_pattern.datastructures.mesh.operations import mesh_move_vertex_to
from compas.numerical import fd_numpy
from compas.numerical import ga
from compas_plotters.meshplotter import MeshPlotter
from compas_plotters.gaplotter import visualize_evolution

def encode(code):
	encoded = []
	for x in code:
		if x == 'r':
			encoded.append(0.0)
		elif x == 'l':
			encoded.append(0.33)
		elif x == '+':
			encoded.append(0.66)
		#elif x == '-':
		#	encoded.append(3.0)
	return encoded

def decode(code):
	decoded = ''
	for x in code:
		if x < 0.33:
			decoded += 'r'
		elif x < 0.66:
			decoded += 'l'
		else:
			decoded += '+'
		#elif x == 3.0:
		#	decoded += '-'
	return decoded

def define_density(mesh):
	mesh.set_strips_density(1)
	mesh.set_mesh_density_face_target(500)
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
    #vertex_areas = [mesh.vertex_area(vkey) for vkey in mesh.vertices()]
    #load = 1000
    #loads = [[0.0, 0.0, load * mesh.vertex_area(vkey) / mesh.area()] for vkey in mesh.vertices()]
    xyz, q, f, l, r = fd_numpy(vertices, edges, fixed, q, loads)
    for vkey, coordinates in zip(mesh.vertices(), xyz):
        mesh.vertex[vkey]['x'] = coordinates[0]
        mesh.vertex[vkey]['y'] = coordinates[1]
        mesh.vertex[vkey]['z'] = coordinates[2]

def compute_load_path(mesh):
	return sum([mesh.edge_length(*edge) ** 2 for edge in mesh.edges()])

def fit_function(code, **fkwargs):

	mesh = fkwargs['mesh']
	
	#print(code)
	decoded = decode(code)
	#print(decoded)
	mesh_2 = mesh.copy()
	formal = Formal(mesh_2)
	formal.start()
	out = formal.interpret(decoded)
	if out == 'no':
		fit_value = float('inf')
		print(code, decoded, fit_value)
		return fit_value
	
	define_density(mesh_2)
	fix_boundaries(mesh_2.get_quad_mesh())
	find_form(mesh_2.get_quad_mesh())
	
	#return - sum([mesh_2.vertex_index(vkey) ** 2 for vkey in mesh_2.singularities()])
	#return - mesh_2.number_of_strips()
	quad_mesh = mesh_2.get_quad_mesh()
	#fit_value = sum([quad_mesh.face_curvature(fkey) * quad_mesh.face_area(fkey) for fkey in quad_mesh.faces()]) / sum([quad_mesh.face_area(fkey) for fkey in quad_mesh.faces()])
	fit_value = - compute_load_path(quad_mesh)
	if not fit_value:
		fit_value = float('inf')
	print(code, decoded, fit_value)
	return fit_value

# vertices = [
# 	[1.0, 1.0, 0.0],
# 	[-1.0, 1.0, 0.0],
# 	[-1.0, -1.0, 0.0],
# 	[1.0, -1.0, 0.0],
# ]

# faces = [
# 	[0, 1, 2, 3]
# ]

# mesh = CoarseQuadMesh.from_vertices_and_faces(vertices, faces)
mesh = CoarseQuadMesh.from_obj(compas.get('faces.obj'))
mesh.collect_strips()

# mesh_2, fit_value = fit_function(encode('rlrrrrlrrtrrllrrrllrrlrlrrtrtl'), **{'mesh': mesh})
# print(fit_value)

# for vkey in mesh_2.get_quad_mesh().vertices():
# 	attr = mesh_2.get_quad_mesh().vertex[vkey]
# 	attr['x'], attr['z'], attr['y'] = attr['x'], attr['y'], attr['z']

# plotter = MeshPlotter(mesh_2.get_quad_mesh(), figsize = (5, 5))
# plotter.draw_vertices(radius = 0.01)
# plotter.draw_edges()
# plotter.draw_faces()
# plotter.show()

output_path = '/Users/Robin/Desktop/ga_results/'

num_var = 6
boundaries = [(0.0, 1.0)] * num_var
num_pop = 100
num_gen = 30
num_elite = 2
num_bin_dig = [6] * num_var
mutation_probability = 0.03 
n_cross = 2
fkwargs = {'mesh': mesh}

ga_ = ga(fit_function, 'min', num_var, boundaries, output_path=output_path, num_pop=num_pop, num_gen=num_gen, num_elite=num_elite, num_bin_dig=num_bin_dig, mutation_probability=mutation_probability, n_cross=n_cross, fkwargs=fkwargs)

visualize_evolution(ga_.output_path)
