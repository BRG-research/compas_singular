import time
import operator
from compas_pattern.datastructures.mesh.mesh import Mesh
from compas.geometry import Polyline
from compas_pattern.datastructures.mesh.operations import mesh_move_vertex_to
from compas.numerical import descent_numpy
from compas.numerical import fd_numpy
from compas_plotters.meshplotter import MeshPlotter
from compas.topology import conway_gyro

def fix_boundaries(mesh, polyline_points, t=0):
    polyline = Polyline(polyline_points)
    n = len(mesh.vertices_on_boundary())
    for i, vkey in enumerate(mesh.boundaries()[0]):
        xyz = polyline.point((t + i / n) % 1.0)
        mesh_move_vertex_to(mesh, xyz, vkey)

def find_form(mesh):
    vertices = [mesh.vertex_coordinates(vkey) for vkey in sorted(list(mesh.vertices()))]
    edges = list(mesh.edges())
    fixed = mesh.vertices_on_boundary()
    q = [1.0] * len(edges)
    loads = [[0.0, 0.0, 50.0 / len(vertices)]] * len(vertices)
    xyz, q, f, l, r = fd_numpy(vertices, edges, fixed, q, loads)
    for vkey, coordinates in zip(sorted(list(mesh.vertices())), xyz):
        mesh_move_vertex_to(mesh, coordinates, vkey)

def load_path(mesh):
    return sum([mesh.edge_length(*edge)for edge in mesh.edges()])

def func(t, mesh, polyline_points):
    fix_boundaries(mesh, polyline_points, t)
    find_form(mesh)
    return load_path(mesh)

mesh = Mesh.from_json('/Users/Robin/Desktop/simple_mesh.json')
mesh = conway_gyro(mesh)
polyline_points = [[2.6063381123514175, 40.935946423181882, 0.0], [3.9369282045788494, 42.327616276045276, 0.0], [5.760612811568148, 42.957179887931325, 0.0], [7.677141583573143, 42.741476009840468, 0.0], [9.249202441569466, 41.636074033399247, 0.0], [10.099070540147636, 39.901842354098889, 0.0], [10.445234328797181, 37.988992350564551, 0.0], [10.832127422110238, 36.086128649415919, 0.0], [12.034580052260155, 34.611669302310716, 0.0], [13.872402034803775, 34.000898316364172, 0.0], [15.793258601276873, 33.693072434788895, 0.0], [17.697244927994845, 33.299890980625278, 0.0], [19.435815699891037, 32.455904337698669, 0.0], [20.426594142557271, 30.827275105478869, 0.0], [20.342022048992952, 28.899749204952844, 0.0], [19.623693444007561, 27.097254631909845, 0.0], [18.531723370562204, 25.490791357033796, 0.0], [17.151204887065784, 24.1245174325152, 0.0], [15.504742411164692, 23.097835022281213, 0.0], [13.634194878088236, 22.598407206196676, 0.0], [11.709234015328173, 22.793376767312694, 0.0], [9.93372896539173, 23.575992856031679, 0.0], [8.319373942334007, 24.660282275558348, 0.0], [6.709463863068362, 25.750770094918934, 0.0], [4.866553897213048, 26.293470858116262, 0.0], [3.0216937343488413, 25.733523450550926, 0.0], [1.353415694349765, 24.7335783835434, 0.0], [-0.33207180153779414, 23.763448993158061, 0.0], [-2.1478721442735416, 23.076290891477637, 0.0], [-4.0778793647653915, 22.908325747702342, 0.0], [-5.960745854618975, 23.364948037786053, 0.0], [-7.647240949939723, 24.325417190174758, 0.0], [-9.104033414789109, 25.611201434493566, 0.0], [-10.347777096128976, 27.105281954883473, 0.0], [-11.391413517402787, 28.74577648393597, 0.0], [-12.227592881842222, 30.501025652824321, 0.0], [-12.815238320469355, 32.353654138559236, 0.0], [-13.042641240111568, 34.281247769605443, 0.0], [-12.622290953609523, 36.162503420602924, 0.0], [-11.195139556380814, 37.41966870664929, 0.0], [-9.279464876213346, 37.665438686605405, 0.0], [-7.3612965110303445, 37.357975781718082, 0.0], [-5.502088376669821, 36.787694911721061, 0.0], [-3.692030245523491, 36.075185023177717, 0.0], [-1.9139944966914493, 35.285643261342685, 0.0], [-0.14360420308513655, 34.478991840040493, 0.0], [1.6875554934165495, 33.836829772274363, 0.0], [2.3840652252579315, 35.2261359704494, 0.0], [2.07811399189295, 37.147211081626246, 0.0], [2.0417178149613906, 39.088213850462886, 0.0], [2.6063381123514175, 40.935946423181882, 0.0]]

# fix_boundaries(mesh, polyline_points, t=0.0)
# find_form(mesh)
# print('load path: ', load_path(mesh))

t0 = time.time()
opt_design = None
opt_param = None
opt_perf = None
n = 10
for i in range(n):
    t = float(i) / float(n)
    perf = func(t, mesh, polyline_points)
    if opt_perf is None or perf < opt_perf:
        opt_perf = perf
        opt_param = t
        opt_design = mesh.copy()
t1 = time.time()
print('computing time: ', t1 - t0)
print('opt parameter: ', opt_param, 'optimal performance: ', opt_perf)

# for vkey, attr in mesh.vertices(True):
#     attr['x'], attr['y'], attr['z'] = attr['x'], attr['z'], attr['y']

# t = [0.5]
# print(descent_numpy(t, func, iterations=100, gtol=10**(-1), bounds=[[0, 1]], args=(mesh, polyline_points)))

plotter = MeshPlotter(opt_design, figsize=(20, 20))
plotter.draw_vertices(radius=0.05)
plotter.draw_edges()
plotter.draw_faces()
plotter.show()
