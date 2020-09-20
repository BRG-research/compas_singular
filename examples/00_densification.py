import os

from compas_singular.datastructures import CoarseQuadMesh
from compas_plotters.meshplotter import MeshPlotter

HERE = os.path.dirname(__file__)
FILE = os.path.join(HERE, 'data/coarse_quad_mesh_british_museum.json')

# read input data
coarse_quad_mesh = CoarseQuadMesh.from_json(FILE)

# plot coarse quad mesh
plotter = MeshPlotter(coarse_quad_mesh, figsize=(5, 5))
plotter.draw_edges()
plotter.draw_vertices(radius=.05)
plotter.draw_faces()
plotter.show()

# collect strip data
coarse_quad_mesh.collect_strips()

# densification with uniform density
coarse_quad_mesh.set_strips_density(3)
coarse_quad_mesh.densification()

# plot dense quad mesh
plotter = MeshPlotter(coarse_quad_mesh.get_quad_mesh(), figsize=(5, 5))
plotter.draw_edges()
plotter.draw_vertices(radius=.05)
plotter.draw_faces()
plotter.show()

# densification with target length
coarse_quad_mesh.set_strips_density_target(t=.5)
coarse_quad_mesh.densification()

# plot dense quad mesh
plotter = MeshPlotter(coarse_quad_mesh.get_quad_mesh(), figsize=(5, 5))
plotter.draw_edges()
plotter.draw_vertices(radius=.05)
plotter.draw_faces()
plotter.show()

# change density of one strip
skey = list(coarse_quad_mesh.strips())[0]
coarse_quad_mesh.set_strip_density(skey, 10)
coarse_quad_mesh.densification()

# plot dense quad mesh
plotter = MeshPlotter(coarse_quad_mesh.get_quad_mesh(), figsize=(5, 5))
plotter.draw_edges()
plotter.draw_vertices(radius=.05)
plotter.draw_faces()
plotter.show()
