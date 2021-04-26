from compas_singular.datastructures import QuadMesh
from compas_singular.datastructures.lizard import Lizard
from compas.datastructures import mesh_smooth_centroid
from compas_plotters.meshplotter import MeshPlotter


# input mesh - standard 3 x 3 grid
vertices = [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [2.0, 0.0, 0.0], [0.0, 1.0, 0.0], [1.0, 1.0, 0.0], [2.0, 1.0, 0.0], [0.0, 2.0, 0.0], [1.0, 2.0, 0.0], [2.0, 2.0, 0.0]]
faces = [[0, 1, 4, 3], [1, 2, 5, 4], [3, 4, 7, 6], [4, 5, 8, 7]]
mesh = QuadMesh.from_vertices_and_faces(vertices, faces)
mesh.collect_strips()

# # plot input quad mesh
# plotter = MeshPlotter(mesh, figsize=(5, 5))
# plotter.draw_edges()
# plotter.draw_vertices(radius=.05)
# plotter.draw_faces()
# plotter.show()

# edit topology with lizard
lizard = Lizard(mesh)
lizard.initiate()
string = 'atta' # try: ata, attta, d, atttad, attpptta ...
lizard.from_string_to_rules(string)

# geometrical processing
mesh_smooth_centroid(mesh, kmax=1, damping=0.5)

for fkey in mesh.faces():
	print(mesh.face_vertices(fkey))

# # plot output quad mesh
# plotter = MeshPlotter(mesh, figsize=(5, 5))
# plotter.draw_edges()
# plotter.draw_vertices(radius=.05)
# plotter.draw_faces()
# plotter.show()
