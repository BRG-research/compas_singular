from compas_pattern.datastructures.mesh.mesh import Mesh
from compas_pattern.datastructures.mesh.operations import mesh_move_vertex_to
from compas.numerical import fd_numpy
from compas_plotters.meshplotter import MeshPlotter

def find_form(mesh):
    vertices = [mesh.vertex_coordinates(vkey) for vkey in sorted(list(mesh.vertices()))]
    edges = list(mesh.edges())
    fixed = mesh.vertices_on_boundary()
    print(len(fixed))
    q = [1.0] * len(edges)
    loads = [[0.0, 0.0, 50.0 / len(vertices)]] * len(vertices)
    xyz, q, f, l, r = fd_numpy(vertices, edges, fixed, q, loads)
    for vkey, coordinates in zip(sorted(list(mesh.vertices())), xyz):
        mesh_move_vertex_to(mesh, coordinates, vkey)

mesh = Mesh.from_json('/Users/Robin/Desktop/simple_mesh.json')
# print(sorted(list(mesh.vertices())))
find_form(mesh)

# for i in range(len(boundary)):
#     if boundary[i] != boundary2[i]:
#         print('!')

plotter = MeshPlotter(mesh, figsize=(20, 20))
plotter.draw_vertices(radius=0.1)
plotter.draw_edges()
plotter.draw_faces()
plotter.show()
