
import rhinoscriptsyntax as rs
import compas_rhino as rhino

from compas_pattern.cad.rhino.utilities import surface_borders

from compas.datastructures.mesh import Mesh

from compas_pattern.cad.rhino.utilities import draw_mesh

from compas.geometry.algorithms.smoothing import mesh_smooth_centroid
from compas.geometry.algorithms.smoothing import mesh_smooth_area
from compas.geometry.algorithms.smoothing_cpp import smooth_centroid_cpp
from compas_pattern.algorithms.smoothing import define_constraints
from compas_pattern.algorithms.smoothing import apply_constraints

surface_guid = rs.GetObject('srf', filter = 8)
curve_features_guids = rs.GetObjects('crv features', filter = 4)
if curve_features_guids is None:
    curve_features_guids = []
point_features_guids = rs.GetObjects('pt features', filter = 1)
if point_features_guids is None:
    point_features_guids = []

lines = rs.GetObjects('lines', filter = 4)
edges = [[rs.CurveStartPoint(line), rs.CurveEndPoint(line)] for line in lines]
mesh = Mesh.from_lines(edges)

print mesh.number_of_vertices() - mesh.number_of_edges() + mesh.number_of_faces()
faces = list(mesh.faces())
for fkey in faces:
    if len(mesh.face_vertices(fkey)) > 10:
        mesh.delete_face(fkey)
print mesh.number_of_vertices() - mesh.number_of_edges() + mesh.number_of_faces()

smooth_mesh = mesh.copy()
smooth_mesh.cull_vertices()
constraints, surface_boundaries = define_constraints(smooth_mesh, surface_guid, curve_constraints = curve_features_guids, point_constraints = point_features_guids)
fixed_vertices = [vkey for vkey, constraint in constraints.items() if constraint[0] == 'point']
rs.EnableRedraw(True)
smoothing_iterations = rs.GetInteger('number of iterations for smoothing', number = 20)
damping_value = rs.GetReal('damping value for smoothing', number = .5)
rs.EnableRedraw(False)
mesh_smooth_area(smooth_mesh, fixed = fixed_vertices, kmax = smoothing_iterations, damping = damping_value, callback = apply_constraints, callback_args = [smooth_mesh, constraints])
rs.DeleteObjects(surface_boundaries)
smooth_mesh_guid = draw_mesh(smooth_mesh)