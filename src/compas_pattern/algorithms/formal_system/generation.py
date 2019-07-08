from random import randint

from compas_pattern.algorithms.formal_system.formal_system import Formal

__all__ = [
	'generate_random'
]


def generate_random(quad_mesh, n):

	walk = ''

	for i in range(n):
		
		rules = ['r', 'l', 't']
		rule = rules[randint(0, len(rules) - 1)]
		walk += rule

	encode = Formal(quad_mesh)
	encode.start()
	encode.interpret(walk)

	return walk

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	import compas
	from compas_pattern.datastructures.mesh_quad.mesh_quad import QuadMesh
	from compas.plotters import MeshPlotter

	vertices = [
		[0.0, 0.0, 0.0],
		[1.0, 0.0, 0.0],
		[1.0, 1.0, 0.0],
		[0.0, 1.0, 0.0],
	]

	faces = [
		[0, 1, 2, 3]
	]

	mesh = QuadMesh.from_vertices_and_faces(vertices, faces)
	mesh.collect_strips()

	code = generate_random(mesh, 30)
	print(code)

	plotter = MeshPlotter(mesh, figsize = (5, 5))
	plotter.draw_vertices(radius = 0.01)
	plotter.draw_edges()
	plotter.draw_faces()
	plotter.show()
		
