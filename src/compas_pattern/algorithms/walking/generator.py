from random import random
from random import randint

from compas_pattern.algorithms.walking.walking import Walker

__all__ = [
	'random_walk'
]


def random_walk(walker, n):

	walk = ''

	for i in range(n):
		
		rules = walker.get_eligible_rules()
		rule = rules[randint(0, len(rules) - 1)]

		if rule == 'f':
			walker.forward()

		elif rule == 'r':
			walker.rotate()

		elif rule == 's':
			walker.start_polyedge()

		elif rule == 'e':
			walker.end_polyedge()
			
		walk += rule

	return walk

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	from random import randint
	import compas
	from compas.datastructures import mesh_unify_cycles
	from compas.plotters import MeshPlotter

	for i in range(100):

		vertices = [
			[0.0, 0.0, 0.0],
			[1.0, 0.0, 0.0],
			[1.0, 1.0, 0.0],
			[0.0, 1.0, 0.0],
		]

		faces = [
			[0, 1, 2, 3]
		]

		walker = Walker.from_vertices_and_faces(vertices, faces)
		walker.collect_strips()
		mesh_unify_cycles(walker)

		walker.start_walking()

		try:
			walk = random_walk(walker, randint(3, 100))

			name = walk + '.json'
			walker.to_json('/Users/Robin/Desktop/walker_data/' + name)
		
		except:
			pass
	# plotter = MeshPlotter(walker, figsize = (5, 5))
	# plotter.draw_vertices(radius = 0.01)
	# plotter.draw_edges()
	# plotter.draw_faces()
	# plotter.show()


