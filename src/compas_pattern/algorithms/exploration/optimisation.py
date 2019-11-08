__all__ = []


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	import compas
	from compas_pattern.datastructures.mesh_quad_coarse.mesh_quad_coarse import CoarseQuadMesh
	from compas_pattern.algorithms.exploration.walk import Walker
	from compas_pattern.datastructures.mesh_quad.grammar.add_strip import add_strip
	from compas.datastructures import mesh_smooth_centroid
	from compas_plotters.meshplotter import MeshPlotter
	from compas.numerical import ga

	mesh = CoarseQuadMesh.from_obj(compas.get('faces.obj'))
	mesh.collect_strips()

	fit_type = 'max'
	num_var = 5
	boundaries = [(0.0, 1.0)] * num_var
	num_bin_dig = [2] * num_var
	output_path = '/Users/Robin/Desktop/ga/'
	fkwargs = {'mesh': mesh}

	def fit_function(X, **fkwargs):
		print('X', X)
		mesh = fkwargs['mesh']
		orders = [2] + [int(x) for x in X]
		mesh_2 = mesh.copy()
		walker = Walker(mesh_2)
		walker.start()
		print('orders', orders)
		out = walker.interpret_orders(orders)
		polyedge = walker.polyedge
		print('polyedge', polyedge)
		add_strip(mesh_2, polyedge)
		# if out == None:
		# 	fit_value = float('inf')
		fit_value = mesh_2.number_of_faces()
		return fit_value

	# vector = [0,1,0,1,0]
	# mesh_2, fit_value = fit_function(vector, **fkwargs)
	# print('fit value: ', fit_value)
	# mesh_smooth_centroid(mesh_2, kmax=10, fixed=mesh_2.vertices_on_boundary())
	# plotter = MeshPlotter(mesh_2, figsize = (20, 20))
	# plotter.draw_vertices(radius = 0.1)
	# plotter.draw_edges()
	# plotter.draw_faces()
	# plotter.show()

	ga_ = ga(fit_function,
		 fit_type,
		 num_var,
		 boundaries,
		 num_gen=10,
		 num_pop=10,
		 num_elite=20,
		 num_bin_dig=num_bin_dig,
		 output_path=output_path,
		 mutation_probability=0.03,
		 n_cross=2,
		 fkwargs=fkwargs)


