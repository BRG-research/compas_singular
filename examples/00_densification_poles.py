import json

from compas_pattern.datastructures import CoarsePseudoQuadMesh

from compas_plotters.meshplotter import MeshPlotter

# read input data
json_data = 'data/coarse_quad_mesh_british_museum_poles.json'

coarse_pseudo_quad_mesh = CoarsePseudoQuadMesh.from_json(json_data)

#plot coarse quad mesh
plotter = MeshPlotter(coarse_pseudo_quad_mesh, figsize=(5, 5))
plotter.draw_edges()
plotter.draw_vertices(radius=.05)
plotter.draw_faces()
plotter.show()

# collect strip data
coarse_pseudo_quad_mesh.collect_strips()

# densification with target length
coarse_pseudo_quad_mesh.set_strips_density_target(t=.5)
coarse_pseudo_quad_mesh.densification()

# plot dense quad mesh
plotter = MeshPlotter(coarse_pseudo_quad_mesh.get_quad_mesh(), figsize=(5, 5))
plotter.draw_edges()
plotter.draw_vertices(radius=.05)
plotter.draw_faces()
plotter.show()
